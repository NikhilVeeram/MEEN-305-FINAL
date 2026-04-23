# Beam Length / Support Correction Audit

This note records the correction from the mistaken `8 in` beam model to the
project-correct setup:

- total beam length: `9.0 in`
- support A: `x = 0.5 in`
- support B: `x = 8.5 in`
- support span: `8.0 in`

The project handout is explicit that the beam is `9 in` long while the supports
are `8 in` apart. Earlier repo work mixed those two ideas and effectively used
the support span as the full beam length in several places.

## Places that depended on the old setup

- [beam_solver.py](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/scripts/beam_solver.py)
  The analysis grid, reaction/moment logic, default geometry, and CLI defaults
  treated the support span as the beam x-domain.
- [optimize_beam.py](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/scripts/optimize_beam.py)
  Search geometry, parameter maps, and auto-generated reports assumed the old
  `0..8 in` coordinate picture.
- [beam_3d_models.py](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/scripts/beam_3d_models.py)
  Mesh and DXF exports were built over the analysis span instead of the full
  beam length.
- [diagram_assets.py](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/scripts/diagram_assets.py)
  The front-view length graphic still showed an `8 in` beam body.
- Existing run folders under [designs/active_runs](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/designs/active_runs)
  Their JSON, reports, plots, previews, and packaged exports reflect the older
  coordinate assumptions unless regenerated.
- [final_project_report.tex](/c:/Users/nikhil/Documents/GitHub/MEEN-305-FINAL/docs/reports/final_project_report.tex)
  Some sections already mention `L_total = 9 in`, but many detailed values,
  equations, figure captions, and result narratives still come from the older
  run set and should be regenerated from the corrected workflow.

## What changed in code

- The beam geometry now carries explicit support positions in addition to total
  length and support span.
- The solver works on global beam coordinates over the full `0..9 in` beam.
- Reactions still use the `8 in` support span and load position `a` from
  support A, which matches the project equations.
- Overhang regions outside the supports are treated as unloaded beam segments.
- Optimization reporting now distinguishes:
  - support span `L`
  - total beam length `L_total`
  - support positions `x_A`, `x_B`
  - global beam x-position for each load
- The FoS plot is visually clipped to a readable range, and the optimizer
  uniformity logic now evaluates only the meaningful supported region rather
  than allowing zero-stress overhangs to distort the objective.

## Outputs that need regeneration

- New corrected active run folder:
  `designs/active_runs/continuous_uniform_both_load_cases_9in_corrected`
- Any package derived from the corrected run under `designs/packages/`
- Any corrected `.stl`, `.obj`, `.dxf`, and preview exports under
  `designs/model_exports/`
- Any note or report that quotes old governing FoS, deflection, weight, or
  load-position values from the `0..8 in` interpretation
- The final report after the corrected run is accepted as the new reference

## Risks / assumptions still to watch

- The optimizer can make the useful-region FoS flatter, but FoS will still rise
  near supports and unloaded ends because the bending moment approaches zero
  there. A perfectly horizontal FoS plot is not physically achievable for this
  load case family.
- Existing archived runs remain valuable for reference but should not be quoted
  as final corrected results.
- If any external CAD or presentation files were built from older exports, they
  must be refreshed from the corrected run folder rather than reused.
