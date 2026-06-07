# fNIRS Preprocessing Summary

This document summarizes the first MNE-Python preprocessing pass for the local
SNIRF fNIRS dataset. Preprocessed data are stored locally under `derivatives/`
and are not uploaded to GitHub.

## Pipeline Steps

The preprocessing script follows the key preprocessing steps from the original
MATLAB/nirs-toolbox pipeline and implements them with MNE-Python:

1. Load SNIRF raw intensity data with `mne.io.read_raw_snirf`.
2. Rename events:
   - `1` = `MA`
   - `2` = `PA`
   - `3` = `Control`
3. Resample data to 2 Hz.
4. Convert raw intensity to optical density.
5. Convert optical density to HbO/HbR with the modified Beer-Lambert law.
6. Trim the recording to the task window with 5 seconds before the first event
   and 5 seconds after the last event.

## Batch Preprocessing Result

| Group | Number of subjects |
| --- | ---: |
| G1_3 | 59 |
| G4_6 | 72 |
| Total | 131 |

All 131 local SNIRF files were successfully preprocessed.

## Output

The script writes local preprocessed files to:

```text
derivatives/preprocessed/<group>/<subject>/<subject>_hbo_hbr_raw.fif
```

The derivative folder is ignored by Git because these files are derived from
private participant data.

## Quality-Control Notes

- All subjects retained complete `MA` and `Control` event markers after
  preprocessing.
- Each subject had 16 short-distance channel candidates using a 0.01 m
  source-detector distance threshold.
- One subject had 17 `PA` events rather than 16. This does not affect the
  current MA-only analysis, but it should be revisited before PA analyses.
- Thirteen subjects produced the MNE warning `Negative intensities encountered.
  Setting to abs(x)` during optical-density conversion. These subjects were
  still preprocessed successfully, but this should be reported as a QC caveat
  and considered before final statistical interpretation.

## Reproduce This Step

```bash
conda activate brainhack-fnirs
python scripts/preprocess_fnirs.py \
  --root-dir "/path/to/local/dyslexia_project/Anyalysis/group" \
  --overwrite
```

The script writes a local per-subject preprocessing table to:

```text
results/preprocessing_summary.csv
```

The CSV output is ignored by Git because it contains per-subject file-level
information.
