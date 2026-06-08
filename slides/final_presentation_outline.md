# Final Presentation Outline

Generated PPTX:

```text
slides/final_presentation.pptx
```

Regenerate with:

```bash
python scripts/create_final_presentation.py
```

## Slide 1: Title

MA-Related fNIRS Brain Activation Differences Between Lower- and Upper-Grade Children

Subtitle: A Python-based fNIRS analysis pipeline using MNE-Python, developed
with reference to a MATLAB/nirs-toolbox workflow.

## Slide 2: Motivation

- Morphological awareness is important for children's language and reading
  development.
- fNIRS can measure task-related cortical hemodynamic responses in child
  participants.
- The project asks whether lower- and upper-grade children show different
  MA-related activation patterns.

## Slide 3: Research Question

Do lower-grade and upper-grade children show different fNIRS brain activation
patterns during morphological awareness processing?

Primary contrast:

```text
(G4_6 MA - G4_6 Control) - (G1_3 MA - G1_3 Control)
```

## Slide 4: Data

- Local SNIRF fNIRS dataset from child participants.
- Groups:
  - `G1_3`: 59 participants
  - `G4_6`: 72 participants
  - Total: 131 participants
- Event mapping:
  - `1` = `MA`
  - `2` = `PA`
  - `3` = `Control`
- Raw data are not uploaded to GitHub because they contain child-participant
  data.

## Slide 5: New Skills and Tools

- Learned MNE-Python and MNE-NIRS for fNIRS analysis.
- Loaded SNIRF files in Python.
- Built a script-based preprocessing and GLM workflow.
- Compared Python steps with an existing MATLAB/nirs-toolbox pipeline.

## Slide 6: Python Pipeline

1. SNIRF loading and event validation.
2. Resampling to 2 Hz.
3. Optical-density conversion.
4. Beer-Lambert HbO/HbR conversion.
5. Task-window trimming.
6. First-level GLM with short-separation regressors.
7. Group-level long-HbO MA contrast analysis.
8. MATLAB-like mixed-effects group analysis.
9. Aggregate visualization.

## Slide 7: MATLAB-to-Python Alignment

- MATLAB pipeline used as a methodological reference.
- Python pipeline added:
  - short-separation regressors
  - long-HbO-only group analysis
  - mixed-effects group model
- Remaining differences:
  - MATLAB AR-IRLS vs Python `ar1`
  - MATLAB and Python mixed-effects solver/default differences
  - possible HRF/model differences

## Slide 8: Result Summary

- All 131 SNIRF files were loaded and preprocessed successfully.
- All 131 participants completed first-level GLM.
- Current Python group-level long-HbO results did not identify corrected
  significant channels.
- Simple t-test uncorrected channel counts:
  - G1_3 MA-Control: 2
  - G4_6 MA-Control: 1
  - G4_6 minus G1_3 MA-Control: 0
- Mixed-effects uncorrected channel counts:
  - G1_3 MA-Control: 1
  - G4_6 MA-Control: 2
  - G4_6 minus G1_3 MA-Control: 0

## Slide 9: Result Figures

Suggested figures:

- `figures/ma_group_significance_counts.png`
- `figures/ma_top_channel_pvalues.png`
- `figures/ma_mixed_effects_group_significance_counts.png`
- `figures/ma_mixed_effects_top_channel_pvalues.png`

Main message: current Python results are preliminary and should be interpreted
with correction and model-difference caveats.

## Slide 10: Mixed-Effects Result Figures

Suggested figures:

- `figures/ma_mixed_effects_group_significance_counts.png`
- `figures/ma_mixed_effects_top_channel_pvalues.png`

Main message: the MATLAB-like mixed-effects model also did not identify
corrected significant long-HbO channels.

## Slide 11: Open Science and Privacy

- Code, documentation, and aggregate figures are shared.
- Raw data and participant-level derivatives are not uploaded.
- `.gitignore` excludes raw data formats, subject information, local results,
  and validation exports.
- The pipeline is script-based so the analysis order can be followed and rerun.

## Slide 12: Limitations

- Python and MATLAB statistical outputs are not yet numerically identical.
- MATLAB preprocessing export still needs to be run for time-series validation.
- Python mixed-effects group analysis was added, but solver/default differences
  may remain.
- Results should be treated as exploratory until validation and model alignment
  are completed.

## Slide 13: Next Steps

- Run MATLAB preprocessing export.
- Validate MATLAB vs MNE-Python preprocessed HbO/HbR time series.
- Compare simple t-test and mixed-effects results in the final presentation.
- Finalize website report/notebook and slides.
- Polish final presentation delivery.
