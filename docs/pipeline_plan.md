# Pipeline Plan

The project pipeline is organized around the main research question:

```text
Do lower-grade and upper-grade children show different fNIRS brain activation
patterns during morphological awareness processing?
```

The main task contrast is:

```text
MA - Control
```

The main group contrast is:

```text
(G4_6 MA - G4_6 Control) - (G1_3 MA - G1_3 Control)
```

## Analysis Stages

1. Load local SNIRF files and validate event markers.
2. Preprocess fNIRS data with MNE-Python.
3. Run subject-level GLM with MNE-NIRS.
4. Estimate each participant's `MA-Control` contrast.
5. Run group-level long-HbO channel comparisons.
6. Run a MATLAB-like mixed-effects group model for long-HbO MA contrasts.
7. Generate aggregate figures for the report and slides.
8. Generate aggregate fNIRS topographic brain maps.
9. Validate MATLAB-vs-MNE preprocessing outputs after MATLAB export.

## Main Scripts

| Stage | Script |
| --- | --- |
| Data loading | `scripts/load_data.py` |
| Preprocessing | `scripts/preprocess_fnirs.py` |
| First-level GLM | `scripts/first_level_glm.py` |
| Group analysis | `scripts/group_analysis.py` |
| Mixed-effects group analysis | `scripts/group_mixed_effects.py` |
| Visualization | `scripts/visualization.py` |
| Topographic brain maps | `scripts/plot_brain_maps.py` |
| MATLAB export | `scripts/export_matlab_preprocessed_for_validation.m` |
| MATLAB-vs-MNE validation | `scripts/validate_matlab_mne_preprocessing.py` |

## Current Status

The Python MA analysis pipeline is implemented and has been run on the local
dataset. MATLAB-vs-MNE preprocessing validation has also been completed
locally. The validation found that the current MNE-Python preprocessing is not
a strict numerical replication of the MATLAB/nirs-toolbox preprocessing, so the
MATLAB comparison is treated as a methodological limitation rather than as the
main scientific result.
