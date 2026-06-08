"""Compare MATLAB/nirs-toolbox and MNE-Python preprocessed HbO/HbR signals.

This script expects MATLAB-preprocessed CSV files exported by
``scripts/export_matlab_preprocessed_for_validation.m``. It compares those
signals against the MNE-Python FIF files in ``derivatives/preprocessed``.

The validation focuses on preprocessing only. It does not require statistical
results to match exactly.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import mne
import numpy as np
import pandas as pd

from load_data import load_config


def normalize_channel_name(name: str) -> str:
    return (
        name.replace(" ", "_")
        .replace("hbo", "hbo")
        .replace("hbr", "hbr")
        .replace("S", "S")
        .replace("D", "D")
    )


def matlab_name_from_mne(ch_name: str) -> str:
    return ch_name.replace(" ", "_")


def find_python_fif(preprocessed_dir: Path, group: str, subject: str) -> Path | None:
    candidate = preprocessed_dir / group / subject / f"{subject}_hbo_hbr_raw.fif"
    if candidate.exists():
        return candidate
    matches = sorted(preprocessed_dir.rglob(f"{subject}_hbo_hbr_raw.fif"))
    return matches[0] if matches else None


def compare_subject(
    matlab_csv: Path,
    python_fif: Path,
    subject: str,
    group: str,
) -> list[dict[str, Any]]:
    matlab_df = pd.read_csv(matlab_csv)
    raw = mne.io.read_raw_fif(python_fif, preload=True, verbose="error")

    if "time" not in matlab_df.columns:
        raise ValueError(f"MATLAB CSV has no time column: {matlab_csv}")

    matlab_time = matlab_df["time"].to_numpy(dtype=float)
    rows = []

    for ch_name in raw.ch_names:
        matlab_col = matlab_name_from_mne(ch_name)
        if matlab_col not in matlab_df.columns:
            matlab_col = normalize_channel_name(matlab_col)
        if matlab_col not in matlab_df.columns:
            rows.append(
                {
                    "subject": subject,
                    "group": group,
                    "ch_name": ch_name,
                    "status": "missing_matlab_channel",
                }
            )
            continue

        py_signal = raw.get_data(picks=[ch_name])[0]
        py_time = raw.times
        py_interp = np.interp(matlab_time, py_time, py_signal)
        matlab_signal = matlab_df[matlab_col].to_numpy(dtype=float)

        valid = np.isfinite(py_interp) & np.isfinite(matlab_signal)
        if valid.sum() < 3:
            rows.append(
                {
                    "subject": subject,
                    "group": group,
                    "ch_name": ch_name,
                    "status": "too_few_valid_points",
                }
            )
            continue

        py_valid = py_interp[valid]
        matlab_valid = matlab_signal[valid]
        diff = py_valid - matlab_valid
        corr = np.corrcoef(py_valid, matlab_valid)[0, 1]

        rows.append(
            {
                "subject": subject,
                "group": group,
                "ch_name": ch_name,
                "status": "ok",
                "n_points": int(valid.sum()),
                "correlation": float(corr),
                "mae": float(np.mean(np.abs(diff))),
                "rmse": float(np.sqrt(np.mean(diff**2))),
                "python_mean": float(np.mean(py_valid)),
                "matlab_mean": float(np.mean(matlab_valid)),
                "python_std": float(np.std(py_valid)),
                "matlab_std": float(np.std(matlab_valid)),
                "std_ratio_python_over_matlab": float(
                    np.std(py_valid) / np.std(matlab_valid)
                    if np.std(matlab_valid) != 0
                    else np.nan
                ),
            }
        )

    return rows


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    ok = results[results["status"] == "ok"].copy()
    if ok.empty:
        return pd.DataFrame(
            [
                {
                    "n_subjects": 0,
                    "n_channels": 0,
                    "median_correlation": np.nan,
                    "median_rmse": np.nan,
                    "median_mae": np.nan,
                }
            ]
        )

    return pd.DataFrame(
        [
            {
                "n_subjects": ok["subject"].nunique(),
                "n_channel_comparisons": len(ok),
                "median_correlation": ok["correlation"].median(),
                "min_correlation": ok["correlation"].min(),
                "median_rmse": ok["rmse"].median(),
                "median_mae": ok["mae"].median(),
                "median_std_ratio_python_over_matlab": ok[
                    "std_ratio_python_over_matlab"
                ].median(),
            }
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate MATLAB vs MNE preprocessing outputs.")
    parser.add_argument("--config", type=Path, default=Path("config/config_template.yaml"))
    parser.add_argument("--matlab-export-dir", type=Path, default=None)
    parser.add_argument("--python-preprocessed-dir", type=Path, default=None)
    parser.add_argument("--output-table", type=Path, default=None)
    parser.add_argument("--summary-table", type=Path, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    validation = config.get("analysis", {}).get("validation", {})

    matlab_export_dir = args.matlab_export_dir or Path(
        validation.get("matlab_export_dir", "validation/matlab_preprocessed")
    )
    python_preprocessed_dir = args.python_preprocessed_dir or Path(
        validation.get("python_preprocessed_dir", "derivatives/preprocessed")
    )
    output_table = args.output_table or Path(
        validation.get("output_table", "results/matlab_mne_preprocessing_validation.csv")
    )
    summary_table = args.summary_table or Path(
        validation.get("summary_table", "results/matlab_mne_preprocessing_validation_summary.csv")
    )

    manifest_path = matlab_export_dir / "manifest.csv"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"No MATLAB export manifest found at {manifest_path}. "
            "Run scripts/export_matlab_preprocessed_for_validation.m in MATLAB first."
        )

    manifest = pd.read_csv(manifest_path)
    rows = []
    for _, row in manifest.iterrows():
        subject = str(row["subject"])
        group = str(row["group"])
        matlab_csv = Path(row["csv_path"])
        python_fif = find_python_fif(python_preprocessed_dir, group, subject)
        if python_fif is None:
            rows.append(
                {
                    "subject": subject,
                    "group": group,
                    "status": "missing_python_fif",
                }
            )
            continue
        rows.extend(compare_subject(matlab_csv, python_fif, subject, group))

    results = pd.DataFrame(rows)
    summary = summarize(results)

    output_table.parent.mkdir(parents=True, exist_ok=True)
    summary_table.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_table, index=False)
    summary.to_csv(summary_table, index=False)

    print(summary.to_string(index=False))
    print(f"\nSaved validation table to {output_table}")
    print(f"Saved validation summary to {summary_table}")


if __name__ == "__main__":
    main()
