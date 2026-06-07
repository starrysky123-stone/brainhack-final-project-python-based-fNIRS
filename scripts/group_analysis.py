"""Run group-level channel statistics on first-level fNIRS contrasts.

The input is the first-level ``MA-Control`` contrast table produced by
``scripts/first_level_glm.py``. This script computes:

- one-sample tests for the MA-Control effect within each grade group
- Welch two-sample tests comparing G4_6 and G1_3 effects

Local CSV outputs are ignored by Git because they contain per-channel derived
results from private participant data.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import fdrcorrection

from load_data import load_config


GROUP_ORDER = ("G1_3", "G4_6")


def safe_one_sample_t(values: pd.Series) -> tuple[float, float, float, int]:
    clean = values.dropna().astype(float)
    n = len(clean)
    if n < 2:
        return np.nan, np.nan, np.nan, n
    result = stats.ttest_1samp(clean, popmean=0.0, nan_policy="omit")
    return float(clean.mean()), float(result.statistic), float(result.pvalue), n


def safe_welch_t(
    group_a: pd.Series,
    group_b: pd.Series,
) -> tuple[float, float, float, float, float, int, int]:
    a = group_a.dropna().astype(float)
    b = group_b.dropna().astype(float)
    if len(a) < 2 or len(b) < 2:
        return np.nan, np.nan, np.nan, np.nan, np.nan, len(a), len(b)
    result = stats.ttest_ind(b, a, equal_var=False, nan_policy="omit")
    return (
        float(a.mean()),
        float(b.mean()),
        float(b.mean() - a.mean()),
        float(result.statistic),
        float(result.pvalue),
        len(a),
        len(b),
    )


def add_multiple_comparison_columns(df: pd.DataFrame, alpha: float) -> pd.DataFrame:
    corrected = []
    for (comparison, chroma), sub_df in df.groupby(["comparison", "Chroma"], dropna=False):
        sub_df = sub_df.copy()
        n_tests = sub_df["p_value"].notna().sum()
        sub_df["p_bonferroni"] = (sub_df["p_value"] * n_tests).clip(upper=1)
        sub_df["significant_bonferroni"] = sub_df["p_bonferroni"] < alpha
        if n_tests:
            valid = sub_df["p_value"].notna()
            rejected, q_values = fdrcorrection(sub_df.loc[valid, "p_value"], alpha=alpha)
            sub_df["p_fdr"] = np.nan
            sub_df["significant_fdr"] = False
            sub_df.loc[valid, "p_fdr"] = q_values
            sub_df.loc[valid, "significant_fdr"] = rejected
        else:
            sub_df["p_fdr"] = np.nan
            sub_df["significant_fdr"] = False
        corrected.append(sub_df)
    return pd.concat(corrected, ignore_index=True)


def compute_group_stats(contrast_df: pd.DataFrame, alpha: float) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    group_cols = ["Chroma", "ch_name", "Source", "Detector"]

    for keys, channel_df in contrast_df.groupby(group_cols, dropna=False):
        chroma, ch_name, source, detector = keys

        for group in GROUP_ORDER:
            values = channel_df.loc[channel_df["group"] == group, "effect"]
            mean_effect, t_stat, p_value, n_subjects = safe_one_sample_t(values)
            rows.append(
                {
                    "comparison": f"{group} MA-Control",
                    "Chroma": chroma,
                    "ch_name": ch_name,
                    "Source": source,
                    "Detector": detector,
                    "n_subjects": n_subjects,
                    "mean_effect": mean_effect,
                    "group1_mean": mean_effect,
                    "group2_mean": np.nan,
                    "difference": mean_effect,
                    "t_stat": t_stat,
                    "p_value": p_value,
                    "test": "one-sample t-test vs 0",
                }
            )

        g1 = channel_df.loc[channel_df["group"] == "G1_3", "effect"]
        g2 = channel_df.loc[channel_df["group"] == "G4_6", "effect"]
        g1_mean, g2_mean, difference, t_stat, p_value, n_g1, n_g2 = safe_welch_t(g1, g2)
        rows.append(
            {
                "comparison": "G4_6 minus G1_3 MA-Control",
                "Chroma": chroma,
                "ch_name": ch_name,
                "Source": source,
                "Detector": detector,
                "n_subjects": n_g1 + n_g2,
                "n_G1_3": n_g1,
                "n_G4_6": n_g2,
                "mean_effect": difference,
                "group1_mean": g1_mean,
                "group2_mean": g2_mean,
                "difference": difference,
                "t_stat": t_stat,
                "p_value": p_value,
                "test": "Welch two-sample t-test",
            }
        )

    return add_multiple_comparison_columns(pd.DataFrame(rows), alpha=alpha)


def summarize_results(stats_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (comparison, chroma), sub_df in stats_df.groupby(["comparison", "Chroma"]):
        rows.append(
            {
                "comparison": comparison,
                "Chroma": chroma,
                "n_channels": len(sub_df),
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
    parser = argparse.ArgumentParser(description="Run group-level fNIRS channel analysis.")
    parser.add_argument("--config", type=Path, default=Path("config/config_template.yaml"))
    parser.add_argument("--contrast-table", type=Path, default=None)
    parser.add_argument("--output-table", type=Path, default=None)
    parser.add_argument("--summary-table", type=Path, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    group_config = config.get("analysis", {}).get("group", {})
    alpha = float(group_config.get("alpha", 0.05))

    contrast_table = args.contrast_table or Path(
        group_config.get("contrast_table", "results/first_level_contrasts.csv")
    )
    output_table = args.output_table or Path(
        group_config.get("output_table", "results/group_level_channel_stats.csv")
    )
    summary_table = args.summary_table or Path(
        group_config.get("summary_table", "results/group_level_summary.csv")
    )

    contrast_df = pd.read_csv(contrast_table)
    stats_df = compute_group_stats(contrast_df, alpha=alpha)
    summary_df = summarize_results(stats_df)

    output_table.parent.mkdir(parents=True, exist_ok=True)
    summary_table.parent.mkdir(parents=True, exist_ok=True)
    stats_df.to_csv(output_table, index=False)
    summary_df.to_csv(summary_table, index=False)

    print(summary_df.to_string(index=False))
    print(f"\nSaved group-level channel stats to {output_table}")
    print(f"Saved group-level summary to {summary_table}")


if __name__ == "__main__":
    main()
