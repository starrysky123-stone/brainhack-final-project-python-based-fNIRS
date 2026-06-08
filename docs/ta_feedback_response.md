# Response to TA Feedback on MATLAB and MNE-Python Differences

This note summarizes how the project addresses the two separate issues raised
in feedback about MATLAB/nirs-toolbox and MNE-Python preprocessing.

## Short Response

Yes, the current project can address both issues, but they require different
checks.

Issue (1) is a function-mapping question:

```text
Does a MATLAB/nirs-toolbox preprocessing function have a corresponding
MNE-Python or MNE-NIRS function?
```

Issue (2) is a numerical-validation question:

```text
When MATLAB and MNE-Python functions are intended to perform the same
preprocessing step, do they produce similar preprocessed HbO/HbR time series?
```

The current repository documents issue (1) and prepares the validation scripts
for issue (2). The remaining blocking step is to run the MATLAB export script
locally, because the Codex environment does not have MATLAB/nirs-toolbox.

## Issue (1): Function Availability

This issue is not mainly about parameters or algorithm settings. It asks
whether the needed function exists in MNE-Python/MNE-NIRS, or whether the
pipeline must implement the behavior manually.

The current project found or implemented MNE-Python equivalents for the major
preprocessing steps:

| MATLAB/nirs-toolbox step | Python/MNE implementation |
| --- | --- |
| `nirs.io.loadDirectory` | `mne.io.read_raw_snirf` |
| `nirs.modules.RenameStims` | MNE annotation renaming |
| MA/Control event-count check | custom Python check in `scripts/load_data.py` |
| `nirs.modules.LabelShortSeperation` | `mne_nirs.channels.get_short_channels` |
| `nirs.modules.Resample` | `raw.resample(2)` |
| `nirs.modules.OpticalDensity` | `mne.preprocessing.nirs.optical_density` |
| `nirs.modules.BeerLambertLaw` | `mne.preprocessing.nirs.beer_lambert_law` |
| `nirs.modules.TrimBaseline` | custom MNE `raw.crop()` implementation |

The detailed function mapping is documented in:

```text
docs/matlab_mne_function_mapping.md
```

The main remaining non-equivalent parts are modeling/statistics steps rather
than basic preprocessing steps:

- MATLAB first-level GLM uses `AR-IRLS`; the current Python model uses `ar1`.
- MATLAB group-level analysis uses a mixed-effects model; the current Python
  group-level analysis uses channel-wise t-tests on subject-level contrasts.
- MATLAB 3D plotting uses custom lab plotting code; the current Python figures
  are aggregate summary figures.

## Issue (2): Numerical Differences Between Matched Steps

This issue is about whether theoretically corresponding steps actually produce
similar numerical outputs. Differences could come from default parameters or
implementation details.

Plausible sources include:

- resampling and anti-alias filtering details
- treatment of negative or zero intensities
- Beer-Lambert pathlength and wavelength handling
- channel ordering and naming
- short-channel threshold and regressor standardization
- HRF basis differences
- GLM solver and noise model differences
- trimming boundary behavior

To address this, the repository includes:

```text
scripts/export_matlab_preprocessed_for_validation.m
scripts/validate_matlab_mne_preprocessing.py
docs/matlab_validation_runbook.md
```

The validation compares MATLAB-exported preprocessed HbO/HbR CSV files with the
MNE-Python preprocessed FIF files using:

- channel-wise correlation
- mean absolute error
- root mean squared error
- mean and standard deviation comparison
- Python/MATLAB standard-deviation ratio

## Current Status

| Item | Status |
| --- | --- |
| Python MNE-Python preprocessing pipeline | Implemented |
| First-level GLM with short-channel regressors | Implemented |
| Long-HbO MA group-level analysis | Implemented |
| MATLAB-to-MNE function mapping | Documented |
| MATLAB export script for validation | Implemented |
| Python validation script | Implemented |
| Actual numerical MATLAB-vs-MNE validation | Pending MATLAB export |

The current blocking file is:

```text
validation/matlab_preprocessed/manifest.csv
```

This file will be created only after running the MATLAB export script locally.

## Suggested Reply

```text
Thank you, this distinction is very helpful. I agree that these are two
different issues. I have separated them in the project documentation.

For issue (1), I created a MATLAB/nirs-toolbox to MNE-Python function mapping.
Most preprocessing steps have direct or manually implemented MNE-Python
equivalents, such as SNIRF loading, stimulus renaming, event-count checking,
short-channel identification, resampling, optical-density conversion,
Beer-Lambert conversion, and task-window trimming. The parts that are not yet
direct equivalents are mainly modeling/statistical steps, especially MATLAB
AR-IRLS and the MATLAB mixed-effects group model.

For issue (2), I added a MATLAB export script and a Python validation script to
compare the MATLAB-preprocessed HbO/HbR time series with the MNE-Python
preprocessed FIF files. The validation will summarize channel-wise correlation,
MAE, RMSE, and standard-deviation ratios. This validation is ready, but I still
need to run the MATLAB export locally because MATLAB/nirs-toolbox is not
available in the current coding environment.

The main project focus remains the MA-related fNIRS activation comparison
between lower- and upper-grade children, while the MATLAB/MNE comparison is
used as a methodological validation step.
```
