# 5-Minute Presentation Guide

## Project Title

**Building an MNE-Python fNIRS Pipeline for MA-Related Brain Activation Analysis**

## 0:00-0:40 Opening

Hi, I am Yu-Ting Wu.

This project builds a Python-based fNIRS analysis pipeline using
MNE-Python and MNE-NIRS. The goal is to analyze morphological awareness,
or MA-related, brain activation in children and compare lower-grade children,
Grades 1-3, with upper-grade children, Grades 4-6.

The original workflow was written in MATLAB/nirs-toolbox, so this project also
uses the MATLAB workflow as a methodological reference.

## 0:40-1:20 Research Question and Data

The main research question is:

> Do lower-grade and upper-grade children show different fNIRS brain activation
> patterns during morphological awareness processing?

The dataset includes 131 typically developing children.

| Group | Participants |
| --- | ---: |
| Grades 1-3, `G1_3` | 59 |
| Grades 4-6, `G4_6` | 72 |
| Total | 131 |

The main task contrast is:

```text
MA - Control
```

The main group contrast is:

```text
(G4_6 MA-Control) - (G1_3 MA-Control)
```

Because the dataset contains private child-participant fNIRS data, raw data,
subject-level derivatives, and participant-level result tables are not uploaded
to GitHub.

## 1:20-2:30 Python / MNE Pipeline

The main technical contribution of this project is an end-to-end script-based
MNE-Python fNIRS pipeline.

The pipeline includes:

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

The Python pipeline uses MNE-Python to read local SNIRF files and MNE-NIRS to
run first-level GLM analysis. I also added short-separation regressors and a
MATLAB-like mixed-effects group model to better align the Python workflow with
the original MATLAB/nirs-toolbox workflow.

The original MATLAB reference repository is:

[starrysky123-stone/fnirs-ma-brainhack-final-project](https://github.com/starrysky123-stone/fnirs-ma-brainhack-final-project)

## 2:30-3:40 Current Results

The pipeline successfully loaded and preprocessed all 131 participants.

For the group-level Python analysis, I focused on 32 long-distance HbO
channels.

The current Python analysis did not find long-HbO channels that survived FDR or
Bonferroni correction. Therefore, I interpret the group-level result as
exploratory.

This does not mean the project failed. The main outcome is that the pipeline
successfully runs from local SNIRF files to preprocessing, first-level GLM,
group-level analysis, aggregate figures, and topographic maps.

## 3:40-4:30 Topographic fNIRS Maps

The project also generates aggregate fNIRS topographic maps.

The maps were generated using MNE-Python's official visualization function:

```text
mne.viz.plot_topomap
```

These are channel-level fNIRS topographic maps based on the measured optode
montage. They should not be interpreted as structural MRI activation maps.

The main topographic map figure is:

```text
figures/ma_mixed_effects_topographic_maps.png
```

## 4:30-5:00 MATLAB-vs-MNE Validation and Take-Home Message

Because the original workflow was written in MATLAB/nirs-toolbox, I also
validated the Python preprocessing output against the MATLAB preprocessing
output.

After TA feedback, the validation was revised so interpolation is not used as
the primary validation criterion. The script now first checks temporal
alignment, then compares arrays using exact equality, unit-aware `allclose`,
maximum absolute difference, MAE, and RMSE.

The main validation findings are:

| Validation item | Result |
| --- | ---: |
| Subjects compared | 131 |
| Channel-level comparisons | 10,480 |
| Channels passing exact equality | 0 |
| Channels passing current unit-aware `allclose` | 0 |
| Python/MATLAB standard-deviation ratio | 1.67e-08 |

The refined timing diagnostics suggest that MATLAB time is in seconds and that
relative time grids align after removing the starting-time offset. However,
MATLAB and Python still retain different numbers of samples after trimming.
This suggests a remaining crop or trim boundary difference.

The final take-home message is:

> This project does not claim that Python exactly reproduces MATLAB. Instead,
> it builds a transparent and reproducible MNE-Python fNIRS pipeline, applies it
> to MA-related developmental group analysis, and documents where the Python and
> MATLAB workflows diverge.

## One-Sentence Summary

This project built an end-to-end MNE-Python fNIRS pipeline for MA-related group
analysis, produced exploratory group-level and topographic results, and
documented unresolved MATLAB-vs-MNE timing and unit/scale discrepancies as
methodological limitations.

## Useful Links

- Main repository: [starrysky123-stone/brainhack-final-project-python-based-fNIRS](https://github.com/starrysky123-stone/brainhack-final-project-python-based-fNIRS)
- MATLAB reference workflow: [starrysky123-stone/fnirs-ma-brainhack-final-project](https://github.com/starrysky123-stone/fnirs-ma-brainhack-final-project)
- Validation results: [`docs/preprocessing_validation_results.md`](docs/preprocessing_validation_results.md)
- Topographic map method: [`docs/topographic_brain_map_method.md`](docs/topographic_brain_map_method.md)
