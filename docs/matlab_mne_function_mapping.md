# MATLAB/nirs-toolbox to MNE-Python Function Mapping

This document addresses two different questions raised during project feedback:

1. Does a MATLAB/nirs-toolbox processing function have a corresponding
   MNE-Python or MNE-NIRS function?
2. If MATLAB and Python functions are intended to perform the same step, do
   they produce numerically similar outputs?

These are related but separate issues. The first issue is about library
coverage and function mapping. The second issue is about numerical validation,
default parameters, and algorithmic differences.

## Issue 1: Function Availability and Mapping

The table below maps the original MATLAB/nirs-toolbox workflow to the current
Python implementation.

| Analysis stage | MATLAB/nirs-toolbox function | Current Python implementation | Mapping status |
| --- | --- | --- | --- |
| Load raw files | `nirs.io.loadDirectory` | `mne.io.read_raw_snirf` | Direct equivalent for SNIRF loading |
| Rename stimulus labels | `nirs.modules.RenameStims` | `raw.annotations.rename` through `rename_annotations()` | Equivalent behavior, implemented with MNE annotations |
| Check event completeness | custom MATLAB loop over `raw(i).stimulus` | `scripts/load_data.py` annotation/event-count checks | Equivalent logic, custom implementation |
| Label short channels | `nirs.modules.LabelShortSeperation` | `mne_nirs.channels.get_short_channels` | Equivalent channel-identification concept |
| Resample | `nirs.modules.Resample`, `Fs = 2` | `raw.resample(2)` | Direct equivalent concept; numerical method may differ |
| Optical density | `nirs.modules.OpticalDensity` | `mne.preprocessing.nirs.optical_density` | Direct equivalent concept; numerical validation needed |
| Beer-Lambert law | `nirs.modules.BeerLambertLaw` | `mne.preprocessing.nirs.beer_lambert_law` | Direct equivalent concept; parameter/default validation needed |
| Trim baseline/task window | `nirs.modules.TrimBaseline` | `trim_to_task_window()` in `scripts/preprocess_fnirs.py` | No single MNE module; custom implementation using MNE crop |
| First-level GLM | `nirs.modules.GLM` | `mne_nirs.statistics.run_glm` | Equivalent analysis stage, but model options differ |
| First-level noise model | `firstlevelglm.type = 'AR-IRLS'` | `noise_model = 'ar1'` | Not currently equivalent |
| Short-separation regressors in GLM | `firstlevelglm.AddShortSepRegressors = true` | short-channel data added through `add_regs` | Equivalent concept, manually implemented |
| HRF basis | `nirs.design.basis.Canonical`, `peakTime = 6` | `hrf_model = 'glover'` | Similar canonical-HRF goal, not guaranteed identical |
| Group model | `nirs.modules.MixedEffects` | `scripts/group_mixed_effects.py` using statsmodels MixedLM | Approximate equivalent; solver/default validation needed |
| MATLAB contrast test | `GroupStats.ttest(c)` | one-sample/Welch t-tests on first-level `MA-Control` contrasts | Related contrast goal, different statistical model |
| 3D brain plotting | custom `plot3Dbrain_Ver2021_Li` | aggregate channel-count and p-value figures | Not equivalent; current Python figures are summary figures |

## Current Interpretation of Issue 1

The current project has found or implemented MNE-Python equivalents for the
major preprocessing steps:

- SNIRF loading
- stimulus annotation renaming
- event-count validation
- short-channel identification
- resampling
- optical-density conversion
- Beer-Lambert HbO/HbR conversion
- task-window trimming

The main steps that are not yet direct equivalents are statistical/modeling
steps rather than basic preprocessing steps:

- MATLAB `AR-IRLS` first-level GLM is not currently reproduced by the Python
  `ar1` model.
- MATLAB mixed-effects group analysis is approximated with statsmodels MixedLM,
  but exact numerical equivalence has not been validated.
- MATLAB 3D brain plotting uses custom lab code and coordinates that are not
  currently reproduced in Python.

## Issue 2: Numerical Agreement Between Matched Steps

Even when MATLAB and Python have functions for the same conceptual step, the
outputs may differ because of defaults or implementation details.

Potential sources of discrepancy include:

- resampling method and anti-alias filtering
- treatment of negative or zero intensities during optical-density conversion
- Beer-Lambert pathlength factor and wavelength handling
- channel ordering and channel-name conventions
- short-separation channel threshold and regressor standardization
- HRF basis implementation
- GLM solver and noise model
- trimming/cropping boundary behavior

For this reason, function mapping alone is not enough. The project also needs
numerical validation of the preprocessed HbO/HbR time series.

## Validation Plan

The repository includes two scripts for this validation:

1. `scripts/export_matlab_preprocessed_for_validation.m`
   - Run inside MATLAB with nirs-toolbox.
   - Exports MATLAB-preprocessed HbO/HbR time series to local CSV files.
2. `scripts/validate_matlab_mne_preprocessing.py`
   - Runs in Python after MATLAB export.
   - Compares MATLAB CSV time series with MNE-Python FIF files.

The validation metrics are:

- temporal-alignment diagnostics
- exact `np.array_equal`
- unit-aware `np.allclose`
- maximum absolute difference
- mean absolute error
- root mean squared error
- mean and standard deviation in each pipeline
- Python/MATLAB standard-deviation ratio
- sample-index-aligned correlation as a shape diagnostic
- interpolated correlation as a secondary diagnostic only
- fitted MATLAB/Python scale factor as an exploratory diagnostic only

## Current Project Status

At this point, the project can address both feedback issues, but they are at
different stages:

| Feedback issue | Current status |
| --- | --- |
| Function mapping | Mostly documented; this file records the current mapping and gaps |
| Numerical validation | Completed locally and refined after TA feedback |

## Current Validation Result

After exporting the MATLAB/nirs-toolbox preprocessed HbO/HbR time series, the
Python validation was revised to avoid treating interpolation/correlation as
the primary validation criterion. It now first checks temporal alignment and
then evaluates exact equality, unit-aware closeness, and absolute differences.
After dropping one duplicate MATLAB manifest row, the refined validation
compared 131 subjects and 10,480 channel-level time series.

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
| Median Python/MATLAB standard-deviation ratio | 1.67e-08 |
| Interpolated median correlation, secondary diagnostic | 0.602 |
| Exploratory fitted MATLAB/Python scale factor | 5.95e+07 |

This indicates that the current MNE-Python preprocessing is not a strict
numerical replication of the MATLAB/nirs-toolbox preprocessing. The refined
validation suggests MATLAB time is in seconds and relative time grids align
after removing the starting-time offset, but the retained number of samples
still differs by more than one sample for every subject. It also shows no exact
or current unit-aware array closeness and a large amplitude/unit scale
difference. The high sample-index-aligned correlation is useful as a shape
diagnostic, but it is not evidence of numerical equivalence.

The MA activation comparison can still be presented as an MNE-Python analysis
pipeline inspired by the MATLAB workflow. However, the report should not claim
that the Python preprocessing is numerically equivalent to MATLAB. The numerical
validation is best treated as a methodological finding and limitation.
