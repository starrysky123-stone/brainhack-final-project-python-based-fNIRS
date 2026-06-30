# Presentation Notes

## Project Focus

- Analyze child language-development data using fNIRS.
- Use only the typically developing children dataset.
  - Research question: Do lower-grade and upper-grade children show different
    fNIRS brain activation patterns during morphological awareness processing?
  - Groups:

    | Group | Participants |
    | --- | ---: |
    | Grades 1-3, `G1_3` | 59 |
    | Grades 4-6, `G4_6` | 72 |
    | Total | 131 |

  - Main contrast:

    ```text
    MA - Control
    ```

  - Group contrast:

    ```text
    (G4_6 MA-Control) - (G1_3 MA-Control)
    ```

- Rebuild the original MATLAB-based fNIRS analysis pipeline using MNE-Python.

**Purpose:**

- Observe whether the MATLAB-based and MNE-Python-based pipelines produce
  different results.
- Explore where those differences may come from.

**MATLAB-based pipeline repo:**

[starrysky123-stone/fnirs-ma-brainhack-final-project](https://github.com/starrysky123-stone/fnirs-ma-brainhack-final-project)

## Python Pipeline

**Pipeline steps:**

```text
SNIRF loading
-> event renaming
-> resampling
-> optical-density conversion
-> Beer-Lambert Law
-> task-window trimming
-> first-level GLM
-> group-level analysis
-> topographic maps
```

**Scripts to mention if needed:**

| Step | Script |
| --- | --- |
| Data loading | `scripts/load_data.py` |
| Preprocessing | `scripts/preprocess_fnirs.py` |
| First-level GLM | `scripts/first_level_glm.py` |
| Group analysis | `scripts/group_analysis.py` |
| Mixed-effects model | `scripts/group_mixed_effects.py` |
| Brain maps | `scripts/plot_brain_maps.py` |
| MATLAB-MNE validation | `scripts/validate_matlab_mne_preprocessing.py` |

## Current Results

- The MNE-Python pipeline runs end-to-end.
- It processed 131 typically developing children.
- Outputs include:
  - `MA-Control` contrast estimates
  - group-level statistical summaries
  - fNIRS topographic maps
- Python results are not numerically identical to MATLAB/nirs-toolbox results.
- Possible reasons:
  - preprocessing details
  - time alignment
  - unit scaling
  - toolbox-specific default settings

## Figures to Show

**Group-level result figures:**

- `figures/ma_group_significance_counts.png`
- `figures/ma_top_channel_pvalues.png`
- `figures/ma_mixed_effects_group_significance_counts.png`
- `figures/ma_mixed_effects_top_channel_pvalues.png`

**Topographic brain map:**

- `figures/ma_mixed_effects_topographic_maps.png`

**Brain-map note:**

The topographic maps were generated with MNE-Python's official
`mne.viz.plot_topomap` function. They are fNIRS channel-level topographic maps
based on the measured optode montage, not structural MRI activation maps.

## MATLAB-vs-MNE Validation

**Why validation was needed:**

The original workflow was written in MATLAB/nirs-toolbox, so the Python output
was compared with MATLAB preprocessing output to understand cross-platform
differences.

**Validation logic after TA feedback:**

- Check temporal alignment first.
- Avoid using interpolation as the main validation criterion.
- Compare arrays with:
  - `np.array_equal`
  - unit-aware `np.allclose`
  - maximum absolute difference
  - MAE
  - RMSE
- Treat correlation as a shape diagnostic only.

**Aggregate validation findings:**

| Item | Result |
| --- | ---: |
| Subjects compared | 131 |
| Channel-level comparisons | 10,480 |
| Channels passing exact equality | 0 |
| Channels passing current unit-aware `allclose` | 0 |
| Python/MATLAB standard-deviation ratio | 1.67e-08 |

**Timing finding:**

- MATLAB time appears to be in seconds, not milliseconds.
- Relative time grids align after removing the starting-time offset.
- MATLAB and Python still retain different numbers of samples after trimming.
- This suggests a crop/trim boundary difference.

## Interpretation

**Main interpretation:**

The Python pipeline is a transparent MNE-Python implementation inspired by the
MATLAB workflow, not a strict numerical replication of the MATLAB pipeline.

**Limitations:**

- Group-level results are exploratory.
- MATLAB and Python preprocessing outputs are not numerically equivalent.
- Remaining differences likely involve crop/trim boundaries and unit/scale
  conventions.

## Take-Home Message

**Final point to leave with the audience:**

This project produced a reproducible MNE-Python fNIRS pipeline for MA-related
developmental group analysis and documented unresolved MATLAB-vs-MNE timing and
unit/scale discrepancies as methodological limitations.

## Useful Links

- Main Python repository: [starrysky123-stone/brainhack-final-project-python-based-fNIRS](https://github.com/starrysky123-stone/brainhack-final-project-python-based-fNIRS)
- MATLAB reference workflow: [starrysky123-stone/fnirs-ma-brainhack-final-project](https://github.com/starrysky123-stone/fnirs-ma-brainhack-final-project)
- Validation results: [`docs/preprocessing_validation_results.md`](docs/preprocessing_validation_results.md)
- Brain-map method: [`docs/topographic_brain_map_method.md`](docs/topographic_brain_map_method.md)
