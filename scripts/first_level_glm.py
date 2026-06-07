"""Run subject-level GLM on preprocessed HbO/HbR fNIRS data.

This script uses MNE-NIRS to estimate a first-level GLM for each participant.
It exports two local tables:

- condition-wise beta estimates for each channel and chromophore
- the primary ``MA-Control`` contrast for each channel and chromophore

The output tables are ignored by Git because they contain per-subject results
derived from private participant data.
"""

from __future__ import annotations

import argparse
import os
import warnings
from pathlib import Path
from typing import Any

import mne
import numpy as np
import pandas as pd
from mne_nirs.channels import get_short_channels
from mne_nirs.experimental_design import make_first_level_design_matrix
from mne_nirs.statistics import run_glm

from load_data import load_config


def find_preprocessed_files(input_dir: Path) -> list[Path]:
    return sorted(input_dir.rglob("*_hbo_hbr_raw.fif"))


def infer_group_from_derivative(path: Path, input_dir: Path) -> str:
    relative = path.relative_to(input_dir)
    return relative.parts[0] if len(relative.parts) >= 3 else "unknown"


def infer_subject_from_derivative(path: Path) -> str:
    return path.parent.name


def make_contrast_vector(design_columns: list[str], contrast_name: str) -> list[float]:
    contrast = [0.0] * len(design_columns)
    if contrast_name != "MA-Control":
        raise ValueError(f"Unsupported contrast: {contrast_name}")
    contrast[design_columns.index("MA")] = 1.0
    contrast[design_columns.index("Control")] = -1.0
    return contrast


def make_short_channel_regressors(
    raw: mne.io.BaseRaw,
    glm_config: dict[str, Any],
) -> tuple[np.ndarray | None, list[str], int]:
    if not glm_config.get("add_short_channel_regressors", False):
        return None, [], 0

    short = get_short_channels(
        raw,
        max_dist=float(glm_config.get("short_channel_max_dist_m", 0.01)),
    )
    if len(short.ch_names) == 0:
        return None, [], 0

    add_regs = short.get_data().T
    add_regs = add_regs - add_regs.mean(axis=0, keepdims=True)
    std = add_regs.std(axis=0, keepdims=True)
    add_regs = add_regs / np.where(std == 0, 1, std)
    names = [f"short_{name.replace(' ', '_')}" for name in short.ch_names]
    return add_regs, names, len(short.ch_names)


def run_subject_glm(
    fif_path: Path,
    input_dir: Path,
    glm_config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    group = infer_group_from_derivative(fif_path, input_dir)
    subject = infer_subject_from_derivative(fif_path)

    raw = mne.io.read_raw_fif(fif_path, preload=True, verbose="error")

    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        add_regs, add_reg_names, n_short_regressors = make_short_channel_regressors(
            raw,
            glm_config,
        )
        design_matrix = make_first_level_design_matrix(
            raw,
            stim_dur=float(glm_config.get("stim_duration_sec", 10)),
            hrf_model=glm_config.get("hrf_model", "glover"),
            drift_model=glm_config.get("drift_model", "cosine"),
            high_pass=float(glm_config.get("high_pass", 0.008)),
            add_regs=add_regs,
            add_reg_names=add_reg_names,
        )
        glm_estimate = run_glm(
            raw,
            design_matrix,
            noise_model=glm_config.get("noise_model", "ar1"),
            verbose=0,
        )

    betas = glm_estimate.to_dataframe()
    betas.insert(0, "subject", subject)
    betas.insert(1, "group", group)

    contrast_name = glm_config.get("primary_contrast_name", "MA-Control")
    contrast_vector = make_contrast_vector(list(design_matrix.columns), contrast_name)
    contrast = glm_estimate.compute_contrast(contrast_vector).to_dataframe()
    contrast.insert(0, "subject", subject)
    contrast.insert(1, "group", group)
    contrast.insert(2, "contrast", contrast_name)

    summary = {
        "subject": subject,
        "group": group,
        "input_file": str(fif_path),
        "status": "ok",
        "n_channels": len(raw.ch_names),
        "sfreq": raw.info["sfreq"],
        "n_annotations": len(raw.annotations),
        "n_design_columns": len(design_matrix.columns),
        "design_columns": "|".join(design_matrix.columns),
        "n_short_regressors": n_short_regressors,
        "n_beta_rows": len(betas),
        "n_contrast_rows": len(contrast),
        "n_warnings": len(caught_warnings),
        "warning_messages": " | ".join(sorted({str(w.message) for w in caught_warnings})),
    }
    return betas, contrast, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run first-level MNE-NIRS GLM.")
    parser.add_argument("--config", type=Path, default=Path("config/config_template.yaml"))
    parser.add_argument("--input-dir", type=Path, default=None)
    parser.add_argument("--beta-table", type=Path, default=None)
    parser.add_argument("--contrast-table", type=Path, default=None)
    parser.add_argument("--summary-table", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/mplconfig")

    config = load_config(args.config)
    glm_config = config.get("analysis", {}).get("glm", {})

    input_dir = args.input_dir or Path(glm_config.get("input_dir", "derivatives/preprocessed"))
    beta_table = args.beta_table or Path(glm_config.get("beta_table", "results/first_level_betas_ssreg.csv"))
    contrast_table = args.contrast_table or Path(
        glm_config.get("contrast_table", "results/first_level_contrasts_ssreg.csv")
    )
    summary_table = args.summary_table or Path(
        glm_config.get("summary_table", "results/first_level_glm_summary_ssreg.csv")
    )

    fif_files = find_preprocessed_files(input_dir)
    if args.limit is not None:
        fif_files = fif_files[: args.limit]
    if not fif_files:
        raise FileNotFoundError(f"No preprocessed FIF files found under {input_dir}")

    beta_tables = []
    contrast_tables = []
    summaries = []
    for fif_path in fif_files:
        try:
            betas, contrast, summary = run_subject_glm(fif_path, input_dir, glm_config)
            beta_tables.append(betas)
            contrast_tables.append(contrast)
            summaries.append(summary)
        except Exception as exc:
            summaries.append(
                {
                    "subject": infer_subject_from_derivative(fif_path),
                    "group": infer_group_from_derivative(fif_path, input_dir),
                    "input_file": str(fif_path),
                    "status": "error",
                    "error": str(exc),
                }
            )

    summary_table.parent.mkdir(parents=True, exist_ok=True)
    beta_table.parent.mkdir(parents=True, exist_ok=True)
    contrast_table.parent.mkdir(parents=True, exist_ok=True)

    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(summary_table, index=False)

    if beta_tables:
        pd.concat(beta_tables, ignore_index=True).to_csv(beta_table, index=False)
    if contrast_tables:
        pd.concat(contrast_tables, ignore_index=True).to_csv(contrast_table, index=False)

    print(summary_df.to_string(index=False))
    print(f"\nSaved first-level GLM summary to {summary_table}")
    print(f"Saved beta table to {beta_table}")
    print(f"Saved contrast table to {contrast_table}")


if __name__ == "__main__":
    main()
