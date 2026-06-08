# Final Project Requirements Checklist

This checklist summarizes the course final-project requirements and maps them
to the current repository. It is based on the local course note PDF:
`腦數據分析final project注意事項.pdf`.

## Required Deliverables

| Requirement | Current repository status |
| --- | --- |
| GitHub repository with project code | Present: `scripts/` |
| Clear README | Present: `README.md` |
| Website report or notebook | In progress: `report/final_report_draft.md`, `notebooks/` |
| Slides | In progress: `slides/final_presentation_outline.md` |
| Recorded project video | Not stored in repository |
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
| Clear presentation | Slide outline added; final slides still needed |
| Data ethics and privacy | Raw data, subject-level results, and derived participant files are ignored by Git |

## Analysis Workflow Coverage

| Workflow step | Current file |
| --- | --- |
| Data loading | `scripts/load_data.py` |
| Preprocessing | `scripts/preprocess_fnirs.py` |
| First-level GLM | `scripts/first_level_glm.py` |
| Group-level analysis | `scripts/group_analysis.py` |
| Visualization | `scripts/visualization.py` |
| MATLAB preprocessing validation | `scripts/export_matlab_preprocessed_for_validation.m`, `scripts/validate_matlab_mne_preprocessing.py` |

## Remaining Tasks

1. Run MATLAB preprocessing export for validation if MATLAB/nirs-toolbox is
   available locally.
2. Run Python MATLAB-MNE preprocessing validation after export.
3. Turn the report draft into the final website report or notebook.
4. Create final presentation slides from the slide outline.
5. Record the project video outside the repository.
6. Push the repository to GitHub after confirming no private data are staged.
