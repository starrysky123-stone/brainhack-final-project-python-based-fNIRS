# MATLAB and Python Pipeline Alignment Notes

This document records the changes made after comparing the initial MNE-Python
results with the existing MATLAB/nirs-toolbox results.

## Why the Initial Results Differed

The first Python implementation was a valid MNE-Python pipeline, but it was not
a one-to-one reproduction of the MATLAB pipeline. The largest differences were:

- MATLAB used `firstlevelglm.AddShortSepRegressors = true`.
- MATLAB used `AR-IRLS` at the first level, while Python used MNE-NIRS `ar1`.
- MATLAB used a group-level mixed-effects model:
  `beta ~ -1 + Group:cond + (1|Subject)`.
- The initial Python group-level test used channel-wise t-tests on subject
  `MA-Control` contrasts.
- MATLAB's final corrected table focused on 32 long-distance HbO channels,
  while the initial Python analysis included 40 channels for HbO and HbR.

## Python Revisions Made

The Python pipeline was revised to better match the MATLAB analysis:

1. Added short-separation channel regressors to the first-level GLM.
   - Each participant contributed 16 short-channel nuisance regressors.
   - The regressors are standardized and added to the first-level design matrix.
2. Added long-HbO-only filtering to the group-level script.
   - The script reads the preprocessed FIF files and identifies long HbO
     channels using MNE-NIRS.
   - Group analysis is restricted to 32 long-distance HbO channels.
3. Wrote revised local output tables with `ssreg` in the filename.

## Revised Python Results

The revised first-level GLM completed successfully for all 131 participants.

| Group | Number of subjects |
| --- | ---: |
| G1_3 | 59 |
| G4_6 | 72 |
| Total | 131 |

Revised group-level long-HbO results:

| Comparison | Channels | Uncorrected p < .05 | FDR significant | Bonferroni significant |
| --- | ---: | ---: | ---: | ---: |
| G1_3 MA-Control | 32 | 2 | 0 | 0 |
| G4_6 MA-Control | 32 | 1 | 0 | 0 |
| G4_6 minus G1_3 MA-Control | 32 | 0 | 0 | 0 |

## Remaining Differences

Even after these revisions, the Python results still do not match the MATLAB
FWE-significant channel pattern. The remaining likely causes are:

- MATLAB uses AR-IRLS, which is not the same as MNE-NIRS `ar1`.
- MATLAB uses a mixed-effects group model, while the current Python group-level
  script uses channel-wise t-tests.
- The exact MATLAB canonical HRF implementation may differ from MNE's `glover`
  model.
- The MATLAB contrast output labels should be checked because some saved CSV
  filenames and `cond` labels appear to point to different group contrasts.

These differences should be reported as limitations if the final project
compares MATLAB and Python outputs.
