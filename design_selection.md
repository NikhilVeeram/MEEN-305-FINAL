# Design Selection

This file organizes the current beam-design outputs and identifies the best candidate to present.

## Recommended best design

Use the design in `optimization_outputs/` as the current best design.

### Why this is the best current candidate

- It is the lightest feasible design found by the current optimizer objective.
- It drives the governing minimum factor of safety close to the project target of `1.5`.
- It includes spanwise lightening features, not just outer taper.
- It satisfies the current optimization constraint set.

### Best-design metrics

- Weight: `0.04117 lbf`
- Governing minimum FoS: `1.584`
- Governing load case: `Load Case 1`
- Governing location: `x = 4.000 in`
- Max deflection: `0.08054 in`

### Best-design geometry

- `b_L = 0.67597 in`
- `b_M = 0.35000 in`
- `b_R = 0.66377 in`
- `h_L = 0.37894 in`
- `h_M = 0.38709 in`
- `h_R = 1.79385 in`
- `t = 0.06000 in`
- `r_L = 0.08089`
- `r_M = 0.46889`
- `r_R = 0.16990`

## Where everything is

### Main selected design

- Summary report: [optimization_report.md](<c:\Users\nikhi\Documents\GitHub\MEEN-305-FINAL\optimization_outputs\optimization_report.md>)
- LaTeX report: [optimization_report.tex](<c:\Users\nikhi\Documents\GitHub\MEEN-305-FINAL\optimization_outputs\optimization_report.tex>)
- Best-design data: [best_design.json](<c:\Users\nikhi\Documents\GitHub\MEEN-305-FINAL\optimization_outputs\best_design.json>)
- Full design trail: [design_study.csv](<c:\Users\nikhi\Documents\GitHub\MEEN-305-FINAL\optimization_outputs\design_study.csv>)
- Variable map: [beam_parameter_map.png](<c:\Users\nikhi\Documents\GitHub\MEEN-305-FINAL\optimization_outputs\beam_parameter_map.png>)

### Selected design plots

- Geometry properties: [geometry_properties.png](<c:\Users\nikhi\Documents\GitHub\MEEN-305-FINAL\optimization_outputs\best_design\geometry_properties.png>)
- Outer dimensions and opening profile: [outer_dimension_views.png](<c:\Users\nikhi\Documents\GitHub\MEEN-305-FINAL\optimization_outputs\best_design\outer_dimension_views.png>)
- Load Case 1 plots: [load_case_1_results.png](<c:\Users\nikhi\Documents\GitHub\MEEN-305-FINAL\optimization_outputs\best_design\load_case_1_results.png>)
- Load Case 2 plots: [load_case_2_results.png](<c:\Users\nikhi\Documents\GitHub\MEEN-305-FINAL\optimization_outputs\best_design\load_case_2_results.png>)

## Other useful runs

### `optimization_targeted/`

- This is a good comparison run that also pushed the design near `FoS = 1.5`.
- It is heavier than the current selected design.
- Its best candidate was:
  - Weight: `0.06614 lbf`
  - Minimum FoS: `1.553`
  - Max deflection: `0.05775 in`

### Older exploratory runs

- `optimization_opening_smoke/`
- `optimization_smoke_test/`
- `optimization_smoke_test_2/`

These are useful as development history, but not the design to present as the final best candidate.

## Presentation recommendation

If you need one clear answer right now, present `optimization_outputs/` as the best design.

If your team decides deflection also needs to be tightly controlled for the final pick, rerun the optimizer with an explicit deflection limit before locking the final presentation design.
