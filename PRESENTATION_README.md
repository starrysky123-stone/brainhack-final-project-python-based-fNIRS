# Presentation Notes

## Project Focus

**Dataset focus:**

This project uses fNIRS data from a child language-development dataset.

**Participant focus:**

For this project, I only use data from typically developing children. The
participants are divided into two age-related reading-development groups:
lower-grade children and upper-grade children.

**Main analysis focus:**

The analysis asks whether lower-grade and upper-grade typically developing
children show different fNIRS brain activation patterns during morphological
awareness processing.

**Pipeline focus:**

The main technical goal is to build a transparent MNE-Python fNIRS pipeline and
apply it to MA-related developmental group analysis.

Because the original analysis workflow was written in MATLAB/nirs-toolbox, this
project also focuses on rebuilding the analysis pipeline in Python and asking
whether pipelines built with different tools produce different results, and
where those differences may come from.

## Research Question

**Question to say clearly:**

Do lower-grade and upper-grade children show different fNIRS brain activation
patterns during morphological awareness processing?

**Groups:**

| Group | Participants |
| --- | ---: |
| Grades 1-3, `G1_3` | 59 |
| Grades 4-6, `G4_6` | 72 |
| Total | 131 |

**Main contrast:**

```text
MA - Control
```

**Group contrast:**

```text
(G4_6 MA-Control) - (G1_3 MA-Control)
```

## Why This Project

**Key points:**

- The dataset comes from a child language-development fNIRS study.
- This project focuses only on typically developing children.
- The scientific comparison is between lower-grade and upper-grade children.
- Original lab workflow: MATLAB/nirs-toolbox.
- Final project workflow: Python with MNE-Python/MNE-NIRS.
- The project emphasizes rebuilding the analysis toolchain and documenting
  cross-tool differences.

**Useful phrase:**

My project has two connected goals: first, to apply fNIRS analysis to a
developmental MA question in typically developing children; second, to rebuild
the original MATLAB/nirs-toolbox workflow in MNE-Python and examine whether
tool-specific pipeline differences affect the results.

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

**Main result statement:**

The Python pipeline successfully processed all 131 participants and generated
group-level statistics, aggregate figures, and fNIRS topographic maps.

**Statistical result:**

- Analysis focused on 32 long-distance HbO channels.
- No channel survived FDR or Bonferroni correction.
- Current group-level findings should be interpreted as exploratory.

**Useful phrase:**

The current statistical evidence for group differences is not strong after
correction, but the pipeline runs end to end and produces reproducible outputs.

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
