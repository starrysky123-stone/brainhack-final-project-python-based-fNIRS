"""Preprocess SNIRF fNIRS data with MNE-Python.

This script mirrors the preprocessing section of the original MATLAB pipeline:

1. Load SNIRF raw intensity data.
2. Rename stimulus annotations to MA, PA, and Control.
3. Resample to 2 Hz.
4. Convert intensity to optical density.
5. Apply the modified Beer-Lambert law to obtain HbO/HbR.
6. Trim to the task window with a small pre/post baseline.

Processed FIF files are written to ``derivatives/``, which is ignored by Git.
"""

from __future__ import annotations

import argparse
import os
import warnings
from pathlib import Path
from typing import Any

import mne
import pandas as pd
from mne.preprocessing.nirs import (
    beer_lambert_law,
    optical_density,
    source_detector_distances,
)

from load_data import (
    DEFAULT_CONDITION_MAP,
    find_snirf_files,
    infer_group,
    load_config,
    rename_annotations,
)


def trim_to_task_window(
    raw: mne.io.BaseRaw,
    pre_baseline: float,
    post_baseline: float,
) -> mne.io.BaseRaw:
    if len(raw.annotations) == 0:
        return raw

    onset = raw.annotations.onset
    duration = raw.annotations.duration
    tmin = max(0.0, float(onset.min() - pre_baseline))
    tmax = min(float(raw.times[-1]), float((onset + duration).max() + post_baseline))
    return raw.crop(tmin=tmin, tmax=tmax)


def make_output_path(snirf_path: Path, output_root: Path, group: str) -> Path:
    subject = snirf_path.parent.name
    return output_root / group / subject / f"{subject}_hbo_hbr_raw.fif"


def preprocess_one(
    snirf_path: Path,
    group: str,
    output_root: Path,
    condition_map: dict[str, str],
    preprocessing: dict[str, Any],
    overwrite: bool,
) -> dict[str, Any]:
    output_path = make_output_path(snirf_path, output_root, group)
    if output_path.exists() and not overwrite:
        return {
            "subject_folder": snirf_path.parent.name,
            "group": group,
            "snirf_file": snirf_path.name,
            "output_file": str(output_path),
            "status": "skipped_exists",
        }

    raw = mne.io.read_raw_snirf(snirf_path, preload=True, verbose="error")
    rename_annotations(raw, condition_map)

    raw.resample(float(preprocessing.get("resample_hz", 2)), verbose="error")
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        raw_od = optical_density(raw)
        raw_hb = beer_lambert_law(raw_od, ppf=float(preprocessing.get("ppf", 6.0)))

    baseline = preprocessing.get("trim_baseline_sec", {})
    raw_hb = trim_to_task_window(
        raw_hb,
        pre_baseline=float(baseline.get("pre", 5)),
        post_baseline=float(baseline.get("post", 5)),
    )

    distances = source_detector_distances(raw_hb.info)
    short_threshold = float(preprocessing.get("short_channel_threshold_m", 0.01))
    descriptions = list(raw_hb.annotations.description)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    raw_hb.save(output_path, overwrite=True, verbose="error")

    row: dict[str, Any] = {
        "subject_folder": snirf_path.parent.name,
        "group": group,
        "snirf_file": snirf_path.name,
        "output_file": str(output_path),
        "status": "ok",
        "n_channels": len(raw_hb.ch_names),
        "sfreq": raw_hb.info["sfreq"],
        "duration_sec": raw_hb.times[-1] if len(raw_hb.times) else 0,
        "n_annotations": len(raw_hb.annotations),
        "n_short_channels": int((distances < short_threshold).sum()),
        "n_warnings": len(caught_warnings),
        "warning_messages": " | ".join(sorted({str(w.message) for w in caught_warnings})),
    }
    for cond in sorted(set(condition_map.values())):
        row[f"n_{cond}"] = descriptions.count(cond)
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess local SNIRF fNIRS files.")
    parser.add_argument("--config", type=Path, default=Path("config/config_template.yaml"))
    parser.add_argument("--root-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--summary", type=Path, default=Path("results/preprocessing_summary.csv"))
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    # Keep Matplotlib cache inside the writable workspace/temp area when MNE imports plotting.
    os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/mplconfig")

    config = load_config(args.config)
    data_config = config.get("data", {})
    event_config = config.get("events", {})
    preprocessing = config.get("preprocessing", {})

    root_dir = args.root_dir or Path(data_config.get("root_dir", "data"))
    output_root = args.output_dir or Path(data_config.get("derivatives_dir", "derivatives/preprocessed"))
    group_dirs = data_config.get("group_dirs", {})
    pattern = data_config.get("snirf_pattern", "*.snirf")
    condition_map = event_config.get("condition_map", DEFAULT_CONDITION_MAP)

    snirf_files = find_snirf_files(root_dir, pattern)
    if args.limit is not None:
        snirf_files = snirf_files[: args.limit]
    if not snirf_files:
        raise FileNotFoundError(f"No SNIRF files found under {root_dir}")

    rows = []
    for snirf_path in snirf_files:
        group = infer_group(snirf_path, group_dirs)
        try:
            rows.append(
                preprocess_one(
                    snirf_path=snirf_path,
                    group=group,
                    output_root=output_root,
                    condition_map=condition_map,
                    preprocessing=preprocessing,
                    overwrite=args.overwrite,
                )
            )
        except Exception as exc:
            rows.append(
                {
                    "subject_folder": snirf_path.parent.name,
                    "group": group,
                    "snirf_file": snirf_path.name,
                    "status": "error",
                    "error": str(exc),
                }
            )

    args.summary.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(args.summary, index=False)
    print(df.to_string(index=False))
    print(f"\nSaved preprocessing summary to {args.summary}")


if __name__ == "__main__":
    main()
