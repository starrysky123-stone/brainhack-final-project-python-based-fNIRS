# Final Project Requirements Checklist

This checklist summarizes the course final-project requirements and maps them
to the current repository. It is based on the local course note PDF:
`腦數據分析final project注意事項.pdf`.

## Required Deliverables

| Requirement | Current repository status |
| --- | --- |
| GitHub repository with project code | Present: `scripts/` |
| Clear README | Present: `README.md` |
| Website report or notebook | Present: `report/index.md`, `report/final_report_draft.md`, `notebooks/` |
| Slides | Present: `slides/final_presentation_outline.md`, `slides/final_presentation.pptx` |
| Analysis figures | Present: `figures/` |

## README Requirements

| README item | Current status |
| --- | --- |
| Project topic | Present |
| Data description | Present, with privacy note |
| Main analysis content | Present |
| How to run the code | Present |
| Repository structure | Present |

## Evaluation Criteria

| Criterion | Current implementation |
| --- | --- |
| Brain data analysis relevance | fNIRS analysis of MA-related activation |
| New skill or technique | MNE-Python/MNE-NIRS fNIRS pipeline construction |
| Open science | Public code and transparent analysis steps |
| Reproducibility | Script-based data loading, preprocessing, GLM, group analysis, and visualization |
| Clear code/notebooks | Scripts are organized by analysis stage |
| Clear presentation | Slide outline and first PPTX deck added |
| Data ethics and privacy | Raw data, subject-level results, and derived participant files are ignored by Git |
| Reproducibility smoke test | `docs/reproducibility_smoke_test.md` |

## Analysis Workflow Coverage

| Workflow step | Current file |
| --- | --- |
| Data loading | `scripts/load_data.py` |
| Preprocessing | `scripts/preprocess_fnirs.py` |
| First-level GLM | `scripts/first_level_glm.py` |
| Group-level analysis | `scripts/group_analysis.py` |
| Mixed-effects group analysis | `scripts/group_mixed_effects.py` |
| Visualization | `scripts/visualization.py` |
| MATLAB preprocessing validation | `scripts/export_matlab_preprocessed_for_validation.m`, `scripts/validate_matlab_mne_preprocessing.py` |
| MATLAB-to-MNE function mapping | `docs/matlab_mne_function_mapping.md` |
| MATLAB validation runbook | `docs/matlab_validation_runbook.md` |

## Remaining Tasks

1. Review and polish `slides/final_presentation.pptx` in PowerPoint or Keynote.
2. If time permits, investigate likely sources of the MATLAB-vs-MNE scale and
   waveform differences.
3. Push any final code/documentation commits to GitHub after confirming no
   private data are staged.
