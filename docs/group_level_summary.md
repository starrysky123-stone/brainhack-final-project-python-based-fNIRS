# Group-Level MA-Control Summary

This document summarizes the first group-level comparison for the MNE-Python
fNIRS pipeline. Per-channel result tables are stored locally under `results/`
and are not uploaded to GitHub.

## Research Contrast

The primary research contrast is:

```text
(G4_6 MA - G4_6 Control) - (G1_3 MA - G1_3 Control)
```

In the current Python pipeline, this is implemented by first estimating each
participant's `MA-Control` first-level contrast and then comparing those
contrast effects between grade groups at each channel and chromophore.

## Statistical Tests

The group-level script uses the short-separation-regressed first-level contrast
table and filters the analysis to long-distance HbO channels, matching the
MATLAB analysis focus more closely than the initial all-channel Python version.

It computes three channel-level analyses:

1. `G1_3 MA-Control`: one-sample t-test against 0.
2. `G4_6 MA-Control`: one-sample t-test against 0.
3. `G4_6 minus G1_3 MA-Control`: Welch two-sample t-test.

Multiple-comparison correction is applied separately for each comparison across
32 long-distance HbO channels:

- FDR correction
- Bonferroni correction

## Batch Result

The group analysis used all 131 participants:

| Group | Number of subjects |
| --- | ---: |
| G1_3 | 59 |
| G4_6 | 72 |
| Total | 131 |

The result table contains 96 rows:

```text
3 comparisons x 1 chromophore x 32 channels
```

## Main Result

No channel survived FDR or Bonferroni correction at alpha = 0.05.

Uncorrected long-HbO channel counts with `p < .05`:

| Comparison | Chroma | Uncorrected p < .05 | FDR significant | Bonferroni significant |
| --- | --- | ---: | ---: | ---: |
| G1_3 MA-Control | HbO | 2 | 0 | 0 |
| G4_6 MA-Control | HbO | 1 | 0 | 0 |
| G4_6 minus G1_3 MA-Control | HbO | 0 | 0 | 0 |

## Descriptive Top Channels

The smallest uncorrected p-values were:

| Comparison | Chroma | Channel | p | FDR p |
| --- | --- | --- | ---: | ---: |
| G1_3 MA-Control | HbO | S1_D1 hbo | 0.004539 | 0.145263 |
| G4_6 MA-Control | HbO | S11_D13 hbo | 0.031599 | 0.594439 |
| G1_3 MA-Control | HbO | S1_D4 hbo | 0.043052 | 0.634445 |
| G4_6 minus G1_3 MA-Control | HbO | S1_D1 hbo | 0.086210 | 0.956130 |

These are descriptive exploratory results only. The corrected analysis did not
identify statistically significant channels.

## Reproduce This Step

```bash
conda activate brainhack-fnirs
python scripts/group_analysis.py
```

The script writes local tables to:

```text
results/group_level_channel_stats_ssreg_long_hbo.csv
results/group_level_summary_ssreg_long_hbo.csv
```
