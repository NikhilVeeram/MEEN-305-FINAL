# Active Continuous Design Summary

This summary now distinguishes between the older continuous design family and
the corrected `9 in` beam workflow.

## Correction Applied

The project handout requires:

- total beam length: `9.0 in`
- support span: `8.0 in`
- support A at `x = 0.5 in`
- support B at `x = 8.5 in`

Earlier repo work kept the `8 in` support span but often treated it as the full
beam length in the analysis and generated assets. The corrected workflow fixes
that mismatch across the solver, optimizer, reports, and exports.

## Current Corrected Candidate

The current corrected active run is:

- [continuous_uniform_both_load_cases_9in_corrected](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases_9in_corrected)

Key corrected metrics:

- Weight: `0.04079 lbf`
- Governing minimum FoS: `1.503`
- Governing case: `Load Case 2`
- Governing location: `x = 5.500 in`
- Maximum deflection: `0.16121 in`

Geometry snapshot:

- widths: `0.521 / 0.294 / 0.521 in`
- heights: `0.659 / 0.713 / 0.659 in`
- openings: `0 / 0 / 0`
- wall thickness: `0.051 in`

## Why This Run Matters

- It satisfies the corrected geometry description from the project.
- It keeps the beam continuous, closed, and symmetric.
- It uses a strong excess-FoS penalty plus a uniformity objective so the
  useful-region FoS profile is flatter and the governing value is pushed down
  near the `1.5` target.
- The FoS plot is still expected to rise near unloaded ends and supports,
  because a simply supported beam cannot physically maintain constant FoS all
  the way into zero-moment regions.

## Reference Notes

- Audit note: [beam_length_support_correction_audit.md](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/docs/notes/beam_length_support_correction_audit.md)
- Selection note: [current_design_selection.md](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/docs/notes/current_design_selection.md)

## Older Continuous Candidates

The older run folders below are still in the repo for comparison, but they are
pre-correction outputs:

- [continuous_uniform_load_case_1](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_load_case_1)
- [continuous_uniform_load_case_2](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_load_case_2)
- [continuous_uniform_both_load_cases](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs/continuous_uniform_both_load_cases)
