# SNIRF Data Loading Summary

This document summarizes the first reproducibility check for the local fNIRS
dataset. Raw data are stored outside this public repository and are not uploaded
to GitHub.

## Input Data

- File format: SNIRF (`.snirf`)
- Loader: `mne.io.read_raw_snirf`
- Event mapping recovered from the original MATLAB pipeline:
  - `1` = `MA`
  - `2` = `PA`
  - `3` = `Control`

## Event Validation

The current MA-focused analysis requires complete `MA` and `Control` markers.
The expected number of events is:

- `MA`: 16 events
- `Control`: 16 events

## Batch Loading Result

The batch loading script successfully read all local SNIRF files under the
analysis group directory.

| Group | Number of subjects |
| --- | ---: |
| G1_3 | 59 |
| G4_6 | 72 |
| Total | 131 |

All subjects passed the MA/Control event-count check.

One subject had 17 `PA` events rather than 16. This does not block the current
MA-only analysis, but it should be noted if PA is included in later analyses.

## Reproduce This Check

Create or activate the analysis environment, then run:

```bash
conda activate brainhack-fnirs
python scripts/load_data.py --root-dir "/path/to/local/dyslexia_project/Anyalysis/group"
```

The script writes a local summary table to:

```text
results/snirf_file_summary.csv
```

The CSV output is ignored by Git because it contains per-subject file-level
information. This Markdown summary is intended as the shareable, non-sensitive
version for the public project repository.
