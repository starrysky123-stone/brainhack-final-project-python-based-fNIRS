# GitHub Submission Audit

This audit checks whether the repository is ready to be pushed to GitHub for
the BrainHack final project.

## Remote Repository

The local Git remote is configured as:

```text
origin  https://github.com/starrysky123-stone/brainhack-final-project-python-based-fNIRS.git
```

## Privacy Check

The tracked file list was checked for private or participant-level file types:

```text
.snirf
.nirs
.mat
.csv
.xlsx
.pptx
.fif
```

No tracked files matched these private or local-export file types.

The tracked file list was also checked for private/local folders:

```text
data/
raw_data/
derivatives/
results/
validation/
```

No tracked files were found inside these folders.

## Ignored Local Files

The following local paths are ignored by Git and should remain local:

```text
.DS_Store
data/
derivatives/
final_presentation.pptx
results/
scripts/__pycache__/
slides/final_presentation.pptx
validation/
```

This is expected. These paths may contain private data, participant-level
derivatives, local result tables, or local presentation exports.

## Tracked Public Materials

The repository currently tracks:

- analysis scripts in `scripts/`
- environment files: `environment.yml`, `requirements.txt`
- documentation in `docs/`
- aggregate figures in `figures/`
- report files in `report/`
- notebook placeholders/demonstrations in `notebooks/`
- slide outline in `slides/final_presentation_outline.md`

## Current GitHub Readiness

| Item | Status |
| --- | --- |
| README present | Ready |
| Analysis scripts present | Ready |
| Report page present | Ready |
| Aggregate figures present | Ready |
| Slide outline present | Ready |
| Mixed-effects group script present | Ready |
| Topographic brain maps present | Ready |
| Raw data excluded | Ready |
| Subject-level results excluded | Ready |
| PPTX exports excluded | Ready |
| MATLAB validation result | Completed locally and documented |

## Remaining Before Final Submission

1. Review `slides/final_presentation.pptx` visually in PowerPoint or Keynote.
2. Push commits to GitHub after one final privacy check.
3. Polish the final presentation delivery.
