# Active Continuous Design Summary

## What I Changed

This revision follows the project handout more closely:

- continuous closed tube only
- no weight-reducing holes or web cutouts
- symmetric left/right geometry
- objective includes a direct uniformity term so the beam is pushed toward a
  nearly constant stress / FoS profile over the meaningful loaded region
- final size is still reduced until the governing FoS stays just above `1.5`

Implementation changes:

- `uniformity_weight`
- `uniformity_case = load1 | load2 | all`
- `mirror_profile`
- zero-opening runs using `--min-web-opening-ratio 0 --max-web-opening-ratio 0`

## Important Note About Edge FoS

The project suggestion to minimize the standard deviation of stress is good, and
that is now part of the search objective.

However, exact `FoS = 1.5` all the way to the supports is not physically
possible for a simply supported beam under point loading, because the bending
moment goes to zero at the supports. That makes the stress collapse there and
the FoS rise sharply.

To match the intent of the instructions, I optimized uniformity over the
meaningful loaded region rather than forcing the mathematically impossible edge
behavior. The optimizer uses a stress floor ratio of `0.35` so it focuses on
the beam regions that are actually carrying significant bending.

## New Continuous Candidates

| Design | Optimization target | Weight (lbf) | Min FoS | Max deflection (in) | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| `continuous_uniform_load_case_1` | Make Load Case 1 as uniform as possible while satisfying both cases | 0.04212 | 1.601 | 0.12094 | Closed, continuous, symmetric tube; most conservative of the three. |
| `continuous_uniform_load_case_2` | Make Load Case 2 as uniform as possible while satisfying both cases | 0.03568 | 1.543 | 0.12117 | Lightest of the new continuous family. |
| `continuous_uniform_both_load_cases` | Balance both load cases together | 0.03752 | 1.526 | 0.12629 | Best compromise if you want one balanced continuous design. |

## Geometry Snapshots

### `continuous_uniform_load_case_1`

- widths: `0.690 / 0.397 / 0.690 in`
- heights: `0.350 / 0.350 / 0.350 in`
- openings: `0 / 0 / 0`

### `continuous_uniform_load_case_2`

- widths: `0.541 / 0.413 / 0.541 in`
- heights: `0.577 / 0.362 / 0.577 in`
- openings: `0 / 0 / 0`

### `continuous_uniform_both_load_cases`

- widths: `0.424 / 0.433 / 0.424 in`
- heights: `0.392 / 0.350 / 0.392 in`
- openings: `0 / 0 / 0`

## Which One Is Best

If the priority is lowest weight among the new continuous symmetric designs,
choose `continuous_uniform_load_case_2`.

If the priority is best compromise across both load directions, choose
`continuous_uniform_both_load_cases`.

## Packaged Deliverables

- [continuous_uniform_load_case_1 package](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/packages/continuous_design_deliverables/continuous_uniform_load_case_1)
- [continuous_uniform_load_case_2 package](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/packages/continuous_design_deliverables/continuous_uniform_load_case_2)
- [continuous_uniform_both_load_cases package](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/designs/packages/continuous_design_deliverables/continuous_uniform_both_load_cases)

Each package includes:

- `best_design.json`
- `optimization_report.md`
- `optimization_report.tex`
- `beam_parameter_map.png`
- `best_design/*.png`
- preview PNG
- `.obj`
- `.stl`
- `.dxf`

## STEP Status

DXF exports were generated successfully.

STEP files were still not generated because the repo does not include a STEP
export-capable CAD kernel or library.
