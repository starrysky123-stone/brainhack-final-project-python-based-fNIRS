# BrainHack Final Project: MA-Related fNIRS Brain Activation Differences

For the 5-minute presentation script, see
[`PRESENTATION_README.md`](PRESENTATION_README.md).

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

## Related Repository

The original MATLAB/nirs-toolbox workflow used as the methodological reference
for this project is available here:

- [starrysky123-stone/fnirs-ma-brainhack-final-project](https://github.com/starrysky123-stone/fnirs-ma-brainhack-final-project)

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
7. Run a MATLAB-like mixed-effects group model for long-HbO MA contrasts.
8. Validate MATLAB/nirs-toolbox and MNE-Python preprocessing outputs as a
   method check.
9. Diagnose MATLAB/MNE time-grid differences stage by stage.
10. Generate aggregate fNIRS topographic maps for the MA results.

## New Skills and Open Science

This final project focuses on learning and applying MNE-Python and MNE-NIRS for
fNIRS data analysis. The new technical components include SNIRF loading in
Python, fNIRS preprocessing, subject-level GLM analysis, group-level MA
contrast testing, aggregate visualization, and MATLAB-to-MNE preprocessing
validation.

The repository is organized for open and reproducible analysis while protecting
participant privacy. Code, documentation, and aggregate figures are included;
raw data, subject information, local derivatives, and participant-level result
tables are excluded from Git.

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

## Topographic Brain Maps

The project includes aggregate fNIRS topographic maps generated from the
Python mixed-effects `MA-Control` estimates. The plotting script is project
specific, but the core visualization function is the official MNE-Python
`mne.viz.plot_topomap` function:

```text
https://mne.tools/stable/generated/mne.viz.plot_topomap.html
```

The maps use the long-distance HbO channel montage stored in the preprocessed
FIF files and visualize 32 channel-level mixed-effects estimates. They should
be interpreted as fNIRS optode/channel topographic maps, not structural MRI
activation maps.

See `docs/topographic_brain_map_method.md` for the detailed plotting method.

## Methodological Pipeline Alignment

This project was developed with reference to an existing MATLAB/nirs-toolbox
pipeline. The Python pipeline now includes two important alignment steps:

- short-separation regressors at the first-level GLM stage
- long-HbO-only filtering for group-level channel statistics

The Python and MATLAB results are not numerically identical. Following TA
feedback, the local preprocessing validation now separates temporal alignment
from numerical value comparison instead of using interpolation as the primary
validation criterion. The refined validation compared 131 subjects and 10,480
channel-level HbO/HbR time series after dropping one duplicate MATLAB manifest
row. No subjects had identical time-grid lengths, and only 14 subjects had
common time points that were close under the current tolerance. No channel was
exactly equal or unit-aware `allclose` under the current default tolerances.
The sample-index-aligned median correlation was 0.993, but this is interpreted
only as a shape diagnostic. The median Python/MATLAB standard-deviation ratio
was 1.67e-08, indicating a major unit/scale mismatch. Therefore, the current
Python pipeline should be interpreted as a transparent MNE-Python
implementation inspired by the MATLAB workflow, not as a strict numerical
replication of the MATLAB/nirs-toolbox pipeline.

Following later feedback, the validation also checks whether MATLAB time values
appear to be in seconds or milliseconds, whether relative time grids align after
removing the starting-time offset, and whether time-grid length differences
exceed one sample. The current aggregate results suggest MATLAB times are in
seconds and relative time grids align, but MATLAB and Python retain different
numbers of samples after trimming, indicating a remaining crop/trim boundary
difference.

Important remaining differences include MATLAB AR-IRLS estimation, possible
HRF/model implementation differences, and solver/default differences in the
mixed-effects group model.

See:

- `docs/matlab_python_alignment.md`
- `docs/matlab_mne_function_mapping.md`
- `docs/matlab_validation_runbook.md`
- `docs/preprocessing_validation_plan.md`
- `docs/preprocessing_validation_results.md`
- `docs/ta_feedback_response.md`

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

Run MATLAB-like mixed-effects group analysis:

```bash
python scripts/group_mixed_effects.py
```

Create aggregate MA result figures:

```bash
python scripts/visualization.py
python scripts/visualization.py \
  --stats results/group_level_mixed_effects_channel_stats_ssreg_long_hbo.csv \
  --summary results/group_level_mixed_effects_summary_ssreg_long_hbo.csv \
  --output-prefix ma_mixed_effects \
  --figure-title "MA-Control Mixed-Effects Long-HbO"
python scripts/plot_brain_maps.py
```

Run optional time-grid diagnostics:

```bash
python scripts/python_time_grid_diagnostics.py --root-dir "/path/to/local/Anyalysis/group"
```

The corresponding MATLAB diagnostic script is:

```text
scripts/export_matlab_time_grid_diagnostics.m
```

Create the final presentation deck:

```bash
python scripts/create_final_presentation.py
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
- `docs/mixed_effects_group_summary.md`
- `docs/matlab_python_alignment.md`
- `docs/matlab_mne_function_mapping.md`
- `docs/matlab_validation_runbook.md`
- `docs/preprocessing_validation_plan.md`
- `docs/ta_feedback_response.md`
- `docs/topographic_brain_map_method.md`
- `docs/ten_minute_presentation_plan.md`
- `docs/final_project_requirements_checklist.md`
- `docs/github_submission_audit.md`
- `docs/reproducibility_smoke_test.md`
- `report/index.md`
- `report/final_report_draft.md`
- `slides/final_presentation_outline.md`

The PowerPoint deck generated by `scripts/create_final_presentation.py` is kept
as a local export and is ignored by Git.

## Data Availability

The original fNIRS data and participant-level derivatives are not shared in
this repository because they contain data from child participants and may
include sensitive information. The repository is designed so that the analysis
logic can be reviewed without uploading private data.
