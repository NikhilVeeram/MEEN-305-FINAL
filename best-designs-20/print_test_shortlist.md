# Print Test Shortlist — Current Set

Generated on 2026-04-24 (updated after prior-set test results).

This record covers the **current** best-designs-20 set: all solid closed-tube designs (web opening ratio = 0.000 everywhere) ranked by weight. Wall thickness floor is now 0.040 in (down from 0.060 in in the prior set), which pushed the lightest candidate from ~18 g down to 12.8 g.

Print the champion (rank 01) first. It is the lightest fully solid-wall beam that passes both load cases with standard PLA material assumptions (2380 psi effective allowable). No web openings means no bridging issues, no floating cantilever sections, and no material discontinuities in the side walls.

Use `print_settings.md` for slicer setup. STLs are in `3d-models/`. Scale to `2540%` uniform, or set X to `228.6 mm`, because mesh coordinates are in inches.

---

## Champion — Rank 01 (print first)

| Property | Imperial | Metric |
| --- | --- | --- |
| Design folder | `01_overall_rank__continuous_uniform_both_load_cases_9in_corrected__eval_0370__w_0.02815__fos_1.642` | — |
| Weight (model) | `0.02815 lbf` | `12.77 g` |
| Min FoS | `1.642` | — |
| Governing case | Load Case 2 (sideways, 8 lbf) | — |
| Max deflection | `0.0948 in` | `2.41 mm` |
| Width L / M / R | `0.6020 / 0.5109 / 0.6020 in` | `15.29 / 12.98 / 15.29 mm` |
| Height L / M / R | `0.2891 / 0.4955 / 0.2891 in` | `7.34 / 12.59 / 7.34 mm` |
| Wall thickness | `0.0400 in` | `1.016 mm` |
| Web openings | `0.000 / 0.000 / 0.000` | — |
| STL | `3d-models/01_overall_rank__continuous_uniform_both_load_cases_9in_corrected__eval_0370__w_0.02815__fos_1.642.stl` | — |

LC1 (upright, 5 lbf): FoS = 2.478, max VM = 960 psi, max defl = 0.0864 in / 2.19 mm  
LC2 (side, 8 lbf): FoS = 1.642, max VM = 1450 psi, max defl = 0.0948 in / 2.41 mm

The champion is also copied to `../final-champion/champion_beam.stl`.

---

## Backup Candidates (if rank 01 fails)

| Rank | Weight | Min FoS | Max defl | Notes |
| ---: | --- | --- | --- | --- |
| 02 | 13.1 g | 1.732 | — | Next lightest; solid wall, good FoS margin |
| 03 | 13.4 g | 2.116 | — | Over-designed but very safe backup |
| 04 | 13.5 g | 1.562 | — | Slightly heavier, tighter margin |
| 05 | 13.9 g | 1.789 | — | Conservative closed-tube option |

All backup STLs are in `3d-models/`.

---

## Print Gates (all designs in this set pass)

- Corrected 9.0 in beam, supports at x = 0.5 in and x = 8.5 in
- Max web opening ratio: **0.000** (solid walls, no holes)
- Wall thickness: ≥ 0.040 in (≥ 1.016 mm)
- Min FoS: ≥ 1.5 (standard PLA, 2380 psi effective allowable)
- Evaluated with standard PLA: orientation factor 0.70, infill factor 0.85

---

## Prior Print Test Results (for record)

See `../print_test_shortlist_prior_set.md` for the prior-set results. Summary: rank 03 of the prior set failed to print; ranks 02 and 04 printed successfully.
