# MEEN 305 Final Project

This repo is organized around the active continuous beam-design workflow.

## Structure

- [scripts](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/scripts)
  Python analysis, optimization, and export tools.
- [docs](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/docs)
  Project notes, reports, and reference material.
- [designs/active_runs](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/active_runs)
  Active optimization runs and their generated reports/plots.
- [designs/model_exports](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/model_exports)
  Generated mesh exports and previews.
- [designs/packages](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/packages)
  Packaged per-design deliverables.
- [archive/deprecated_assets](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/archive/deprecated_assets)
  Older exploratory or superseded assets kept for reference.

## Active Design Set

- [continuous_uniform_load_case_1](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_load_case_1)
- [continuous_uniform_load_case_2](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_load_case_2)
- [continuous_uniform_both_load_cases](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases)

The best overview note is [active_continuous_design_summary.md](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/docs/notes/active_continuous_design_summary.md).

## Common Commands

Run the solver:

```powershell
python scripts/beam_solver.py
```

Run the optimizer:

```powershell
python scripts/optimize_beam.py --output-dir designs/active_runs/optimization_run
```

Generate 3D exports:

```powershell
python scripts/beam_3d_models.py --write-dxf
```
