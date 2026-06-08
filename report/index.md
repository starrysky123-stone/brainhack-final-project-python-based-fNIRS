# MA-Related fNIRS Brain Activation Differences Between Lower- and Upper-Grade Children

## Overview

This BrainHack final project examines morphological awareness (MA)-related
brain activation in children using fNIRS. The main scientific goal is to
compare lower-grade children (Grades 1-3; `G1_3`) and upper-grade children
(Grades 4-6; `G4_6`) during the MA task.

The main task contrast is:

```text
MA - Control
```

The main group contrast is:

```text
(G4_6 MA - G4_6 Control) - (G1_3 MA - G1_3 Control)
```

The project also builds an MNE-Python/MNE-NIRS analysis pipeline with reference
to an existing MATLAB/nirs-toolbox workflow. The MATLAB comparison is used as a
methodological validation step, while the central research focus remains the
MA-related activation difference between grade groups.

## Research Question

Do lower-grade and upper-grade children show different fNIRS brain activation
patterns during morphological awareness processing?

## Data

The local dataset contains SNIRF files from 131 child participants.

| Group | Subjects |
| --- | ---: |
| `G1_3` | 59 |
| `G4_6` | 72 |
| Total | 131 |

The SNIRF event labels were mapped according to the original MATLAB pipeline:

| SNIRF label | Condition |
| --- | --- |
| `1` | `MA` |
| `2` | `PA` |
| `3` | `Control` |

All participants had complete `MA` and `Control` event markers for the current
MA-focused analysis. One participant had 17 `PA` events instead of 16, but this
does not affect the current `MA-Control` analysis.

Raw data and participant-level derivative files are not uploaded to GitHub
because the dataset contains child-participant data.

## New Skills and Open Science

The main new skill learned in this project is the use of MNE-Python and
MNE-NIRS for fNIRS data analysis. This includes:

- loading SNIRF files in Python
- preprocessing fNIRS signals
- estimating subject-level GLM models
- constructing group-level MA contrasts
- generating reproducible aggregate result figures
- planning MATLAB-to-MNE preprocessing validation

The project follows an open-science structure by keeping code, documentation,
and aggregate figures in the repository. Raw data, subject-level derivatives,
participant information, and local validation exports are excluded from Git.

## Methods

The analysis method has two connected components:

1. A Python-based fNIRS pipeline using MNE-Python and MNE-NIRS.
2. A MATLAB/nirs-toolbox reference pipeline used for methodological alignment
   and validation.

The MATLAB-Python comparison separates two issues:

1. Whether a MATLAB/nirs-toolbox function has a corresponding MNE-Python or
   MNE-NIRS function.
2. Whether MATLAB and Python outputs are numerically similar when the functions
   are intended to perform the same preprocessing step.

The function mapping is documented in
`docs/matlab_mne_function_mapping.md`. The numerical validation procedure is
documented in `docs/matlab_validation_runbook.md`.

A concise response to the TA feedback is documented in
`docs/ta_feedback_response.md`.

## Python Pipeline

The current Python pipeline is script-based:

| Step | Script |
| --- | --- |
| SNIRF loading and event validation | `scripts/load_data.py` |
| fNIRS preprocessing | `scripts/preprocess_fnirs.py` |
| First-level GLM | `scripts/first_level_glm.py` |
| Group-level MA analysis | `scripts/group_analysis.py` |
| Result visualization | `scripts/visualization.py` |

Preprocessing steps:

1. Load SNIRF raw intensity data.
2. Rename events to `MA`, `PA`, and `Control`.
3. Resample to 2 Hz.
4. Convert raw intensity to optical density.
5. Convert optical density to HbO/HbR concentration.
6. Trim the recording to the task window with 5 seconds before the first event
   and 5 seconds after the last event.

First-level GLM settings:

- HRF model: `glover`
- stimulus duration: 10 seconds
- drift model: cosine
- high-pass value: 0.008
- noise model: `ar1`
- short-separation regressors: enabled
- primary contrast: `MA-Control`

Group-level analysis uses each participant's `MA-Control` contrast and focuses
on 32 long-distance HbO channels.

## Results

All 131 local SNIRF files were loaded and preprocessed successfully.

All 131 participants completed the first-level GLM.

The current Python group-level analysis did not identify corrected significant
long-HbO channels.

| Comparison | Uncorrected p < .05 | FDR significant | Bonferroni significant |
| --- | ---: | ---: | ---: |
| `G1_3 MA-Control` | 2 | 0 | 0 |
| `G4_6 MA-Control` | 1 | 0 | 0 |
| `G4_6 minus G1_3 MA-Control` | 0 | 0 | 0 |

The smallest uncorrected p-values were:

| Comparison | Channel | p | FDR p |
| --- | --- | ---: | ---: |
| `G1_3 MA-Control` | `S1_D1 hbo` | 0.004539 | 0.145263 |
| `G4_6 MA-Control` | `S11_D13 hbo` | 0.031599 | 0.594439 |
| `G1_3 MA-Control` | `S1_D4 hbo` | 0.043052 | 0.634445 |
| `G4_6 minus G1_3 MA-Control` | `S1_D1 hbo` | 0.086210 | 0.956130 |

These results are preliminary and should be interpreted cautiously. The Python
pipeline provides a reproducible MA analysis workflow, but the current
statistical result should not be presented as a direct numerical replication of
the MATLAB/nirs-toolbox result.

## Figures

![MA group-level significance counts](../figures/ma_group_significance_counts.png)

![Top MA channel p-values](../figures/ma_top_channel_pvalues.png)

These figures are generated from aggregate group-level summary tables, not from
raw participant-level time series.

## MATLAB Comparison and Validation Status

The original MATLAB/nirs-toolbox workflow used methods that are not identical
to the current MNE-Python implementation.

Important remaining differences include:

- MATLAB first-level GLM used AR-IRLS, while the Python pipeline uses `ar1`.
- MATLAB group analysis used a mixed-effects model, while the current Python
  pipeline uses channel-wise t-tests on subject-level contrasts.
- HRF and model details may differ between nirs-toolbox and MNE-NIRS.
- Some saved MATLAB contrast-table filenames and internal contrast labels
  should be checked before treating the MATLAB significant-channel summary as
  final.

The numerical preprocessing validation is prepared but not yet completed. The
blocking step is to run the MATLAB export script locally:

```matlab
run('scripts/export_matlab_preprocessed_for_validation.m')
```

After MATLAB export, the Python validation script can be run:

```bash
python scripts/validate_matlab_mne_preprocessing.py
```

The validation will compare MATLAB and MNE-Python preprocessed HbO/HbR time
series using channel-wise correlation, MAE, RMSE, and standard-deviation ratios.

## Interpretation

The current project demonstrates that an MNE-Python/MNE-NIRS pipeline can be
used to load, preprocess, model, and summarize local fNIRS data for an
MA-focused developmental comparison.

At the current stage, no corrected significant group-level long-HbO channel was
identified in the Python analysis. The result should be treated as exploratory
until MATLAB-vs-MNE preprocessing validation and possible group-model alignment
are completed.

## Reproducibility

The Python pipeline can be reproduced with:

```bash
python scripts/load_data.py --root-dir "/path/to/local/Anyalysis/group"
python scripts/preprocess_fnirs.py --root-dir "/path/to/local/Anyalysis/group" --overwrite
python scripts/first_level_glm.py
python scripts/group_analysis.py
python scripts/visualization.py
```

Local MATLAB validation is documented in:

```text
docs/matlab_validation_runbook.md
```

## Next Steps

1. Run the MATLAB preprocessing export locally.
2. Run the Python MATLAB-vs-MNE preprocessing validation.
3. Summarize whether the preprocessing outputs are numerically close enough.
4. Consider a Python mixed-effects group model to better match the MATLAB
   group-level analysis.
5. Polish the final presentation and record the project video.
