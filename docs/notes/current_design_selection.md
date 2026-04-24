# Current Design Selection

This note identifies the current recommended design candidate after correcting
the beam geometry to the project-required setup:

- total beam length: `9.0 in`
- support A: `x = 0.5 in`
- support B: `x = 8.5 in`
- support span: `8.0 in`

## Recommended Corrected Design

Use `continuous_uniform_both_load_cases_9in_corrected` as the current active
reference design.

Why this is the best corrected candidate in the repo right now:

- It uses the project-correct `9 in` overall beam length.
- It places the supports at `x = 0.5 in` and `x = 8.5 in`.
- It keeps the beam continuous, closed, and left-right symmetric.
- It was re-optimized with a strong penalty on excess FoS so the governing case
  is driven back down near the `1.5` target instead of staying overbuilt.
- Its governing FoS occurs in Load Case 2 at the correct off-center load
  position, which matches the project intent better than the earlier mistaken
  `8 in` beam interpretation.

Key metrics:

- Weight: `0.04079 lbf`
- Governing minimum FoS: `1.503`
- Governing load case: `Load Case 2`
- Governing location: `x = 5.500 in`
- Maximum deflection: `0.16121 in`

## Current Physical Print/Test Pass

For the current physical print pass, only ranks 02, 03, and 04 from
`best-designs-20` were printed. Rank 01, rank 05, and the remaining ranked
candidates were not printed in this pass.

Rank 02 is expected to be the best printed candidate because it has the lowest
modeled weight among the printed set. The final report choice should be made
after testing ranks 02, 03, and 04, using the lightest printed beam that does
not fail.

## Where the Active Files Live

### Corrected active run

- Run folder: [continuous_uniform_both_load_cases_9in_corrected](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases_9in_corrected)
- Summary report: [optimization_report.md](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases_9in_corrected/optimization_report.md)
- LaTeX report: [optimization_report.tex](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases_9in_corrected/optimization_report.tex)
- Best-design data: [best_design.json](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases_9in_corrected/best_design.json)
- Full design trail: [design_study.csv](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases_9in_corrected/design_study.csv)
- Variable map: [beam_parameter_map.png](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases_9in_corrected/beam_parameter_map.png)

### Corrected plots

- Geometry properties: [geometry_properties.png](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases_9in_corrected/best_design/geometry_properties.png)
- Outer dimensions: [outer_dimension_views.png](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases_9in_corrected/best_design/outer_dimension_views.png)
- Load Case 1 plots: [load_case_1_results.png](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases_9in_corrected/best_design/load_case_1_results.png)
- Load Case 2 plots: [load_case_2_results.png](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases_9in_corrected/best_design/load_case_2_results.png)

## Packaged Deliverables

- Package folder: [continuous_design_deliverables_9in_corrected](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/packages/continuous_design_deliverables_9in_corrected)
- Mesh export folder: [continuous_mesh_exports_9in_corrected](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/model_exports/continuous_mesh_exports_9in_corrected)

## Older Active Runs

The earlier `continuous_uniform_*` run folders remain useful as reference, but
they were generated before the explicit `9 in` beam / `0.5 in` and `8.5 in`
support correction was pushed through the code and outputs. Treat them as
pre-correction references, not as the current final answer.
