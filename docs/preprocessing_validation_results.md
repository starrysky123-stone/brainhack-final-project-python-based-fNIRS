# MATLAB-vs-MNE Preprocessing Validation Results

This document reports the aggregate output of:

```bash
python scripts/validate_matlab_mne_preprocessing.py
```

The full validation CSV files are intentionally not tracked by Git because they
contain subject-level derived results:

```text
results/matlab_mne_preprocessing_validation.csv
results/matlab_mne_preprocessing_time_alignment.csv
results/matlab_mne_preprocessing_validation_summary.csv
```

Only the aggregate summary is reported here.

## Validation Logic

After TA feedback, the validation script was revised so interpolation is not
used as the primary validation criterion.

The refined validation does the following:

1. Checks MATLAB/Python temporal alignment first.
2. Drops duplicate MATLAB manifest rows by `(group, subject)`.
3. Compares sample-index-aligned arrays.
4. Reports exact `np.array_equal`.
5. Reports unit-aware `np.allclose` with explicit tolerances.
6. Reports maximum absolute difference, MAE, and RMSE.
7. Reports correlation only as a shape diagnostic.
8. Reports interpolated correlation and fitted scale only as secondary or
   exploratory diagnostics.

## Aggregate Results

| Metric | Value |
| --- | ---: |
| MATLAB manifest rows | 132 |
| Duplicate MATLAB subject rows dropped | 1 |
| Subjects compared | 131 |
| Channel-level comparisons | 10,480 |
| Subjects with identical MATLAB/Python time-grid length | 0 |
| Subjects with close common time points | 14 |
| Median maximum absolute time difference over common indices | 21.0 s |
| Maximum absolute time difference over common indices | 481.5 s |
| Channels passing exact `np.array_equal` | 0 |
| Channels passing current unit-aware `np.allclose` | 0 |
| Sample-index-aligned median correlation | 0.992879 |
| Sample-index-aligned minimum correlation | -0.232606 |
| Median maximum absolute difference | 205.316976 |
| Median RMSE | 58.214452 |
| Median MAE | 45.775663 |
| Median Python/MATLAB standard-deviation ratio | 1.667799e-08 |
| Interpolated median correlation, secondary diagnostic | 0.602226 |
| Exploratory fitted MATLAB/Python scale factor | 5.951696e+07 |

## Interpretation

The validation does not support strict numerical equivalence between the
current MNE-Python preprocessing output and the MATLAB/nirs-toolbox
preprocessing output.

The main unresolved discrepancies are:

1. **Temporal alignment**: no subject had identical MATLAB/Python time-grid
   lengths, and only 14 subjects had close common time points.
2. **Numerical closeness**: no channel passed exact equality or the current
   unit-aware `allclose` check.
3. **Unit/scale**: the Python/MATLAB standard-deviation ratio was approximately
   `1.67e-08`, indicating a large scale mismatch.

The high sample-index-aligned median correlation suggests that many signals
have similar shape when compared by sample order. However, correlation is not
evidence of numerical equivalence because it can obscure temporal and unit/scale
differences.

Therefore, the Python pipeline should be presented as a transparent
MNE-Python/MNE-NIRS implementation inspired by the MATLAB workflow, not as a
strict numerical replication of the MATLAB/nirs-toolbox pipeline.
