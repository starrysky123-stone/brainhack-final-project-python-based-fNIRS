"""Create fNIRS topographic brain maps for MA group effects.

The maps use the local fNIRS montage stored in the preprocessed FIF files and
the long-HbO mixed-effects group statistics. The output figures are aggregate
visualizations and do not contain participant-level data.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import mne
import numpy as np
import pandas as pd
from mne_nirs.channels import get_long_channels


COMPARISONS = (
    ("G1_3 MA - Control", "G1-3 MA-Control"),
    ("G4_6 MA - Control", "G4-6 MA-Control"),
    ("G4_6 MA effect - G1_3 MA effect", "G4-6 minus G1-3"),
)


def find_reference_fif(preprocessed_dir: Path) -> Path:
    fif_files = sorted(preprocessed_dir.rglob("*_hbo_hbr_raw.fif"))
    if not fif_files:
        raise FileNotFoundError(f"No preprocessed FIF files found under {preprocessed_dir}")
    return fif_files[0]


def load_long_hbo_info(preprocessed_dir: Path, channel_names: set[str]) -> mne.Info:
    raw = mne.io.read_raw_fif(find_reference_fif(preprocessed_dir), preload=False, verbose="error")
    long_hbo = get_long_channels(raw.copy().pick("hbo"))
    ordered_channels = [ch for ch in long_hbo.ch_names if ch in channel_names]
    if not ordered_channels:
        raise ValueError("No long-HbO channels in the stats table matched the FIF montage.")
    return long_hbo.copy().pick(ordered_channels).info


def comparison_values(stats_df: pd.DataFrame, comparison: str, ch_names: list[str]) -> np.ndarray:
    comparison_df = stats_df[stats_df["comparison"] == comparison].set_index("ch_name")
    missing = [ch for ch in ch_names if ch not in comparison_df.index]
    if missing:
        raise ValueError(
            f"Stats table is missing {len(missing)} channels for {comparison}: {missing[:5]}"
        )
    return comparison_df.loc[ch_names, "effect"].to_numpy(dtype=float)


def save_single_map(
    values: np.ndarray,
    info: mne.Info,
    title: str,
    vmax: float,
    output_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 5.4), constrained_layout=True)
    image, _ = mne.viz.plot_topomap(
        values,
        info,
        axes=ax,
        show=False,
        contours=0,
        cmap="RdBu_r",
        vlim=(-vmax, vmax),
        sensors=True,
        extrapolate="local",
    )
    ax.set_title(title, fontsize=13)
    cbar = fig.colorbar(image, ax=ax, shrink=0.82)
    cbar.set_label("Mixed-effects estimate (HbO)")
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def save_panel_map(
    stats_df: pd.DataFrame,
    info: mne.Info,
    vmax: float,
    output_path: Path,
) -> None:
    ch_names = info.ch_names
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.8), constrained_layout=True)
    last_image = None

    for ax, (comparison, title) in zip(axes, COMPARISONS):
        values = comparison_values(stats_df, comparison, ch_names)
        last_image, _ = mne.viz.plot_topomap(
            values,
            info,
            axes=ax,
            show=False,
            contours=0,
            cmap="RdBu_r",
            vlim=(-vmax, vmax),
            sensors=True,
            extrapolate="local",
        )
        ax.set_title(title, fontsize=12)

    cbar = fig.colorbar(last_image, ax=axes, shrink=0.82)
    cbar.set_label("Mixed-effects estimate (HbO)")
    fig.suptitle("MA-Related Long-HbO fNIRS Topographic Maps", fontsize=15)
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot MA fNIRS topographic brain maps.")
    parser.add_argument(
        "--stats",
        type=Path,
        default=Path("results/group_level_mixed_effects_channel_stats_ssreg_long_hbo.csv"),
    )
    parser.add_argument(
        "--preprocessed-dir",
        type=Path,
        default=Path("derivatives/preprocessed"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("figures"))
    args = parser.parse_args()

    if not args.stats.exists():
        raise FileNotFoundError(
            f"No stats table found at {args.stats}. Run scripts/group_mixed_effects.py first."
        )

    stats_df = pd.read_csv(args.stats)
    stats_df = stats_df[stats_df["Chroma"] == "hbo"].copy()
    channel_names = set(stats_df["ch_name"].dropna())
    info = load_long_hbo_info(args.preprocessed_dir, channel_names)
    ch_names = info.ch_names

    all_values = np.concatenate(
        [comparison_values(stats_df, comparison, ch_names) for comparison, _ in COMPARISONS]
    )
    vmax = float(np.nanmax(np.abs(all_values)))
    if not np.isfinite(vmax) or vmax == 0:
        vmax = 1.0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    save_panel_map(
        stats_df,
        info,
        vmax,
        args.output_dir / "ma_mixed_effects_topographic_maps.png",
    )

    for comparison, title in COMPARISONS:
        values = comparison_values(stats_df, comparison, ch_names)
        slug = (
            title.lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("__", "_")
        )
        save_single_map(
            values,
            info,
            title,
            vmax,
            args.output_dir / f"ma_mixed_effects_topomap_{slug}.png",
        )

    print(f"Saved topographic maps to {args.output_dir}")


if __name__ == "__main__":
    main()
