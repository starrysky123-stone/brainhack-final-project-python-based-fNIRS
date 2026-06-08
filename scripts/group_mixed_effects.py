"""Run MATLAB-like mixed-effects group analysis for MA fNIRS contrasts.

This script is a closer Python analogue to the MATLAB/nirs-toolbox group model:

    beta ~ -1 + Group:cond + (1|Subject)

It fits a separate random-intercept mixed model for each channel/chromophore
using first-level condition betas, then evaluates the MA-Control contrasts.
The output tables are local derived results and are ignored by Git.
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path
from typing import Any

import mne
import numpy as np
import pandas as pd
import statsmodels.api as sm
from mne_nirs.channels import get_long_channels
from scipy import stats
from statsmodels.stats.multitest import fdrcorrection

from load_data import load_config


CONDITIONS = ("Control", "MA", "PA")
GROUPS = ("G1_3", "G4_6")
MODEL_COLUMNS = (
    "G4_6:Control",
    "G1_3:Control",
    "G4_6:MA",
    "G1_3:MA",
    "G4_6:PA",
    "G1_3:PA",
)
CONTRASTS = {
    "G4_6 MA - Control": {
        "G4_6:MA": 1.0,
        "G4_6:Control": -1.0,
    },
    "G1_3 MA - Control": {
        "G1_3:MA": 1.0,
        "G1_3:Control": -1.0,
    },
    "G4_6 MA effect - G1_3 MA effect": {
        "G4_6:MA": 1.0,
        "G4_6:Control": -1.0,
        "G1_3:MA": -1.0,
        "G1_3:Control": 1.0,
    },
}


def get_long_hbo_channel_names(input_dir: Path) -> set[str]:
    fif_files = sorted(input_dir.rglob("*_hbo_hbr_raw.fif"))
    if not fif_files:
        raise FileNotFoundError(f"No preprocessed FIF files found under {input_dir}")

    raw = mne.io.read_raw_fif(fif_files[0], preload=False, verbose="error")
    long_hbo = get_long_channels(raw.copy().pick("hbo"))
    return set(long_hbo.ch_names)


def filter_beta_table(beta_df: pd.DataFrame, group_config: dict[str, Any]) -> pd.DataFrame:
    beta_df = beta_df[beta_df["Condition"].isin(CONDITIONS)].copy()

    if group_config.get("long_hbo_only", False):
        input_dir = Path(group_config.get("preprocessed_input_dir", "derivatives/preprocessed"))
        long_hbo_names = get_long_hbo_channel_names(input_dir)
        beta_df = beta_df[
            (beta_df["Chroma"] == "hbo") & (beta_df["ch_name"].isin(long_hbo_names))
        ].copy()

    beta_df = beta_df[beta_df["group"].isin(GROUPS)].copy()
    beta_df["model_cell"] = beta_df["group"] + ":" + beta_df["Condition"]
    return beta_df


def make_design(channel_df: pd.DataFrame) -> pd.DataFrame:
    design = pd.DataFrame(0.0, index=channel_df.index, columns=MODEL_COLUMNS)
    for col in MODEL_COLUMNS:
        design.loc[channel_df["model_cell"] == col, col] = 1.0
    return design


def make_contrast_vector(contrast: dict[str, float], columns: list[str]) -> np.ndarray:
    vector = np.zeros(len(columns), dtype=float)
    for name, weight in contrast.items():
        vector[columns.index(name)] = weight
    return vector


def fit_channel_model(channel_df: pd.DataFrame) -> tuple[Any | None, dict[str, Any]]:
    channel_df = channel_df.dropna(subset=["theta"]).copy()
    design = make_design(channel_df)

    present_cells = set(channel_df["model_cell"])
    missing_cells = [cell for cell in MODEL_COLUMNS if cell not in present_cells]
    if missing_cells:
        return None, {
            "model_status": "missing_model_cells",
            "model_message": "|".join(missing_cells),
        }

    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model = sm.MixedLM(
                endog=channel_df["theta"].astype(float),
                exog=design,
                groups=channel_df["subject"].astype(str),
            )
            result = model.fit(reml=False, method="lbfgs", maxiter=500, disp=False)
        return result, {
            "model_status": "ok",
            "model_message": " | ".join(sorted({str(w.message) for w in caught})),
            "converged": bool(getattr(result, "converged", False)),
            "n_observations": int(result.nobs),
            "n_subjects": int(channel_df["subject"].nunique()),
        }
    except Exception as exc:
        return None, {
            "model_status": "error",
            "model_message": str(exc),
            "converged": False,
            "n_observations": int(len(channel_df)),
            "n_subjects": int(channel_df["subject"].nunique()),
        }


def compute_channel_contrasts(
    result: Any,
    channel_info: dict[str, Any],
    model_info: dict[str, Any],
) -> list[dict[str, Any]]:
    params = result.fe_params.reindex(MODEL_COLUMNS)
    cov = result.cov_params().loc[MODEL_COLUMNS, MODEL_COLUMNS]
    rows = []

    for contrast_name, contrast_weights in CONTRASTS.items():
        vector = make_contrast_vector(contrast_weights, list(MODEL_COLUMNS))
        estimate = float(np.dot(vector, params.to_numpy()))
        variance = float(vector @ cov.to_numpy() @ vector)
        se = float(np.sqrt(variance)) if variance >= 0 else np.nan
        z_stat = estimate / se if se and np.isfinite(se) else np.nan
        p_value = float(2 * stats.norm.sf(abs(z_stat))) if np.isfinite(z_stat) else np.nan

        rows.append(
            {
                **channel_info,
                **model_info,
                "comparison": contrast_name,
                "effect": estimate,
                "se": se,
                "z_stat": float(z_stat) if np.isfinite(z_stat) else np.nan,
                "p_value": p_value,
                "test": "MixedLM beta ~ -1 + Group:Condition + (1|Subject)",
            }
        )
    return rows


def add_multiple_comparison_columns(df: pd.DataFrame, alpha: float) -> pd.DataFrame:
    corrected = []
    for (comparison, chroma), sub_df in df.groupby(["comparison", "Chroma"], dropna=False):
        sub_df = sub_df.copy()
        n_tests = sub_df["p_value"].notna().sum()
        sub_df["p_bonferroni"] = (sub_df["p_value"] * n_tests).clip(upper=1)
        sub_df["significant_bonferroni"] = sub_df["p_bonferroni"] < alpha
        sub_df["p_fdr"] = np.nan
        sub_df["significant_fdr"] = False
        valid = sub_df["p_value"].notna()
        if valid.any():
            rejected, q_values = fdrcorrection(sub_df.loc[valid, "p_value"], alpha=alpha)
            sub_df.loc[valid, "p_fdr"] = q_values
            sub_df.loc[valid, "significant_fdr"] = rejected
        corrected.append(sub_df)
    return pd.concat(corrected, ignore_index=True)


def compute_mixed_effects_stats(beta_df: pd.DataFrame, alpha: float) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    group_cols = ["Chroma", "ch_name", "Source", "Detector"]

    for keys, channel_df in beta_df.groupby(group_cols, dropna=False):
        chroma, ch_name, source, detector = keys
        channel_info = {
            "Chroma": chroma,
            "ch_name": ch_name,
            "Source": source,
            "Detector": detector,
        }
        result, model_info = fit_channel_model(channel_df)
        if result is None:
            for contrast_name in CONTRASTS:
                rows.append(
                    {
                        **channel_info,
                        **model_info,
                        "comparison": contrast_name,
                        "effect": np.nan,
                        "se": np.nan,
                        "z_stat": np.nan,
                        "p_value": np.nan,
                        "test": "MixedLM beta ~ -1 + Group:Condition + (1|Subject)",
                    }
                )
            continue

        rows.extend(compute_channel_contrasts(result, channel_info, model_info))

    return add_multiple_comparison_columns(pd.DataFrame(rows), alpha=alpha)


def summarize_results(stats_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (comparison, chroma), sub_df in stats_df.groupby(["comparison", "Chroma"]):
        rows.append(
            {
                "comparison": comparison,
                "Chroma": chroma,
                "n_channels": len(sub_df),
                "n_models_ok": int((sub_df["model_status"] == "ok").sum()),
                "n_models_converged": int(sub_df["converged"].fillna(False).sum()),
                "n_uncorrected_p_lt_0_05": int((sub_df["p_value"] < 0.05).sum()),
                "n_fdr_significant": int(sub_df["significant_fdr"].sum()),
                "n_bonferroni_significant": int(sub_df["significant_bonferroni"].sum()),
                "min_p_value": float(sub_df["p_value"].min()),
                "min_p_fdr": float(sub_df["p_fdr"].min()),
                "min_p_bonferroni": float(sub_df["p_bonferroni"].min()),
            }
        )
    return pd.DataFrame(rows).sort_values(["comparison", "Chroma"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run MATLAB-like mixed-effects group analysis.")
    parser.add_argument("--config", type=Path, default=Path("config/config_template.yaml"))
    parser.add_argument("--beta-table", type=Path, default=None)
    parser.add_argument("--output-table", type=Path, default=None)
    parser.add_argument("--summary-table", type=Path, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    group_config = config.get("analysis", {}).get("mixed_effects_group", {})
    if not group_config:
        group_config = config.get("analysis", {}).get("group", {})
    alpha = float(group_config.get("alpha", 0.05))

    beta_table = args.beta_table or Path(
        group_config.get("beta_table", "results/first_level_betas_ssreg.csv")
    )
    output_table = args.output_table or Path(
        group_config.get(
            "output_table",
            "results/group_level_mixed_effects_channel_stats_ssreg_long_hbo.csv",
        )
    )
    summary_table = args.summary_table or Path(
        group_config.get(
            "summary_table",
            "results/group_level_mixed_effects_summary_ssreg_long_hbo.csv",
        )
    )

    beta_df = pd.read_csv(beta_table)
    beta_df = filter_beta_table(beta_df, group_config)
    stats_df = compute_mixed_effects_stats(beta_df, alpha=alpha)
    summary_df = summarize_results(stats_df)

    output_table.parent.mkdir(parents=True, exist_ok=True)
    summary_table.parent.mkdir(parents=True, exist_ok=True)
    stats_df.to_csv(output_table, index=False)
    summary_df.to_csv(summary_table, index=False)

    print(summary_df.to_string(index=False))
    print(f"\nSaved mixed-effects channel stats to {output_table}")
    print(f"Saved mixed-effects summary to {summary_table}")


if __name__ == "__main__":
    main()
