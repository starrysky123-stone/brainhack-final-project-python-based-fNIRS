# Mixed-Effects Group-Level MA Summary

This document summarizes the Python mixed-effects group analysis added to more
closely approximate the MATLAB/nirs-toolbox group model.

## Why This Step Was Added

The original MATLAB/nirs-toolbox group-level analysis used:

```text
beta ~ -1 + Group:cond + (1|Subject)
```

The first Python group analysis used channel-wise t-tests on each participant's
`MA-Control` first-level contrast. That approach is valid as a simple
exploratory analysis, but it is not the same statistical model as the MATLAB
mixed-effects analysis.

The new script:

```text
scripts/group_mixed_effects.py
```

fits a separate random-intercept mixed model for each long-distance HbO channel
using first-level condition betas.

## Model

For each channel, the Python model uses:

```text
theta ~ -1 + Group:Condition + (1|Subject)
```

where `theta` is the first-level beta estimate from MNE-NIRS.

The modeled cells follow the MATLAB contrast order:

```text
G4_6:Control
G1_3:Control
G4_6:MA
G1_3:MA
G4_6:PA
G1_3:PA
```

The tested contrasts are:

1. `G4_6 MA - Control`
2. `G1_3 MA - Control`
3. `G4_6 MA effect - G1_3 MA effect`

## Batch Result

The mixed-effects analysis used 32 long-distance HbO channels. All 32 channel
models completed successfully and converged.

| Comparison | Chroma | Channels | Models converged | Uncorrected p < .05 | FDR significant | Bonferroni significant |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| G1_3 MA - Control | HbO | 32 | 32 | 1 | 0 | 0 |
| G4_6 MA - Control | HbO | 32 | 32 | 2 | 0 | 0 |
| G4_6 MA effect - G1_3 MA effect | HbO | 32 | 32 | 0 | 0 | 0 |

## Descriptive Top Channels

The smallest uncorrected p-values were:

| Comparison | Chroma | Channel | z | p | FDR p |
| --- | --- | --- | ---: | ---: | ---: |
| G1_3 MA - Control | HbO | S1_D1 hbo | 2.358071 | 0.018370 | 0.587846 |
| G4_6 MA - Control | HbO | S1_D4 hbo | 2.212083 | 0.026961 | 0.549683 |
| G4_6 MA - Control | HbO | S11_D13 hbo | -2.115878 | 0.034355 | 0.549683 |
| G4_6 MA effect - G1_3 MA effect | HbO | S1_D1 hbo | -1.553607 | 0.120278 | 0.968250 |

These are descriptive exploratory results only. No channel survived FDR or
Bonferroni correction.

## Figures

![MA mixed-effects significance counts](../figures/ma_mixed_effects_group_significance_counts.png)

![Top MA mixed-effects channel p-values](../figures/ma_mixed_effects_top_channel_pvalues.png)

## Relationship to MATLAB

This mixed-effects script improves alignment with the MATLAB group-level model,
but it is still not a full numerical replication of the MATLAB pipeline.

Remaining differences include:

- MATLAB first-level GLM uses AR-IRLS, while the current Python first-level GLM
  uses MNE-NIRS `ar1`.
- MATLAB and Python HRF implementations may differ.
- MATLAB/nirs-toolbox and statsmodels may estimate mixed-effects models with
  different numerical solvers and defaults.
- MATLAB-vs-MNE preprocessing validation is still pending MATLAB export.

## Reproduce This Step

Use the project conda environment:

```bash
conda activate brainhack-fnirs
python scripts/group_mixed_effects.py
python scripts/visualization.py \
  --stats results/group_level_mixed_effects_channel_stats_ssreg_long_hbo.csv \
  --summary results/group_level_mixed_effects_summary_ssreg_long_hbo.csv \
  --output-prefix ma_mixed_effects \
  --figure-title "MA-Control Mixed-Effects Long-HbO"
```

The script writes local tables to:

```text
results/group_level_mixed_effects_channel_stats_ssreg_long_hbo.csv
results/group_level_mixed_effects_summary_ssreg_long_hbo.csv
```

These result tables are ignored by Git because they contain local derived
analysis outputs.
