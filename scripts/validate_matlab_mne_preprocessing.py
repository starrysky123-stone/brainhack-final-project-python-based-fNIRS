"""Compare MATLAB/nirs-toolbox and MNE-Python preprocessed HbO/HbR signals.

This script expects MATLAB-preprocessed CSV files exported by
``scripts/export_matlab_preprocessed_for_validation.m``. It compares those
signals against the MNE-Python FIF files in ``derivatives/preprocessed``.

The validation focuses on preprocessing only. It does not require statistical
results to match exactly.

The primary comparison is sample-index aligned and unit-aware. Interpolated
metrics are reported only as secondary diagnostics because interpolation can
hide temporal misalignment between MATLAB and Python outputs.
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


def compare_time_grid(
    matlab_time: np.ndarray,
    py_time: np.ndarray,
    subject: str,
    group: str,
    time_atol: float,
) -> dict[str, Any]:
    n_common = min(len(matlab_time), len(py_time))
    matlab_dt = np.diff(matlab_time)
    py_dt = np.diff(py_time)
    matlab_median_dt = float(np.median(matlab_dt)) if len(matlab_dt) else np.nan
    py_median_dt = float(np.median(py_dt)) if len(py_dt) else np.nan
    if np.isfinite(matlab_median_dt) and matlab_median_dt != 0:
        dt_ratio_python_over_matlab = py_median_dt / matlab_median_dt
    else:
        dt_ratio_python_over_matlab = np.nan

    matlab_seconds_error = abs(matlab_median_dt - py_median_dt)
    matlab_milliseconds_error = abs((matlab_median_dt * 0.001) - py_median_dt)
    if np.isfinite(matlab_seconds_error) and matlab_seconds_error <= time_atol:
        matlab_time_unit_guess = "seconds"
    elif np.isfinite(matlab_milliseconds_error) and matlab_milliseconds_error <= time_atol:
        matlab_time_unit_guess = "milliseconds"
    else:
        matlab_time_unit_guess = "unknown"

    if n_common:
        time_diff = py_time[:n_common] - matlab_time[:n_common]
        max_abs_time_diff = float(np.max(np.abs(time_diff)))
        mean_abs_time_diff = float(np.mean(np.abs(time_diff)))
        time_allclose = bool(
            np.allclose(py_time[:n_common], matlab_time[:n_common], rtol=0, atol=time_atol)
        )
        py_relative_time = py_time[:n_common] - py_time[0]
        matlab_relative_time = matlab_time[:n_common] - matlab_time[0]
        relative_time_diff = py_relative_time - matlab_relative_time
        max_abs_relative_time_diff = float(np.max(np.abs(relative_time_diff)))
        mean_abs_relative_time_diff = float(np.mean(np.abs(relative_time_diff)))
        relative_time_allclose = bool(
            np.allclose(
                py_relative_time,
                matlab_relative_time,
                rtol=0,
                atol=time_atol,
            )
        )
    else:
        max_abs_time_diff = np.nan
        mean_abs_time_diff = np.nan
        time_allclose = False
        max_abs_relative_time_diff = np.nan
        mean_abs_relative_time_diff = np.nan
        relative_time_allclose = False

    length_diff_python_minus_matlab = int(len(py_time) - len(matlab_time))
    abs_length_diff = abs(length_diff_python_minus_matlab)
    return {
        "subject": subject,
        "group": group,
        "matlab_n_times": int(len(matlab_time)),
        "python_n_times": int(len(py_time)),
        "length_diff_python_minus_matlab": length_diff_python_minus_matlab,
        "abs_length_diff": abs_length_diff,
        "length_diff_gt_1": bool(abs_length_diff > 1),
        "same_n_times": bool(len(matlab_time) == len(py_time)),
        "n_common_times": int(n_common),
        "matlab_t0": float(matlab_time[0]) if len(matlab_time) else np.nan,
        "python_t0": float(py_time[0]) if len(py_time) else np.nan,
        "time_zero_offset_python_minus_matlab": float(py_time[0] - matlab_time[0])
        if len(matlab_time) and len(py_time)
        else np.nan,
        "matlab_t_end": float(matlab_time[-1]) if len(matlab_time) else np.nan,
        "python_t_end": float(py_time[-1]) if len(py_time) else np.nan,
        "matlab_median_dt": matlab_median_dt,
        "python_median_dt": py_median_dt,
        "dt_ratio_python_over_matlab": float(dt_ratio_python_over_matlab),
        "matlab_time_unit_guess": matlab_time_unit_guess,
        "time_allclose": time_allclose,
        "relative_time_allclose": relative_time_allclose,
        "max_abs_time_diff_common": max_abs_time_diff,
        "mean_abs_time_diff_common": mean_abs_time_diff,
        "max_abs_relative_time_diff_common": max_abs_relative_time_diff,
        "mean_abs_relative_time_diff_common": mean_abs_relative_time_diff,
    }


def finite_metrics(
    py_signal: np.ndarray,
    matlab_signal: np.ndarray,
    rtol: float,
    atol: float,
) -> dict[str, Any] | None:
    valid = np.isfinite(py_signal) & np.isfinite(matlab_signal)
    if valid.sum() < 3:
        return None

    py_valid = py_signal[valid]
    matlab_valid = matlab_signal[valid]
    diff = py_valid - matlab_valid
    corr = np.corrcoef(py_valid, matlab_valid)[0, 1]

    return {
        "n_points": int(valid.sum()),
        "array_equal": bool(np.array_equal(py_valid, matlab_valid)),
        "allclose": bool(np.allclose(py_valid, matlab_valid, rtol=rtol, atol=atol)),
        "max_abs_diff": float(np.max(np.abs(diff))),
        "mae": float(np.mean(np.abs(diff))),
        "rmse": float(np.sqrt(np.mean(diff**2))),
        "correlation": float(corr),
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


def compare_subject(
    matlab_csv: Path,
    python_fif: Path,
    subject: str,
    group: str,
    python_unit_scale: float,
    rtol: float,
    atol: float,
    time_atol: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    matlab_df = pd.read_csv(matlab_csv)
    raw = mne.io.read_raw_fif(python_fif, preload=True, verbose="error")

    if "time" not in matlab_df.columns:
        raise ValueError(f"MATLAB CSV has no time column: {matlab_csv}")

    matlab_time = matlab_df["time"].to_numpy(dtype=float)
    py_time = raw.times
    time_row = compare_time_grid(matlab_time, py_time, subject, group, time_atol)
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

        py_signal = raw.get_data(picks=[ch_name])[0] * python_unit_scale
        matlab_signal = matlab_df[matlab_col].to_numpy(dtype=float)
        n_common = min(len(py_signal), len(matlab_signal))
        metrics = finite_metrics(
            py_signal[:n_common],
            matlab_signal[:n_common],
            rtol=rtol,
            atol=atol,
        )

        if metrics is None:
            rows.append(
                {
                    "subject": subject,
                    "group": group,
                    "ch_name": ch_name,
                    "status": "too_few_valid_points",
                }
            )
            continue

        py_interp = np.interp(matlab_time, py_time, py_signal)
        interp_metrics = finite_metrics(
            py_interp,
            matlab_signal,
            rtol=rtol,
            atol=atol,
        )

        finite_for_fit = np.isfinite(py_signal[:n_common]) & np.isfinite(
            matlab_signal[:n_common]
        )
        if finite_for_fit.sum() >= 3:
            fit_scale, fit_offset = np.polyfit(
                py_signal[:n_common][finite_for_fit],
                matlab_signal[:n_common][finite_for_fit],
                1,
            )
        else:
            fit_scale, fit_offset = np.nan, np.nan

        rows.append(
            {
                "subject": subject,
                "group": group,
                "ch_name": ch_name,
                "status": "ok_index_aligned",
                "python_unit_scale": python_unit_scale,
                "rtol": rtol,
                "atol": atol,
                "time_allclose": time_row["time_allclose"],
                "same_n_times": time_row["same_n_times"],
                "max_abs_time_diff_common": time_row["max_abs_time_diff_common"],
                **metrics,
                "interpolated_correlation": (
                    interp_metrics["correlation"] if interp_metrics else np.nan
                ),
                "interpolated_mae": interp_metrics["mae"] if interp_metrics else np.nan,
                "interpolated_rmse": interp_metrics["rmse"] if interp_metrics else np.nan,
                "exploratory_fitted_scale_matlab_per_python": float(fit_scale),
                "exploratory_fitted_offset_matlab_units": float(fit_offset),
            }
        )

    return rows, time_row


def summarize(
    results: pd.DataFrame,
    time_results: pd.DataFrame,
    manifest_n_rows: int,
    manifest_n_duplicate_subject_rows: int,
) -> pd.DataFrame:
    ok = results[results["status"] == "ok_index_aligned"].copy()
    if ok.empty:
        return pd.DataFrame(
            [
                {
                    "manifest_n_rows": manifest_n_rows,
                    "manifest_n_duplicate_subject_rows": manifest_n_duplicate_subject_rows,
                    "n_subjects": 0,
                    "n_channels": 0,
                    "median_correlation": np.nan,
                    "median_rmse": np.nan,
                    "median_mae": np.nan,
                    "n_subjects_same_n_times": 0,
                    "n_subjects_time_allclose": 0,
                }
            ]
        )

    return pd.DataFrame(
        [
            {
                "manifest_n_rows": manifest_n_rows,
                "manifest_n_duplicate_subject_rows": manifest_n_duplicate_subject_rows,
                "n_subjects": ok["subject"].nunique(),
                "n_channel_comparisons": len(ok),
                "n_subjects_same_n_times": int(time_results["same_n_times"].sum()),
                "n_subjects_length_diff_le_1": int(
                    (time_results["abs_length_diff"] <= 1).sum()
                ),
                "n_subjects_time_allclose": int(time_results["time_allclose"].sum()),
                "n_subjects_relative_time_allclose": int(
                    time_results["relative_time_allclose"].sum()
                ),
                "n_subjects_matlab_time_guess_seconds": int(
                    (time_results["matlab_time_unit_guess"] == "seconds").sum()
                ),
                "n_subjects_matlab_time_guess_milliseconds": int(
                    (time_results["matlab_time_unit_guess"] == "milliseconds").sum()
                ),
                "median_max_abs_time_diff_common": time_results[
                    "max_abs_time_diff_common"
                ].median(),
                "max_abs_time_diff_common": time_results[
                    "max_abs_time_diff_common"
                ].max(),
                "median_max_abs_relative_time_diff_common": time_results[
                    "max_abs_relative_time_diff_common"
                ].median(),
                "max_abs_relative_time_diff_common": time_results[
                    "max_abs_relative_time_diff_common"
                ].max(),
                "n_array_equal": int(ok["array_equal"].sum()),
                "n_allclose": int(ok["allclose"].sum()),
                "median_correlation": ok["correlation"].median(),
                "min_correlation": ok["correlation"].min(),
                "median_max_abs_diff": ok["max_abs_diff"].median(),
                "median_rmse": ok["rmse"].median(),
                "median_mae": ok["mae"].median(),
                "median_std_ratio_python_over_matlab": ok[
                    "std_ratio_python_over_matlab"
                ].median(),
                "median_interpolated_correlation": ok[
                    "interpolated_correlation"
                ].median(),
                "median_exploratory_fitted_scale_matlab_per_python": ok[
                    "exploratory_fitted_scale_matlab_per_python"
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
    parser.add_argument("--time-table", type=Path, default=None)
    parser.add_argument("--python-unit-scale", type=float, default=1.0)
    parser.add_argument("--rtol", type=float, default=1e-5)
    parser.add_argument("--atol", type=float, default=1e-8)
    parser.add_argument("--time-atol", type=float, default=1e-9)
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
    time_table = args.time_table or Path(
        validation.get("time_table", "results/matlab_mne_preprocessing_time_alignment.csv")
    )

    manifest_path = matlab_export_dir / "manifest.csv"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"No MATLAB export manifest found at {manifest_path}. "
            "Run scripts/export_matlab_preprocessed_for_validation.m in MATLAB first."
        )

    manifest = pd.read_csv(manifest_path)
    manifest_n_rows = len(manifest)
    duplicate_mask = manifest.duplicated(["group", "subject"], keep="first")
    manifest_n_duplicate_subject_rows = int(duplicate_mask.sum())
    if manifest_n_duplicate_subject_rows:
        duplicate_labels = manifest.loc[duplicate_mask, ["group", "subject"]].to_dict("records")
        print(
            "Dropping duplicate MATLAB manifest rows for group/subject pairs: "
            f"{duplicate_labels}"
        )
        manifest = manifest.drop_duplicates(["group", "subject"], keep="first").copy()

    rows = []
    time_rows = []
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
        subject_rows, time_row = compare_subject(
            matlab_csv,
            python_fif,
            subject,
            group,
            python_unit_scale=args.python_unit_scale,
            rtol=args.rtol,
            atol=args.atol,
            time_atol=args.time_atol,
        )
        rows.extend(subject_rows)
        time_rows.append(time_row)

    results = pd.DataFrame(rows)
    time_results = pd.DataFrame(time_rows)
    summary = summarize(
        results,
        time_results,
        manifest_n_rows=manifest_n_rows,
        manifest_n_duplicate_subject_rows=manifest_n_duplicate_subject_rows,
    )

    output_table.parent.mkdir(parents=True, exist_ok=True)
    summary_table.parent.mkdir(parents=True, exist_ok=True)
    time_table.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_table, index=False)
    time_results.to_csv(time_table, index=False)
    summary.to_csv(summary_table, index=False)

    print(summary.to_string(index=False))
    print(f"\nSaved validation table to {output_table}")
    print(f"Saved time-alignment table to {time_table}")
    print(f"Saved validation summary to {summary_table}")


if __name__ == "__main__":
    main()
