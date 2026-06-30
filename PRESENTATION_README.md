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

**Use the figures to show two things:**

- The MNE-Python pipeline can produce complete group-level outputs.
- The current results should be interpreted together with the validation
  evidence, because Python and MATLAB are not numerically identical.

**Main figures:**

- `figures/ma_mixed_effects_group_significance_counts.png`
- `figures/ma_mixed_effects_top_channel_pvalues.png`
- `figures/ma_mixed_effects_topographic_maps.png`

**How to explain the figures:**

- These figures show the group-level `MA-Control` comparison between `G1_3`
  and `G4_6`.
- The topographic map visualizes channel-level fNIRS patterns, not structural
  MRI activation.
- Because the MATLAB and Python preprocessing outputs differ, these maps are
  presented as MNE-Python pipeline outputs rather than exact reproductions of
  the MATLAB results.

## MATLAB-vs-MNE Validation

**Main validation question:**

Where might the result differences between MATLAB/nirs-toolbox and MNE-Python
come from?

**Evidence source:**

- These evidence points come from a custom validation script written for this
  project: `scripts/validate_matlab_mne_preprocessing.py`.
- The script compares MATLAB/nirs-toolbox preprocessing outputs with
  MNE-Python preprocessing outputs.
- It is not an official MNE validation function.
- It uses standard numerical checks, including time-grid comparison,
  `np.array_equal`, `np.allclose`, maximum absolute difference, MAE, RMSE, and
  correlation.
- The aggregate results are documented in
  `docs/preprocessing_validation_results.md`.

**Evidence 1: time alignment**

- MATLAB time appears to be in seconds, not milliseconds.
- Absolute time points do not fully match between MATLAB and Python.
- Relative time points align after removing the starting-time offset.
- No subject had identical MATLAB/Python time-grid length.
- This suggests the difference is more likely related to crop/trim boundaries
  or starting-time handling, not a simple seconds-vs-milliseconds issue.

**Evidence 2: numerical equivalence**

- Channels passing exact equality: `0`.
- Channels passing current unit-aware `allclose`: `0`.
- This means the current Python preprocessing output is not numerically
  equivalent to the MATLAB preprocessing output.

**Evidence 3: signal shape**

- Sample-index-aligned median correlation: `0.993`.
- This suggests many signals have similar shapes.
- But correlation is not enough to prove equivalence, because it can hide
  timing and scale differences.

## Interpretation

**Most likely sources of MATLAB-vs-MNE differences:**

- Crop/trim boundary handling.
- Starting-time offset handling.
- Unit or scale conventions.
- Toolbox-specific preprocessing defaults.

**What the validation supports:**

- The difference is probably not just a time-unit problem.
- The Python and MATLAB signals can be shape-similar but still not numerically
  equivalent.
- The MNE-Python pipeline should be presented as a transparent reconstruction,
  not a strict numerical copy of the MATLAB/nirs-toolbox pipeline.

**How to frame the current results:**

- The scientific goal remains the developmental comparison during MA
  processing.
- The methodological finding is that rebuilding the pipeline in MNE-Python
  reveals cross-tool differences that need to be documented.
- Therefore, the current group results are useful, but should be interpreted as
  MNE-Python outputs with known validation limitations.

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
