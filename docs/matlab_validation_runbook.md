# MATLAB-to-MNE Preprocessing Validation Runbook

This runbook is the practical next step for addressing the TA's question:

> Have you validated that after preprocessing in MNE-Python, the data are still
> numerically close enough to the MATLAB-preprocessed version?

The validation focuses on preprocessing outputs, not on forcing the full GLM or
group-level statistical results to be identical.

## What This Validation Answers

This validation addresses issue (2):

```text
Functions that should theoretically perform the same preprocessing steps in
MNE-Python and MATLAB may still produce different numerical results.
```

It does not answer issue (1), which is function availability. Issue (1) is
covered separately in:

```text
docs/matlab_mne_function_mapping.md
```

## Before Running

Confirm these local requirements:

1. MATLAB is available on the local computer.
2. nirs-toolbox is added to the MATLAB path.
3. The local raw-data group folder exists:

```text
/Users/lisa/Desktop/dyslexia＿project/Anyalysis/group
```

4. The MNE-Python preprocessing outputs already exist:

```text
derivatives/preprocessed/<group>/<subject>/<subject>_hbo_hbr_raw.fif
```

## Step 1: Run the MATLAB Export

Open MATLAB and set the current folder to this repository:

```matlab
cd('/Users/lisa/Desktop/brainhack-final-project-python-based-fNIRS')
```

If nirs-toolbox is not already on the MATLAB path, add it first. The exact path
depends on where nirs-toolbox is installed locally. For example:

```matlab
addpath(genpath('/path/to/nirs-toolbox'))
```

Then run:

```matlab
run('scripts/export_matlab_preprocessed_for_validation.m')
```

When MATLAB asks for a folder, select:

```text
/Users/lisa/Desktop/dyslexia＿project/Anyalysis/group
```

The script reruns the MATLAB preprocessing steps:

1. Load data with `nirs.io.loadDirectory`.
2. Rename stimulus channels to `MA`, `PA`, and `Control`.
3. Exclude files with incomplete `MA` or `Control` markers.
4. Label short-separation channels.
5. Resample to 2 Hz.
6. Convert to optical density.
7. Apply Beer-Lambert law.
8. Trim task baseline with 5 seconds before and after task timing.
9. Export each participant's HbO/HbR time series to CSV.

## Expected MATLAB Output

After the export succeeds, this local folder should exist:

```text
validation/matlab_preprocessed/
```

It should contain:

```text
validation/matlab_preprocessed/manifest.csv
validation/matlab_preprocessed/<group>/<subject>/<subject>_matlab_hbo_hbr.csv
validation/matlab_preprocessed/<group>/<subject>/<subject>_matlab_channel_link.csv
```

These files contain participant-level derived data and must not be uploaded to
GitHub.

## Step 2: Run the Python Validation

Back in the terminal, from this repository:

```bash
conda activate brainhack-fnirs
python scripts/validate_matlab_mne_preprocessing.py
```

The script compares MATLAB-exported CSV time series against:

```text
derivatives/preprocessed/<group>/<subject>/<subject>_hbo_hbr_raw.fif
```

## Expected Python Output

The validation writes local result tables:

```text
results/matlab_mne_preprocessing_validation.csv
results/matlab_mne_preprocessing_time_alignment.csv
results/matlab_mne_preprocessing_validation_summary.csv
```

These files are ignored by Git because they contain subject-level derived
results.

## How to Interpret the Validation Metrics

The validation summary reports:

| Metric | Meaning |
| --- | --- |
| `manifest_n_rows` | Number of rows in the MATLAB export manifest before duplicate removal |
| `manifest_n_duplicate_subject_rows` | Duplicate `(group, subject)` manifest rows dropped before validation |
| `n_subjects` | Number of participants successfully compared |
| `n_channel_comparisons` | Number of channel-level MATLAB/Python comparisons |
| `n_subjects_same_n_times` | Number of participants with identical MATLAB/Python time-grid lengths |
| `n_subjects_length_diff_le_1` | Number of participants whose time-grid lengths differ by at most one sample |
| `n_subjects_time_allclose` | Number of participants whose common time points pass `np.allclose` |
| `n_subjects_relative_time_allclose` | Number of participants whose common relative time points pass `np.allclose` after removing the starting-time offset |
| `n_subjects_matlab_time_guess_seconds` | Number of participants whose MATLAB median time step matches Python seconds |
| `n_subjects_matlab_time_guess_milliseconds` | Number of participants whose MATLAB median time step appears to be milliseconds |
| `median_max_abs_time_diff_common` | Median maximum absolute time difference over common sample indices |
| `median_max_abs_relative_time_diff_common` | Median maximum relative-time difference after removing the starting-time offset |
| `n_array_equal` | Number of channel arrays passing exact `np.array_equal` |
| `n_allclose` | Number of channel arrays passing unit-aware `np.allclose` with current tolerances |
| `median_correlation` | Sample-index-aligned time-series shape similarity; diagnostic only |
| `min_correlation` | Worst sample-index-aligned channel correlation |
| `median_max_abs_diff` | Typical maximum absolute difference between aligned arrays |
| `median_rmse` | Typical absolute numerical disagreement scale |
| `median_mae` | Typical absolute error |
| `median_std_ratio_python_over_matlab` | Whether Python and MATLAB signal amplitudes have similar variability |
| `median_interpolated_correlation` | Secondary diagnostic after interpolating Python values to MATLAB time points |
| `median_exploratory_fitted_scale_matlab_per_python` | Exploratory scale diagnostic, not a validation criterion |

The primary validation criteria are the temporal-alignment fields,
`np.array_equal`, `np.allclose`, and absolute differences under an explicit unit
assumption. Correlation and fitted scaling are diagnostics only; they can
obscure time-grid or unit discrepancies.

## Current Local Validation Result

The MATLAB export and Python validation were completed locally. After dropping
one duplicate MATLAB manifest row, the validation compared 131 subjects and
10,480 channel-level HbO/HbR time series.

Summary:

| Metric | Value |
| --- | ---: |
| MATLAB manifest rows / duplicate subject rows | 132 / 1 |
| Subjects compared | 131 |
| Channel-level comparisons | 10,480 |
| Subjects with same number of time points | 0 |
| Subjects with length difference <= 1 sample | 0 |
| Subjects with close common time points | 14 |
| Subjects with close relative common time points | 131 |
| Subjects whose MATLAB time is guessed as seconds | 131 |
| Subjects whose MATLAB time is guessed as milliseconds | 0 |
| Median max absolute time difference | 21.0 s |
| Maximum absolute time difference | 481.5 s |
| Median max relative-time difference | 0.0 s |
| Maximum relative-time difference | 0.0 s |
| Channels exactly equal | 0 |
| Channels unit-aware `allclose` | 0 |
| Sample-index-aligned median correlation | 0.993 |
| Sample-index-aligned minimum correlation | -0.233 |
| Median maximum absolute difference | 205.317 |
| Median RMSE | 58.214 |
| Median MAE | 45.776 |
| Median Python/MATLAB standard-deviation ratio | 1.67e-08 |
| Interpolated median correlation, secondary diagnostic | 0.602 |
| Exploratory fitted MATLAB/Python scale factor | 5.95e+07 |

Interpretation:

The current Python preprocessing output is not numerically equivalent to the
MATLAB/nirs-toolbox preprocessing output. The refined validation suggests the
MATLAB time column is in seconds, not milliseconds. Absolute time points differ
mainly because MATLAB appears to preserve a nonzero starting-time offset after
trimming while the MNE-Python cropped output starts at 0 seconds. Relative time
points align across subjects, but the retained time-grid lengths still differ
by more than one sample for every subject, pointing to a remaining trim/crop
boundary difference. The validation also shows no exact or current unit-aware
array closeness and a large amplitude/unit scale difference. Therefore, the
Python pipeline should be described as a transparent MNE-Python implementation
based on the MATLAB workflow, not as a bitwise or numerically matched
reproduction of the MATLAB pipeline.

## Optional Stepwise Time-Grid Diagnostics

To diagnose where the MATLAB/Python time grids first diverge, export timing
metadata at each preprocessing stage.

In MATLAB:

```matlab
cd('/Users/lisa/Desktop/brainhack-final-project-python-based-fNIRS')
run('scripts/export_matlab_time_grid_diagnostics.m')
```

When MATLAB asks for the data folder, select:

```text
/Users/lisa/Desktop/dyslexia＿project/Anyalysis/group
```

In Python:

```bash
python scripts/python_time_grid_diagnostics.py \
  --root-dir "/Users/lisa/Desktop/dyslexia＿project/Anyalysis/group"
```

These scripts export timing metadata for:

```text
raw_loaded
stim_renamed
event_filtered
short_separation_labeled
resampled_2hz
optical_density
beer_lambert
trimmed
```

The outputs are local diagnostic tables:

```text
validation/matlab_time_grid_by_stage.csv
results/python_time_grid_by_stage.csv
```

They are intentionally not tracked by Git because they may include
participant-level timing metadata.

## Suggested Wording for the Report

If validation looks numerically close:

```text
The MNE-Python preprocessing outputs were compared with MATLAB/nirs-toolbox
preprocessed HbO/HbR time series. The validation showed high channel-wise
time-series similarity, supporting the use of the Python preprocessing pipeline
for the MA analysis. Remaining statistical differences are likely related to
GLM and group-level modeling differences rather than preprocessing failure.
```

If validation shows large discrepancies:

```text
The validation revealed that MNE-Python and MATLAB/nirs-toolbox preprocessing
outputs were not sufficiently close for direct numerical comparison. Therefore,
the current Python pipeline should be treated as a transparent MNE-Python
implementation inspired by the MATLAB workflow, rather than a numerical
replication. Further parameter and algorithm matching is needed before making
strong claims about equivalence.
```

## Output Location

The MATLAB export creates:

```text
validation/matlab_preprocessed/manifest.csv
```

The Python validation creates:

```text
results/matlab_mne_preprocessing_validation.csv
results/matlab_mne_preprocessing_validation_summary.csv
```

These files contain subject-level derived data and are intentionally ignored by
Git.
