# Ten-Minute Final Presentation Plan

This plan is designed for a 10-minute BrainHack final presentation. The goal is
to keep the introduction short and focus on methods, results, and what was
learned from building the MNE-Python pipeline.

## One-Sentence Project Statement

Hi, I am Yu-Ting Wu. This project builds and documents a Python-based fNIRS
analysis pipeline using MNE-Python/MNE-NIRS to compare MA-related brain
activation between lower-grade children, Grades 1-3, and upper-grade children,
Grades 4-6.

## Suggested Time Allocation

| Section | Time | Main message |
| --- | ---: | --- |
| Opening and research question | 0:00-0:45 | This is an fNIRS pipeline project focused on developmental differences in MA-related activation. |
| Data and task contrast | 0:45-1:30 | 131 typically developing children; G1_3 vs G4_6; main contrast is MA-Control. |
| Python pipeline | 1:30-4:00 | Explain the MNE-Python steps from SNIRF loading to preprocessing, GLM, group analysis, and topographic maps. |
| MATLAB-to-Python alignment | 4:00-5:30 | Explain why MATLAB was used as a reference and what was matched or not matched. |
| Results | 5:30-7:45 | No corrected significant long-HbO channels; show exploratory p-value results and topographic maps. |
| Validation and limitation | 7:45-9:15 | MATLAB-vs-MNE preprocessing validation found scale and waveform differences; Python is not a strict MATLAB replica. |
| Take-home message | 9:15-10:00 | The deliverable is a transparent, reproducible MNE-Python fNIRS pipeline for MA analysis, with limitations documented. |

## Recommended Storyline

### 1. Opening

Use only a short introduction. The audience already heard the pitch, so the
presentation should quickly remind them what the project is about.

Suggested wording:

```text
Hi, I am Yu-Ting Wu. My final project is about building a Python-based fNIRS
analysis pipeline using MNE-Python. The scientific question is whether
lower-grade and upper-grade children show different brain activation patterns
during a morphological awareness task.
```

### 2. Data and Research Question

Mention the group structure and the main contrast.

Key points:

- Data: fNIRS data from 131 typically developing children.
- Groups: Grades 1-3 and Grades 4-6.
- Main task contrast: `MA - Control`.
- Main group contrast: `(G4_6 MA-Control) - (G1_3 MA-Control)`.
- Raw data are private child-participant data and are not uploaded to GitHub.

### 3. Methods: Python Pipeline

This should be the longest part of the talk.

Explain the pipeline in order:

1. Load SNIRF files with MNE-Python.
2. Rename event markers to `MA`, `PA`, and `Control`.
3. Resample to 2 Hz.
4. Convert intensity to optical density.
5. Convert optical density to HbO/HbR with Beer-Lambert law.
6. Trim the task window.
7. Run first-level GLM with short-separation regressors.
8. Run group-level long-HbO analyses.
9. Generate aggregate figures and fNIRS topographic maps.

Suggested wording:

```text
The main technical contribution is that I translated the original workflow
into a script-based MNE-Python pipeline. The pipeline now runs from raw SNIRF
loading through preprocessing, first-level GLM, group-level analysis, and
visualization.
```

### 4. MATLAB-to-Python Alignment

Frame MATLAB as a reference workflow, not as a second final result.

Key message:

```text
I had an existing MATLAB/nirs-toolbox pipeline, so I used it as a reference for
building the Python pipeline. I separated two questions: first, whether there
is an MNE-Python equivalent for each MATLAB step; second, whether theoretically
similar functions produce numerically similar outputs.
```

Important distinction:

- Function mapping: mostly solved for preprocessing.
- Numerical equivalence: not fully supported by the validation.
- Main non-equivalent statistical step: MATLAB AR-IRLS versus Python `ar1`.

### 5. Results

Keep the interpretation cautious.

Key results:

- 131/131 subjects loaded and preprocessed.
- First-level GLM completed for 131/131 subjects.
- Group-level analysis focused on 32 long-distance HbO channels.
- No channel survived FDR or Bonferroni correction.
- Exploratory uncorrected effects were present in a small number of channels.
- Topographic maps visualize the mixed-effects MA-Control estimates.

Suggested wording:

```text
The current Python analysis did not find corrected significant long-HbO
channels. So I would treat the group comparison as exploratory. However, the
pipeline itself is working end to end, and it produces aggregate statistical
figures and topographic fNIRS maps.
```

### 6. Topographic Brain Map

Be precise about what the brain map is.

Suggested wording:

```text
The topographic maps were generated with MNE-Python's official
mne.viz.plot_topomap function. They show channel-level fNIRS topographic maps
based on the measured optode montage. They are not structural MRI activation
maps.
```

### 7. Validation and Limitations

This is the part that responds to the TA's feedback.

Key validation result:

- 131 subjects compared.
- 10,560 channel-level HbO/HbR time series compared.
- Median channel-wise correlation: 0.606.
- Median Python/MATLAB standard-deviation ratio: 1.67e-08.
- Median normalized RMSE after scale alignment: 0.793.

Interpretation:

```text
This means I should not claim that the Python preprocessing is numerically
equivalent to MATLAB. Instead, the Python pipeline should be presented as an
open and transparent MNE-Python implementation inspired by the MATLAB workflow.
The MATLAB comparison becomes a methodological validation and limitation.
```

### 8. Take-Home Message

End with a clear project deliverable.

Suggested wording:

```text
The main outcome of this final project is a reproducible MNE-Python fNIRS
pipeline for MA-related group analysis. The pipeline can load and preprocess
local SNIRF data, run first-level GLM, run group-level analysis, generate
figures and topographic maps, and document where it agrees or differs from the
original MATLAB workflow.
```

## If Asked About the Two GitHub Repositories

Suggested answer:

```text
The MATLAB repository contains my original lab workflow. The Python repository
is the final project submission. The Python version uses MNE-Python/MNE-NIRS
and is organized for open science, reproducibility, and privacy. The MATLAB
pipeline is used as a reference for method alignment, but the final project is
centered on the Python pipeline.
```

## What Not to Overemphasize

- Do not spend too much time on broad language-development theory.
- Do not present MATLAB and Python as if they should produce identical final
  brain maps.
- Do not claim corrected significant group differences, because the current
  Python results did not survive correction.
- Do not describe the topographic maps as MRI brain activation maps.

## Final 10-Second Closing

```text
Overall, this project helped me learn how to build an MNE-Python fNIRS
pipeline and apply it to a real developmental MA dataset. The current result is
exploratory, but the pipeline is reproducible and the MATLAB-Python differences
are explicitly documented.
```
