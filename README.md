# MEEN 305 Final Project

This repo is organized around the active continuous beam-design workflow for the
MEEN 305 beam project.

## Current Setup

- Project-correct geometry is a `9.0 in` total beam with supports at `x = 0.5 in`
  and `x = 8.5 in`.
- The support span remains `8.0 in`.
- Load locations are still measured from support A in the project equations, but
  the solver and optimizer now track the full `0 to 9 in` beam coordinate.

## DIR

```text
MEEN-305-FINAL/
|-- README.md
|-- requirements.txt
|-- scripts/
|   |-- beam_solver.py
|   |-- optimize_beam.py
|   |-- beam_3d_models.py
|   `-- diagram_assets.py
|-- docs/
|   |-- notes/
|   |   |-- active_continuous_design_summary.md
|   |   |-- current_design_selection.md
|   |   |-- analysis_accountability_map.md
|   |   `-- beam_length_support_correction_audit.md
|   |-- references/
|   |   `-- project_reference_materials/
|   `-- reports/
|       `-- final_project_report.tex
|-- designs/
|   |-- active_runs/
|   |   |-- continuous_uniform_load_case_1/
|   |   |-- continuous_uniform_load_case_2/
|   |   |-- continuous_uniform_both_load_cases/
|   |   `-- continuous_uniform_both_load_cases_9in_corrected/
|   |-- model_exports/
|   `-- packages/
|-- Instructions_References/
`-- archive/
    `-- deprecated_assets/
```

## Folder Definitions

- [scripts](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/scripts): source-of-truth analysis, optimization, export, and diagram code.
- [docs/notes](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/docs/notes): working notes, design decisions, and correction audits.
- [docs/references/project_reference_materials](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/docs/references/project_reference_materials): project handout, equations sheets, and supporting reference material.
- [docs/reports](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/docs/reports): report deliverables, including the large final report source.
- [designs/active_runs](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs): generated optimization runs and their reports/plots.
- [designs/model_exports](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/model_exports): exported mesh files, previews, and manifest readmes.
- [designs/packages](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/packages): presentation-ready per-design bundles.
- [Instructions_References](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/Instructions_References): prompt fragments and correction instructions collected during the project.
- [archive/deprecated_assets](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/archive/deprecated_assets): superseded runs, legacy exports, and older exploratory work retained for reference.

## Active Reference Files

- [active_continuous_design_summary.md](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/docs/notes/active_continuous_design_summary.md)
- [current_design_selection.md](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/docs/notes/current_design_selection.md)
- [beam_length_support_correction_audit.md](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/docs/notes/beam_length_support_correction_audit.md)

## Common Commands

Run the solver:

```powershell
python scripts/beam_solver.py --total-length-in 9.0 --span-in 8.0 --support-a-x-in 0.5 --support-b-x-in 8.5
```

Run the corrected optimizer into a named folder:

```powershell
python scripts/optimize_beam.py --output-dir designs/active_runs/continuous_uniform_both_load_cases_9in_corrected --total-length-in 9.0 --span-in 8.0 --support-a-x-in 0.5 --support-b-x-in 8.5
```

Generate 3D exports:

```powershell
python scripts/beam_3d_models.py --write-dxf
```
