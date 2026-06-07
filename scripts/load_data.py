"""Load and sanity-check SNIRF fNIRS files with MNE-Python.

This script is the first step of the Python-based fNIRS pipeline. It reads
local SNIRF files, renames stimulus markers using the condition mapping from
the original MATLAB pipeline, and writes a non-sensitive summary table.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import mne
import pandas as pd
import yaml


DEFAULT_CONDITION_MAP = {
    "1": "MA",
    "2": "PA",
    "3": "Control",
}

DEFAULT_EXPECTED_COUNTS = {
    "MA": 16,
    "Control": 16,
}


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def find_snirf_files(root_dir: Path, pattern: str = "*.snirf") -> list[Path]:
    return sorted(root_dir.rglob(pattern))


def infer_group(path: Path, group_dirs: dict[str, str]) -> str:
    parts = set(path.parts)
    for group, dirname in group_dirs.items():
        if dirname in parts:
            return group
    return "unknown"


def rename_annotations(raw: mne.io.BaseRaw, condition_map: dict[str, str]) -> None:
    if len(raw.annotations) == 0:
        return
    raw.annotations.rename(condition_map)


def summarize_raw(
    snirf_path: Path,
    group: str,
    condition_map: dict[str, str],
    expected_counts: dict[str, int],
) -> dict[str, Any]:
    raw = mne.io.read_raw_snirf(snirf_path, preload=False, verbose="error")
    rename_annotations(raw, condition_map)

    descriptions = list(raw.annotations.description)
    counts = {cond: descriptions.count(cond) for cond in sorted(set(condition_map.values()))}
    expected_ok = all(counts.get(cond, 0) == expected for cond, expected in expected_counts.items())

    summary: dict[str, Any] = {
        "subject_folder": snirf_path.parent.name,
        "group": group,
        "snirf_file": snirf_path.name,
        "n_channels": len(raw.ch_names),
        "sfreq": raw.info["sfreq"],
        "duration_sec": raw.times[-1] if len(raw.times) else 0,
        "n_annotations": len(raw.annotations),
        "expected_events_ok": expected_ok,
    }
    for cond, count in counts.items():
        summary[f"n_{cond}"] = count
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Load and summarize local SNIRF fNIRS files.")
    parser.add_argument("--config", type=Path, default=Path("config/config_template.yaml"))
    parser.add_argument("--root-dir", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=Path("results/snirf_file_summary.csv"))
    args = parser.parse_args()

    config = load_config(args.config)
    data_config = config.get("data", {})
    event_config = config.get("events", {})

    root_dir = args.root_dir or Path(data_config.get("root_dir", "data"))
    group_dirs = data_config.get("group_dirs", {})
    pattern = data_config.get("snirf_pattern", "*.snirf")
    condition_map = event_config.get("condition_map", DEFAULT_CONDITION_MAP)
    expected_counts = event_config.get("expected_counts", DEFAULT_EXPECTED_COUNTS)

    snirf_files = find_snirf_files(root_dir, pattern)
    if not snirf_files:
        raise FileNotFoundError(f"No SNIRF files found under {root_dir}")

    rows = [
        summarize_raw(
            snirf_path=path,
            group=infer_group(path, group_dirs),
            condition_map=condition_map,
            expected_counts=expected_counts,
        )
        for path in snirf_files
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(args.output, index=False)
    print(df.to_string(index=False))
    print(f"\nSaved summary to {args.output}")


if __name__ == "__main__":
    main()
