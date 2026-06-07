# First-Level GLM Summary

This document summarizes the subject-level GLM step of the MNE-Python fNIRS
pipeline. Per-subject result tables are stored locally under `results/` and are
not uploaded to GitHub.

## Model

The first-level model was run with MNE-NIRS using the preprocessed HbO/HbR FIF
files from `derivatives/preprocessed/`.

Main settings:

- Design matrix: `mne_nirs.experimental_design.make_first_level_design_matrix`
- HRF model: `glover`
- Stimulus duration: 10 seconds
- Drift model: cosine
- High-pass value for drift regressors: 0.008
- Noise model: `ar1`
- Conditions modeled: `MA`, `PA`, `Control`
- Primary contrast: `MA-Control`

The `PA` condition is included in the first-level design matrix, while the
current project focus remains the MA-related contrast.

## Batch Result

| Group | Number of subjects |
| --- | ---: |
| G1_3 | 59 |
| G4_6 | 72 |
| Total | 131 |

All 131 preprocessed participant files completed the first-level GLM.

## Output Tables

The script writes local result tables to:

```text
results/first_level_glm_summary.csv
results/first_level_betas.csv
results/first_level_contrasts.csv
```

These CSV files are ignored by Git because they contain per-subject derived
results.

Output size:

- First-level beta rows: 125,600
- First-level `MA-Control` contrast rows: 10,480

The contrast table contains one row per subject, channel, and chromophore.

## Quality-Control Notes

- GLM status: 131 successful, 0 failed.
- GLM warnings: 0.
- Most subjects had 12 design-matrix columns:
  `Control`, `MA`, `PA`, 8 cosine drift terms, and `constant`.
- Two subjects had 11 design-matrix columns because the cosine drift basis used
  one fewer drift term for their task-window duration.

## Descriptive Contrast Check

The number of uncorrected `MA-Control` channel-level results with `p < .05` was:

| Group | Chroma | Count |
| --- | --- | ---: |
| G1_3 | HbO | 258 |
| G1_3 | HbR | 253 |
| G4_6 | HbO | 342 |
| G4_6 | HbR | 300 |

These counts are only a descriptive first-level check. They are not a final
group-level statistical conclusion.

## Reproduce This Step

```bash
conda activate brainhack-fnirs
python scripts/first_level_glm.py
```
