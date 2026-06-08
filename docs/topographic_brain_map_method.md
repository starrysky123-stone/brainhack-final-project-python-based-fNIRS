# Topographic fNIRS Brain Map Method

This note documents how the project generated the final topographic fNIRS brain
maps.

## What Was Plotted

The maps visualize the group-level mixed-effects estimates for the MA task
contrast:

```text
MA - Control
```

The plotted channels are the 32 long-distance HbO channels used in the main
Python group-level analysis.

The three panels are:

1. `G1-3 MA-Control`
2. `G4-6 MA-Control`
3. `G4-6 minus G1-3`

## Code Source

The plotting script was written specifically for this project:

```text
scripts/plot_brain_maps.py
```

The core visualization function comes from the official MNE-Python
visualization API:

```text
mne.viz.plot_topomap
https://mne.tools/stable/generated/mne.viz.plot_topomap.html
```

The script uses the preprocessed FIF file to obtain the fNIRS channel montage
and uses the mixed-effects group result table for the values plotted on each
channel.

## Interpretation

These figures should be described as fNIRS topographic maps or channel-level
topographic maps. They are not structural MRI activation maps.

The maps are aggregate visualizations. They do not contain raw data,
participant-level time series, or subject-identifying information.

## Reproduce

Run:

```bash
python scripts/plot_brain_maps.py
```

Outputs:

```text
figures/ma_mixed_effects_topographic_maps.png
figures/ma_mixed_effects_topomap_g1_3_ma_control.png
figures/ma_mixed_effects_topomap_g4_6_ma_control.png
figures/ma_mixed_effects_topomap_g4_6_minus_g1_3.png
```
