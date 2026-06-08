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
results/matlab_mne_preprocessing_validation_summary.csv
```

These files are ignored by Git because they contain subject-level derived
results.

## How to Interpret the Validation Metrics

The validation summary reports:

| Metric | Meaning |
| --- | --- |
| `n_subjects` | Number of participants successfully compared |
| `n_channel_comparisons` | Number of channel-level MATLAB/Python comparisons |
| `median_correlation` | Overall time-series shape similarity |
| `min_correlation` | Worst channel-level correlation |
| `median_rmse` | Typical absolute numerical disagreement scale |
| `median_mae` | Typical absolute error |
| `median_std_ratio_python_over_matlab` | Whether Python and MATLAB signal amplitudes have similar variability |
| `median_fitted_scale_matlab_per_python` | Typical fitted scale factor needed to place Python signals on the MATLAB scale |
| `median_scaled_nrmse_by_matlab_std` | Typical residual error after linear scale alignment, normalized by MATLAB standard deviation |

High correlations would suggest that the preprocessing outputs are temporally
similar. RMSE/MAE and standard-deviation ratios help determine whether the
signals are also similar in scale.

## Current Local Validation Result

The MATLAB export and Python validation were completed locally. The validation
compared 131 subjects and 10,560 channel-level HbO/HbR time series.

Summary:

| Metric | Value |
| --- | ---: |
| Subjects compared | 131 |
| Channel-level comparisons | 10,560 |
| Median channel-wise correlation | 0.606 |
| Minimum channel-wise correlation | -0.810 |
| Median RMSE | 58.285 |
| Median MAE | 45.838 |
| Median Python/MATLAB standard-deviation ratio | 1.67e-08 |
| Median fitted MATLAB/Python scale factor | 3.79e+07 |
| Median normalized RMSE after scale alignment | 0.793 |

Interpretation:

The current Python preprocessing output is not numerically equivalent to the
MATLAB/nirs-toolbox preprocessing output. The validation shows a large
amplitude/unit scale difference and remaining waveform disagreement after
linear scale alignment. Therefore, the Python pipeline should be described as a
transparent MNE-Python implementation based on the MATLAB workflow, not as a
bitwise or numerically matched reproduction of the MATLAB pipeline.

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
