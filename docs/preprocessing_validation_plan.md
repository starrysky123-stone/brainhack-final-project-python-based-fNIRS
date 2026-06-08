# MATLAB vs MNE Preprocessing Validation Plan

This validation step supports the main MA analysis by checking whether the
MNE-Python preprocessing output is numerically reasonable compared with the
existing MATLAB/nirs-toolbox preprocessing pipeline.

The goal is not to force MATLAB and Python to produce identical statistical
results. The goal is to verify that the preprocessed HbO/HbR time series are
reasonably aligned before interpreting MA-related GLM results.

## Current Status

The local MATLAB result files mainly contain GLM and group-level outputs
(`SubjStats`, `GroupStats`, and contrast tables). I did not find a saved
`hb_trim` or equivalent preprocessed time-series file that Python can directly
read.

Because MATLAB is not available in the current Codex environment, the next step
requires running an export script inside MATLAB on the local machine.

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

- correlation
- mean absolute error (MAE)
- root mean squared error (RMSE)
- mean and standard deviation in both pipelines
- Python/MATLAB standard-deviation ratio

The validation outputs are saved locally:

```text
results/matlab_mne_preprocessing_validation.csv
results/matlab_mne_preprocessing_validation_summary.csv
```

These files are ignored by Git because they contain subject-level derived data.
