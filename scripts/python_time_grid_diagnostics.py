"""Export MNE-Python time-grid diagnostics by preprocessing stage.

This script mirrors the major stages of ``scripts/preprocess_fnirs.py`` but
exports only timing metadata. It helps diagnose whether MATLAB/MNE time-grid
differences originate at raw loading, resampling, Beer-Lambert conversion, or
task-window trimming.
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path
from typing import Any

import mne
import numpy as np
import pandas as pd
from mne.preprocessing.nirs import beer_lambert_law, optical_density

from load_data import (
    DEFAULT_CONDITION_MAP,
    find_snirf_files,
    infer_group,
    load_config,
    rename_annotations,
)
from preprocess_fnirs import trim_to_task_window


def time_grid_row(raw: mne.io.BaseRaw, subject: str, group: str, stage: str) -> dict[str, Any]:
    times = raw.times
    dt = np.diff(times)
    return {
        "subject": subject,
        "group": group,
        "stage": stage,
        "n_times": int(len(times)),
        "t0": float(times[0]) if len(times) else np.nan,
        "t_end": float(times[-1]) if len(times) else np.nan,
        "median_dt": float(np.median(dt)) if len(dt) else np.nan,
        "min_dt": float(np.min(dt)) if len(dt) else np.nan,
        "max_dt": float(np.max(dt)) if len(dt) else np.nan,
        "sfreq": float(raw.info["sfreq"]),
        "first_samp": int(raw.first_samp),
        "first_time": float(raw.first_time),
    }


def stage_rows(
    snirf_path: Path,
    group: str,
    condition_map: dict[str, str],
    preprocessing: dict[str, Any],
) -> list[dict[str, Any]]:
    subject = snirf_path.parent.name
    rows: list[dict[str, Any]] = []

    raw = mne.io.read_raw_snirf(snirf_path, preload=True, verbose="error")
    rows.append(time_grid_row(raw, subject, group, "raw_loaded"))

    rename_annotations(raw, condition_map)
    rows.append(time_grid_row(raw, subject, group, "stim_renamed"))

    descriptions = list(raw.annotations.description)
    expected_ok = descriptions.count("MA") == 16 and descriptions.count("Control") == 16
    if not expected_ok:
        rows.append({**time_grid_row(raw, subject, group, "event_filtered"), "excluded": True})
        return rows

    rows.append({**time_grid_row(raw, subject, group, "event_filtered"), "excluded": False})
    rows.append(time_grid_row(raw, subject, group, "short_separation_labeled"))

    raw_resampled = raw.copy().resample(
        float(preprocessing.get("resample_hz", 2)),
        verbose="error",
    )
    rows.append(time_grid_row(raw_resampled, subject, group, "resampled_2hz"))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        raw_od = optical_density(raw_resampled)
    rows.append(time_grid_row(raw_od, subject, group, "optical_density"))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        raw_hb = beer_lambert_law(raw_od, ppf=float(preprocessing.get("ppf", 6.0)))
    rows.append(time_grid_row(raw_hb, subject, group, "beer_lambert"))

    baseline = preprocessing.get("trim_baseline_sec", {})
    raw_trimmed = trim_to_task_window(
        raw_hb.copy(),
        pre_baseline=float(baseline.get("pre", 5)),
        post_baseline=float(baseline.get("post", 5)),
    )
    rows.append(time_grid_row(raw_trimmed, subject, group, "trimmed"))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Export MNE-Python time-grid diagnostics.")
    parser.add_argument("--config", type=Path, default=Path("config/config_template.yaml"))
    parser.add_argument("--root-dir", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=Path("results/python_time_grid_by_stage.csv"))
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    data_config = config.get("data", {})
    event_config = config.get("events", {})
    preprocessing = config.get("preprocessing", {})

    root_dir = args.root_dir or Path(data_config.get("root_dir", "data"))
    group_dirs = data_config.get("group_dirs", {})
    pattern = data_config.get("snirf_pattern", "*.snirf")
    condition_map = event_config.get("condition_map", DEFAULT_CONDITION_MAP)

    snirf_files = find_snirf_files(root_dir, pattern)
    if args.limit is not None:
        snirf_files = snirf_files[: args.limit]
    if not snirf_files:
        raise FileNotFoundError(f"No SNIRF files found under {root_dir}")

    rows: list[dict[str, Any]] = []
    for snirf_path in snirf_files:
        group = infer_group(snirf_path, group_dirs)
        try:
            rows.extend(stage_rows(snirf_path, group, condition_map, preprocessing))
        except Exception as exc:
            rows.append(
                {
                    "subject": snirf_path.parent.name,
                    "group": group,
                    "stage": "error",
                    "error": str(exc),
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output, index=False)
    print(f"Saved Python time-grid diagnostics to {args.output}")


if __name__ == "__main__":
    main()
