# BrainHack Final Project: Python-based fNIRS Analysis Pipeline

## Project title

Preliminary fNIRS Analysis Pipeline and Brain Activation Comparison 
Between Lower- and Upper-Grade Children During Language-Related Tasks

## Project overview

This project aims to build and document a Python-based fNIRS analysis 
pipeline for analyzing developmental differences in brain activation 
during language-related tasks.

The data come from typically developing children. Participants will be 
divided into two reading-development groups: lower-grade children, Grades 
1–3, and upper-grade children, Grades 4–6. The main goal is to compare 
brain activation patterns between these two developmental stages.

## Main research question

Can a Python-based fNIRS analysis pipeline be used to compare brain 
activation differences between lower- and upper-grade children during 
language-related tasks?

## Tools and references

This project will refer to the official MNE-Python and MNE-NIRS examples 
for building the fNIRS analysis workflow.

MNE-Python will be used as the main open-source neurophysiological data 
analysis framework. MNE-NIRS will be considered for fNIRS-specific 
processing, GLM analysis, and visualization.

Reference:

https://mne.tools/stable/index.html

## Planned analysis pipeline

The planned pipeline includes:

1. Load fNIRS data
2. Check stimulus markers and data quality
3. Preprocess fNIRS signals
4. Convert optical density to hemoglobin concentration
5. Run subject-level GLM
6. Run group-level comparison
7. Visualize significant channels and brain activation results
8. Export result tables and figures

## Repository structure

```text
config/      Configuration templates
data/        Local data folder; raw data are not uploaded to GitHub
docs/        Possible website report folder
notebooks/   Jupyter notebooks for project report and demonstration
scripts/     Python scripts for the fNIRS analysis pipeline
results/     Output tables; sensitive or large files are not uploaded
figures/     Output figures for the report and slides
report/      Written report or website report
slides/      Final presentation slides
## Data availability

The original fNIRS data are not publicly shared in this repository because 
they contain data from child participants and may include sensitive 
information.

Only code, documentation, example structure, and non-sensitive outputs 
will be included.

## Current status

This repository is currently under development for the BrainHack final 
project. The initial goal is to build a reproducible project structure and 
gradually implement the Python-based fNIRS analysis pipeline.
