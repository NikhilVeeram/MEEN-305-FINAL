# Current Design Selection

This note identifies the active design candidates in the reorganized project
layout and recommends which one to present or fabricate next.

## Recommended Presentation Design

Use `continuous_uniform_both_load_cases` as the main final design candidate.

Why this is the best overall choice:

- It is continuous and closed throughout, with no discontinuous cutouts.
- It is symmetric left-to-right.
- It was optimized to balance both project load directions together.
- It keeps the governing minimum factor of safety close to the `1.5` target.
- It remains lighter than the more conservative Load Case 1-focused design.

Key metrics:

- Weight: `0.03752 lbf`
- Governing minimum FoS: `1.526`
- Governing load case: `Load Case 2`
- Governing location: `x = 5.000 in`
- Maximum deflection: `0.12629 in`

## Lightest Active Continuous Design

If the only priority is minimum weight among the active continuous designs, use
`continuous_uniform_load_case_2`.

Key metrics:

- Weight: `0.03568 lbf`
- Governing minimum FoS: `1.543`
- Maximum deflection: `0.12117 in`

## Where the Active Files Live

### Recommended balanced design

- Run folder: [continuous_uniform_both_load_cases](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases)
- Summary report: [optimization_report.md](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases/optimization_report.md)
- LaTeX report: [optimization_report.tex](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases/optimization_report.tex)
- Best-design data: [best_design.json](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases/best_design.json)
- Full design trail: [design_study.csv](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases/design_study.csv)
- Variable map: [beam_parameter_map.png](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases/beam_parameter_map.png)

### Balanced design plots

- Geometry properties: [geometry_properties.png](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases/best_design/geometry_properties.png)
- Outer dimensions: [outer_dimension_views.png](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases/best_design/outer_dimension_views.png)
- Load Case 1 plots: [load_case_1_results.png](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases/best_design/load_case_1_results.png)
- Load Case 2 plots: [load_case_2_results.png](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases/best_design/load_case_2_results.png)

## Deliverables

The packaged deliverables for the active continuous family live in:

- [continuous design deliverables](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/packages/continuous_design_deliverables)
- [continuous mesh exports](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/model_exports/continuous_mesh_exports)

## Archived Older Runs

Older exploratory, asymmetric, or non-selected runs were moved to:

- [archive/deprecated_assets](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/archive/deprecated_assets)
