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

The group-level script computes three channel-level analyses:

1. `G1_3 MA-Control`: one-sample t-test against 0.
2. `G4_6 MA-Control`: one-sample t-test against 0.
3. `G4_6 minus G1_3 MA-Control`: Welch two-sample t-test.

Multiple-comparison correction is applied separately for each comparison and
chromophore across 40 channels:

- FDR correction
- Bonferroni correction

## Batch Result

The group analysis used all 131 participants:

| Group | Number of subjects |
| --- | ---: |
| G1_3 | 59 |
| G4_6 | 72 |
| Total | 131 |

The result table contains 240 rows:

```text
3 comparisons x 2 chromophores x 40 channels
```

## Main Result

No channel survived FDR or Bonferroni correction at alpha = 0.05.

Uncorrected channel counts with `p < .05`:

| Comparison | Chroma | Uncorrected p < .05 | FDR significant | Bonferroni significant |
| --- | --- | ---: | ---: | ---: |
| G1_3 MA-Control | HbO | 4 | 0 | 0 |
| G1_3 MA-Control | HbR | 1 | 0 | 0 |
| G4_6 MA-Control | HbO | 1 | 0 | 0 |
| G4_6 MA-Control | HbR | 1 | 0 | 0 |
| G4_6 minus G1_3 MA-Control | HbO | 1 | 0 | 0 |
| G4_6 minus G1_3 MA-Control | HbR | 0 | 0 | 0 |

## Descriptive Top Channels

The smallest uncorrected p-values were:

| Comparison | Chroma | Channel | p | FDR p |
| --- | --- | --- | ---: | ---: |
| G1_3 MA-Control | HbO | S1_D1 hbo | 0.002041 | 0.081644 |
| G4_6 MA-Control | HbR | S9_D20 hbr | 0.009051 | 0.362055 |
| G1_3 MA-Control | HbR | S10_D21 hbr | 0.010989 | 0.439574 |
| G4_6 minus G1_3 MA-Control | HbO | S3_D8 hbo | 0.049535 | 0.987961 |

These are descriptive exploratory results only. The corrected analysis did not
identify statistically significant channels.

## Reproduce This Step

```bash
conda activate brainhack-fnirs
python scripts/group_analysis.py
```

The script writes local tables to:

```text
results/group_level_channel_stats.csv
results/group_level_summary.csv
```
