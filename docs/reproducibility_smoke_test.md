# Reproducibility Smoke Test

This document records a lightweight reproducibility check for the project code.
It does not rerun the full fNIRS analysis; instead, it verifies that the Python
scripts can be imported/compiled and that their command-line interfaces are
available in the project conda environment.

## Environment

The smoke test was run with:

```text
/Users/lisa/miniconda3/envs/brainhack-fnirs/bin/python
```

This corresponds to the local `brainhack-fnirs` conda environment.

## Python Compile Check

Command:

```bash
/Users/lisa/miniconda3/envs/brainhack-fnirs/bin/python -m py_compile \
  scripts/load_data.py \
  scripts/preprocess_fnirs.py \
  scripts/first_level_glm.py \
  scripts/group_analysis.py \
  scripts/group_mixed_effects.py \
  scripts/visualization.py \
  scripts/validate_matlab_mne_preprocessing.py \
  scripts/create_final_presentation.py
```

Result:

```text
passed
```

## CLI Help Check

Command:

```bash
for f in \
  scripts/load_data.py \
  scripts/preprocess_fnirs.py \
  scripts/first_level_glm.py \
  scripts/group_analysis.py \
  scripts/group_mixed_effects.py \
  scripts/visualization.py \
  scripts/validate_matlab_mne_preprocessing.py
do
  /Users/lisa/miniconda3/envs/brainhack-fnirs/bin/python "$f" --help >/dev/null
done
```

Result:

```text
passed
```

## Notes

Some scripts import MNE/MNE-NIRS, which triggers Matplotlib/fontconfig cache
warnings on this local machine:

```text
Matplotlib created a temporary cache directory...
Fontconfig error: No writable cache directories
```

These warnings did not prevent the scripts from compiling or exposing their
command-line help. When running analysis scripts interactively, setting
`MPLCONFIGDIR=/private/tmp` can reduce the Matplotlib cache warning.

## Privacy Check

The tracked file list was also checked for private data patterns:

```text
.snirf, .nirs, .mat, .csv, .xlsx, .pptx, .fif
data/, raw_data/, derivatives/, results/, validation/
```

No tracked files matched these patterns.
