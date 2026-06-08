"""Create summary figures for the MA-focused fNIRS group analysis.

The figures are based on aggregate group-level result tables and do not expose
participant-level raw or derivative time series.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_STATS = Path("results/group_level_channel_stats_ssreg_long_hbo.csv")
DEFAULT_SUMMARY = Path("results/group_level_summary_ssreg_long_hbo.csv")
DEFAULT_OUTPUT_DIR = Path("figures")


COMPARISON_LABELS = {
    "G1_3 MA-Control": "G1-3\nMA-Control",
    "G4_6 MA-Control": "G4-6\nMA-Control",
    "G4_6 minus G1_3 MA-Control": "G4-6 minus G1-3\nMA-Control",
}


def _check_input(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing input table: {path}. Run scripts/group_analysis.py first."
        )


def _comparison_order(values: pd.Series) -> list[str]:
    preferred = list(COMPARISON_LABELS)
    present = list(values.dropna().unique())
    ordered = [name for name in preferred if name in present]
    ordered.extend(name for name in present if name not in ordered)
    return ordered


def plot_significance_counts(summary: pd.DataFrame, output_dir: Path) -> Path:
    """Plot uncorrected and corrected significant-channel counts."""
    order = _comparison_order(summary["comparison"])
    summary = summary.set_index("comparison").loc[order].reset_index()

    x = np.arange(len(summary))
    width = 0.24

    fig, ax = plt.subplots(figsize=(8.6, 4.8), constrained_layout=True)
    colors = {
        "uncorrected": "#4C78A8",
        "fdr": "#F58518",
        "bonferroni": "#54A24B",
    }

    bars1 = ax.bar(
        x - width,
        summary["n_uncorrected_p_lt_0_05"],
        width,
        label="Uncorrected p < .05",
        color=colors["uncorrected"],
    )
    bars2 = ax.bar(
        x,
        summary["n_fdr_significant"],
        width,
        label="FDR q < .05",
        color=colors["fdr"],
    )
    bars3 = ax.bar(
        x + width,
        summary["n_bonferroni_significant"],
        width,
        label="Bonferroni p < .05",
        color=colors["bonferroni"],
    )

    for bars in (bars1, bars2, bars3):
        ax.bar_label(bars, padding=3, fontsize=9)

    ax.set_title("MA-Control Group-Level Long-HbO Channel Counts")
    ax.set_ylabel("Number of channels")
    ax.set_xticks(x)
    ax.set_xticklabels([COMPARISON_LABELS.get(name, name) for name in order])
    ax.set_ylim(0, max(3, int(summary["n_uncorrected_p_lt_0_05"].max()) + 1))
    ax.legend(frameon=False, ncols=1)
    ax.spines[["top", "right"]].set_visible(False)

    output_path = output_dir / "ma_group_significance_counts.png"
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
    return output_path


def plot_top_channels(stats: pd.DataFrame, output_dir: Path, n_top: int = 8) -> Path:
    """Plot the lowest-p channels for each comparison."""
    order = _comparison_order(stats["comparison"])
    color_lookup = {
        "G1_3 MA-Control": "#4C78A8",
        "G4_6 MA-Control": "#F58518",
        "G4_6 minus G1_3 MA-Control": "#54A24B",
    }

    fig, axes = plt.subplots(
        1,
        len(order),
        figsize=(11.4, 5.2),
        sharex=True,
        constrained_layout=True,
    )
    if len(order) == 1:
        axes = [axes]

    max_x = -np.log10(stats["p_value"].clip(lower=np.finfo(float).tiny)).max()
    threshold = -np.log10(0.05)

    for ax, comparison in zip(axes, order):
        subset = (
            stats.loc[stats["comparison"] == comparison]
            .sort_values("p_value")
            .head(n_top)
            .copy()
        )
        subset["neg_log10_p"] = -np.log10(
            subset["p_value"].clip(lower=np.finfo(float).tiny)
        )

        y = np.arange(len(subset))
        ax.barh(
            y,
            subset["neg_log10_p"],
            color=color_lookup.get(comparison, "#777777"),
        )
        ax.axvline(threshold, color="#444444", linestyle="--", linewidth=1)
        ax.set_yticks(y)
        ax.set_yticklabels(subset["ch_name"], fontsize=8)
        ax.invert_yaxis()
        ax.set_title(COMPARISON_LABELS.get(comparison, comparison), fontsize=11)
        ax.set_xlim(0, max(threshold + 0.25, max_x + 0.15))
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle(f"Top {n_top} Long-HbO Channels per MA Comparison", fontsize=14)
    fig.supxlabel("-log10(p)")
    axes[-1].text(
        threshold + 0.02,
        -0.75,
        "p = .05",
        va="center",
        ha="left",
        fontsize=9,
        color="#444444",
    )

    output_path = output_dir / "ma_top_channel_pvalues.png"
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
    return output_path


def build_figures(stats_path: Path, summary_path: Path, output_dir: Path) -> list[Path]:
    _check_input(stats_path)
    _check_input(summary_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    stats = pd.read_csv(stats_path)
    summary = pd.read_csv(summary_path)

    required_stats = {"comparison", "ch_name", "p_value"}
    required_summary = {
        "comparison",
        "n_uncorrected_p_lt_0_05",
        "n_fdr_significant",
        "n_bonferroni_significant",
    }
    missing_stats = required_stats.difference(stats.columns)
    missing_summary = required_summary.difference(summary.columns)
    if missing_stats:
        raise ValueError(f"Stats table missing columns: {sorted(missing_stats)}")
    if missing_summary:
        raise ValueError(f"Summary table missing columns: {sorted(missing_summary)}")

    return [
        plot_significance_counts(summary, output_dir),
        plot_top_channels(stats, output_dir),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create aggregate MA group-analysis figures."
    )
    parser.add_argument("--stats", type=Path, default=DEFAULT_STATS)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = build_figures(args.stats, args.summary, args.output_dir)
    print("Wrote figures:")
    for path in outputs:
        print(f"- {path}")


if __name__ == "__main__":
    main()
