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

The current repository documents issue (1), and the validation scripts for
issue (2) have now been run locally after exporting MATLAB/nirs-toolbox
preprocessed data.

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
- MATLAB group-level analysis uses a mixed-effects model. A Python
  mixed-effects version has now been added, while the simpler channel-wise
  t-test analysis is retained as an exploratory comparison.
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

- temporal-alignment diagnostics
- `np.array_equal`
- unit-aware `np.allclose`
- maximum absolute difference
- mean absolute error
- root mean squared error
- mean and standard deviation comparison
- Python/MATLAB standard-deviation ratio
- interpolated metrics as secondary diagnostics only
- fitted MATLAB/Python scale factor as an exploratory diagnostic only

After TA feedback, I revised the validation so interpolation is no longer the
primary validation criterion. The refined validation first checks temporal
alignment and then performs sample-index-aligned, unit-aware array comparisons.
After dropping one duplicate MATLAB manifest row, the current validation
compared 131 subjects and 10,480 channel-level HbO/HbR time series. No subjects
had identical MATLAB/Python time-grid lengths, only 14 subjects had close
common time points, and no channel was exactly equal or unit-aware `allclose`
under the current default tolerances. The sample-index-aligned median
correlation was 0.993, while the interpolated median correlation was 0.602 as a
secondary diagnostic. The median Python/MATLAB standard-deviation ratio was
1.67e-08.

These results suggest that the current Python preprocessing is not a strict
numerical reproduction of the MATLAB/nirs-toolbox preprocessing. The overall
comparison indicates temporal-grid differences and a large amplitude/unit scale
difference. The high sample-index-aligned correlation is treated as a shape
diagnostic, not as proof of numerical equivalence.

## Current Status

| Item | Status |
| --- | --- |
| Python MNE-Python preprocessing pipeline | Implemented |
| First-level GLM with short-channel regressors | Implemented |
| Long-HbO MA group-level analysis | Implemented |
| MATLAB-like Python mixed-effects group analysis | Implemented |
| MATLAB-to-MNE function mapping | Documented |
| MATLAB export script for validation | Implemented |
| Python validation script | Implemented |
| Actual numerical MATLAB-vs-MNE validation | Completed locally |

## Suggested Reply

```text
Thank you, this distinction is very helpful. I agree that these are two
different issues. I have separated them in the project documentation.

For issue (1), I created a MATLAB/nirs-toolbox to MNE-Python function mapping.
Most preprocessing steps have direct or manually implemented MNE-Python
equivalents, such as SNIRF loading, stimulus renaming, event-count checking,
short-channel identification, resampling, optical-density conversion,
Beer-Lambert conversion, and task-window trimming. I also added a Python
mixed-effects group model to better approximate the MATLAB group-level model.
The part that is still not directly equivalent is mainly the first-level
MATLAB AR-IRLS model and possible solver/default differences.

For issue (2), I added a MATLAB export script and a Python validation script to
compare the MATLAB-preprocessed HbO/HbR time series with the MNE-Python
preprocessed FIF files. Your feedback helped me revise the validation logic:
instead of interpolating Python values onto MATLAB time points as the main
comparison, I now first report temporal alignment, then evaluate
sample-index-aligned `np.array_equal`, unit-aware `np.allclose`, and maximum
absolute differences. Interpolated correlation and fitted scaling are kept only
as secondary diagnostics. After dropping one duplicate MATLAB manifest row, the
refined validation compared 131 subjects and 10,480 channel-level comparisons.
Following your later point about time units and crop/resampling differences, I
also added diagnostics for whether the MATLAB time column appears to be seconds
or milliseconds, whether the arrays differ by more than one sample, and whether
relative time grids align after removing the starting-time offset. The current
results suggest that MATLAB time is in seconds and the relative time grid
aligns after removing the offset, but every subject still differs by more than
one retained sample after trimming. I also added stage-wise time-grid diagnostic
scripts for MATLAB and Python so the next check can locate whether divergence
starts at raw loading, resampling, or trimming. No channel passed exact equality
or the current unit-aware `allclose` tolerance. Therefore, I would not claim
that the current Python preprocessing is numerically equivalent to MATLAB.
Instead, I treat it as an MNE-Python implementation inspired by the MATLAB
workflow and document the temporal, crop/trim, and unit/scale discrepancies as
methodological limitations.

The main project focus remains the MA-related fNIRS activation comparison
between lower- and upper-grade children, while the MATLAB/MNE comparison is
used as a methodological validation step.
```
