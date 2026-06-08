# BrainHack Final Project: MA-Related fNIRS Brain Activation Differences

## Project Title

MA-Related fNIRS Brain Activation Differences Between Lower- and Upper-Grade Children

## Project Overview

This project examines morphological awareness (MA)-related brain activation in
children using fNIRS. The primary scientific goal is to compare lower-grade
children (Grades 1-3; `G1_3`) with upper-grade children (Grades 4-6; `G4_6`)
during the MA task, using `MA-Control` as the main task contrast.

As the methodological component, this project builds an open-source
MNE-Python/MNE-NIRS analysis pipeline and develops it with reference to an
existing MATLAB/nirs-toolbox workflow. The MATLAB comparison is used to support
pipeline validation and interpretation, while the main research focus remains
the MA activation difference between grade groups.

The local dataset contains SNIRF files from 131 child participants. Raw and
derived participant-level files are not uploaded to GitHub because they contain
private child-participant data. This repository contains the analysis code,
configuration, documentation, and non-sensitive summaries.

## Main Research Question

Do lower-grade and upper-grade children show different fNIRS brain activation
patterns during morphological awareness processing?

The primary contrast is:

```text
(G4_6 MA - G4_6 Control) - (G1_3 MA - G1_3 Control)
```

The main condition-level contrast is `MA-Control`.

## Current Pipeline Status

To answer the MA research question, the current Python pipeline has completed
these stages:

1. Load local SNIRF files with `mne.io.read_raw_snirf`.
2. Rename event markers from the original SNIRF annotations:
   - `1` = `MA`
   - `2` = `PA`
   - `3` = `Control`
3. Validate that all participants have complete `MA` and `Control` events.
4. Preprocess fNIRS data with MNE-Python:
   - resample to 2 Hz
   - convert raw intensity to optical density
   - convert optical density to HbO/HbR concentration
   - trim the task window with 5 seconds before and after task timing
5. Run first-level GLM with MNE-NIRS:
   - model `MA`, `PA`, and `Control`
   - add short-separation channel regressors
   - estimate the subject-level `MA-Control` contrast
6. Run group-level long-HbO channel statistics:
   - `G1_3 MA-Control`
   - `G4_6 MA-Control`
   - `G4_6 minus G1_3 MA-Control`
7. Document a MATLAB-vs-MNE preprocessing validation plan as a method check.

## Current Results

All 131 local SNIRF files were loaded and preprocessed successfully.

| Group | Subjects |
| --- | ---: |
| G1_3 | 59 |
| G4_6 | 72 |
| Total | 131 |

The current group-level Python analysis focuses on 32 long-distance HbO
channels. No channel survived FDR or Bonferroni correction at alpha = 0.05.
Uncorrected exploratory results were:

| Comparison | Uncorrected p < .05 | FDR significant | Bonferroni significant |
| --- | ---: | ---: | ---: |
| G1_3 MA-Control | 2 | 0 | 0 |
| G4_6 MA-Control | 1 | 0 | 0 |
| G4_6 minus G1_3 MA-Control | 0 | 0 | 0 |

These results should be interpreted as preliminary MA group-comparison results
from the current MNE-Python implementation.

## Methodological Pipeline Alignment

This project was developed with reference to an existing MATLAB/nirs-toolbox
pipeline. The Python pipeline now includes two important alignment steps:

- short-separation regressors at the first-level GLM stage
- long-HbO-only filtering for group-level channel statistics

The Python and MATLAB results are not expected to be numerically identical at
this stage. Important remaining differences include MATLAB AR-IRLS estimation,
MATLAB mixed-effects group modeling, and possible HRF/model implementation
differences. A separate validation step is documented to compare MATLAB and
MNE-Python preprocessed HbO/HbR time series before interpreting differences
between MATLAB and Python statistical outputs.

See:

- `docs/matlab_python_alignment.md`
- `docs/preprocessing_validation_plan.md`

## Repository Structure

```text
config/      Configuration templates
data/        Local data folder; raw data are not uploaded to GitHub
docs/        Pipeline notes and reproducibility summaries
notebooks/   Jupyter notebooks for demonstration and reporting
scripts/     Python and MATLAB helper scripts for the analysis pipeline
results/     Local output tables; ignored by Git
figures/     Aggregate output figures for the report and slides
report/      Written report drafts
slides/      Final presentation slides
```

## Reproduce the Python Pipeline

Create or activate the environment:

```bash
conda env create -f environment.yml
conda activate brainhack-fnirs
```

Run the data-loading check:

```bash
python scripts/load_data.py --root-dir "/path/to/local/Anyalysis/group"
```

Run preprocessing:

```bash
python scripts/preprocess_fnirs.py \
  --root-dir "/path/to/local/Anyalysis/group" \
  --overwrite
```

Run first-level GLM:

```bash
python scripts/first_level_glm.py
```

Run group-level MA analysis:

```bash
python scripts/group_analysis.py
```

Create aggregate MA result figures:

```bash
python scripts/visualization.py
```

After exporting MATLAB preprocessed data, run the validation check:

```bash
python scripts/validate_matlab_mne_preprocessing.py
```

## Main Documentation

- `docs/data_loading_summary.md`
- `docs/preprocessing_summary.md`
- `docs/first_level_glm_summary.md`
- `docs/group_level_summary.md`
- `docs/matlab_python_alignment.md`
- `docs/preprocessing_validation_plan.md`
- `report/final_report_draft.md`

## Data Availability

The original fNIRS data and participant-level derivatives are not shared in
this repository because they contain data from child participants and may
include sensitive information. The repository is designed so that the analysis
logic can be reviewed without uploading private data.
