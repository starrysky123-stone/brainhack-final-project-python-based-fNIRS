# MATLAB vs MNE Preprocessing Validation Plan

This validation step supports the main MA analysis by checking whether the
MNE-Python preprocessing output is numerically reasonable compared with the
existing MATLAB/nirs-toolbox preprocessing pipeline.

The goal is not to force MATLAB and Python to produce identical statistical
results. The goal is to verify that the preprocessed HbO/HbR time series are
reasonably aligned before interpreting MA-related GLM results.

## Current Status

The MATLAB export and Python validation have been completed locally. Following
TA feedback, the validation was refined so interpolation is no longer the
primary validation criterion. The script now diagnoses temporal alignment first
and then performs sample-index-aligned, unit-aware array comparisons. After
dropping one duplicate MATLAB manifest row, the validation compared 131 subjects
and 10,480 channel-level HbO/HbR time series.

Summary:

| Metric | Value |
| --- | ---: |
| MATLAB manifest rows / duplicate subject rows | 132 / 1 |
| Subjects with same number of time points | 0 |
| Subjects with close common time points | 14 |
| Median max absolute time difference | 21.0 s |
| Maximum absolute time difference | 481.5 s |
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

The validation does not support strict numerical equivalence between the
current MNE-Python preprocessing and the MATLAB/nirs-toolbox preprocessing.
Instead, it shows temporal-grid differences, no exact or current unit-aware
array closeness, and a large amplitude/unit scale difference.

For exact step-by-step commands and interpretation guidance, see:

```text
docs/matlab_validation_runbook.md
```

## Export MATLAB Preprocessed Data

Run this script in MATLAB with nirs-toolbox on the path:

```matlab
scripts/export_matlab_preprocessed_for_validation.m
```

It reruns the MATLAB preprocessing pipeline:

1. Load raw data with `nirs.io.loadDirectory`.
2. Rename stimulus channels to `MA`, `PA`, and `Control`.
3. Exclude files with incomplete `MA` or `Control` markers.
4. Label short-separation channels.
5. Resample to 2 Hz.
6. Convert to optical density.
7. Apply Beer-Lambert law.
8. Trim baseline with 5 seconds before and after task timing.
9. Export each participant's HbO/HbR time series to CSV.

The exported files should be local only:

```text
validation/matlab_preprocessed/
```

Do not upload these CSV files to GitHub.

## Run Python Validation

After MATLAB export, run:

```bash
conda activate brainhack-fnirs
python scripts/validate_matlab_mne_preprocessing.py
```

The Python script compares MATLAB CSV files against:

```text
derivatives/preprocessed/<group>/<subject>/<subject>_hbo_hbr_raw.fif
```

## Validation Metrics

The script computes channel-wise:

- time-grid alignment diagnostics
- `np.array_equal`
- unit-aware `np.allclose`
- maximum absolute difference
- correlation
- mean absolute error (MAE)
- root mean squared error (RMSE)
- mean and standard deviation in both pipelines
- Python/MATLAB standard-deviation ratio
- interpolated metrics as secondary diagnostics only
- fitted MATLAB/Python scale factor as an exploratory diagnostic only

The validation outputs are saved locally:

```text
results/matlab_mne_preprocessing_validation.csv
results/matlab_mne_preprocessing_validation_summary.csv
```

These files are ignored by Git because they contain subject-level derived data.
