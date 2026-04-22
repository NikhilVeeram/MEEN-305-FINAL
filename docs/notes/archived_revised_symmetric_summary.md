# Archived Revised Symmetric Solution Summary

## What Changed

This note documents an archived intermediate design family. The active design
set now lives in
[active_continuous_design_summary.md](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/docs/notes/active_continuous_design_summary.md).

I revised the optimizer so it can explicitly prefer:

- left/right symmetry
- smoother, less abrupt taper
- the same existing printability and durability checks

New optimizer controls added:

- `--mirror-profile` to force left and right support sections to match
- `--symmetry-weight` to penalize left/right imbalance
- `--smoothness-weight` to penalize aggressive shape changes

## Why the Old Designs Looked Wrong

Your concern is valid: several of the older solutions were too one-sided or had
sharp shape changes that were not a good trade for manufacturability.

The key reason is that the old optimizer minimized weight while only softly
rewarding stress utilization. It had no direct penalty for:

- left/right imbalance
- abrupt taper
- visually awkward one-sided flare

## Why FoS Becomes Huge at the Edges

This part is important: for a simply supported beam with point loads, the
bending moment goes to zero at the supports. Since bending stress goes to zero
there, the factor of safety mathematically becomes very large near the edges.

That means you cannot make edge FoS stay near `1.5` everywhere unless you let
the beam shrink almost to zero at the supports. A real printed beam cannot do
that because it still needs:

- finite wall thickness
- finite printable cross-section
- enough material to transfer shear into the supports

So the correct design goal is not "make support FoS equal the middle FoS." The
correct goal is:

- keep the support sections as small as printability allows
- avoid unnecessary asymmetry
- avoid abrupt taper that adds manufacturing risk without helping much

## Before vs After

| Design | Weight (lbf) | Min FoS | Max Defl. (in) | Symmetry score | Smoothness score | What it looks like |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `optimization_outputs` | 0.04117 | 1.584 | 0.08054 | 1.23387 | 0.14016 | Very asymmetric and sharply flared. |
| `optimization_final` | 0.03018 | 1.634 | 0.12226 | 0.26297 | 0.02698 | Better, but still clearly biased side-to-side. |
| `optimization_revised_symmetric_light` | 0.03254 | 1.515 | 0.13453 | 0.00000 | 0.01075 | Exact symmetry with mild taper. |
| `optimization_revised_symmetric_balanced` | 0.02649 | 1.863 | 0.09424 | 0.00000 | 0.00165 | Exact symmetry and almost uniform shape. |
| `optimization_revised_soft_symmetric` | 0.03312 | 1.639 | 0.10926 | 0.04279 | 0.02351 | Slight asymmetry allowed, but much cleaner than before. |

## Best Revised Set

### 1. `optimization_revised_symmetric_balanced`

This is the strongest overall revision.

- It is the lightest of the revised candidates.
- It is exactly symmetric left-to-right.
- It has the smoothest profile of the revised set.
- It also has lower deflection than the current `optimization_final`.
- It passes the printability checks cleanly.

Geometry:

- widths: `0.350 / 0.411 / 0.350 in`
- heights: `0.785 / 0.777 / 0.785 in`
- openings: `0.677 / 0.631 / 0.677`

### 2. `optimization_revised_symmetric_light`

This is the best "near-target FoS" symmetric option.

- It is exactly symmetric.
- It stays very close to the `FoS = 1.5` target.
- It uses a gentle, understandable taper instead of a strange one-sided flare.
- It passes the printability checks cleanly.

Geometry:

- widths: `0.535 / 0.362 / 0.535 in`
- heights: `0.453 / 0.493 / 0.453 in`
- openings: `0.000 / 0.266 / 0.000`

### 3. `optimization_revised_soft_symmetric`

This is the best "allow some asymmetry, but keep it sane" option.

- It is still much cleaner than the old asymmetric solutions.
- It stays feasible and printable.
- It allows some response to the off-center Team 6 load case without becoming
  visually lopsided.

## Packaged Deliverables

These archived comparison packages now live here:

- [optimization_outputs package](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/archive/deprecated_assets/relevant_design_packages/optimization_outputs)
- [optimization_final package](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/archive/deprecated_assets/relevant_design_packages/optimization_final)
- [optimization_revised_symmetric_light package](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/archive/deprecated_assets/relevant_design_packages/optimization_revised_symmetric_light)
- [optimization_revised_symmetric_balanced package](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/archive/deprecated_assets/relevant_design_packages/optimization_revised_symmetric_balanced)
- [optimization_revised_soft_symmetric package](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/archive/deprecated_assets/relevant_design_packages/optimization_revised_soft_symmetric)

Each package includes:

- the `best_design.json`
- the optimization reports
- the solver plot images in `best_design/`
- `beam_parameter_map.png` as the main geometry sketch
- a 3D preview PNG
- `.obj`
- `.stl`
- `.dxf`

## STEP / DXF Status

DXF sketches were generated successfully.

STEP files were not generated. Creating reliable STEP output here would require
a CAD kernel / STEP-export library that is not present in this repo. I chose
not to fake a STEP export because that would be less trustworthy than giving
you real mesh files and real DXF sketches.

## Recommendation

If you want one design to move forward with, use
`optimization_revised_symmetric_balanced`.

If you want the revised design that stays closest to the original "target FoS
near 1.5" logic, use `optimization_revised_symmetric_light`.
