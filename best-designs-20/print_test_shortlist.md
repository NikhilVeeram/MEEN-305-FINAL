# Print Test Shortlist

Generated on 2026-04-24.

All five shortlist beams below come from the regenerated closed-tube top 20. They are intended for print testing, not just numerical ranking.

Hard print gates used for this shortlist:

- closed tube only: max web opening ratio = `0.000`
- wall thickness >= `0.060 in`
- residual web ligament >= `0.140 in`
- shell area ratio >= `0.320`
- max geometry slope <= `0.140 in/in`
- corrected project geometry: 9.0 in total length, supports at x = 0.5 in and x = 8.5 in
- feasible with min FoS >= `1.5`
- max deflection <= `0.165 in`

## Print Order

| Print | Candidate | Why print it |
| ---: | --- | --- |
| 1 | `02_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1064__w_0.04503__fos_1.573` | Best first print. Closed, smooth, no openings, wall `0.0696 in`, FoS `1.573`, deflection `0.15472 in`, and better margin than the near-limit Rank 01. |
| 2 | `06_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1075__w_0.04297__fos_1.520` | Closest to the target FoS while still passing print gates. This is the useful "how close can we safely run it?" print. |
| 3 | `07_overall_rank__continuous_uniform_both_load_cases_9in_corrected__eval_0219__w_0.03983__fos_1.761` | Lightest shortlist option with very low predicted deflection, `0.11057 in`. Good comparison against the newer closed-tube search family. |
| 4 | `01_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1113__w_0.04801__fos_1.591` | Best ranked closed-tube candidate by the flatness score. Print after the safer balanced candidate because its deflection is close to the limit, `0.16477 in`. |
| 5 | `04_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1066__w_0.04048__fos_1.674` | Light and stiff closed-tube variant, deflection `0.12217 in`. Good backup if the near-target FoS design feels too flexible or delicate. |

## Quick Interpretation

Print 1 first because it is the most balanced practical candidate.

Print 2 checks whether the analysis can safely run near FoS = 1.5.

Print 3 is the lightweight/stiff comparison.

Print 4 is the best flatness-ranked candidate, but its predicted deflection is close enough to the limit that it should not be the first print.

Print 5 is the conservative lightweight backup.

## Notes For Test Setup

- Use the matching STL from `best-designs-20/3d-models/`.
- Keep print orientation consistent across all five so the comparison is meaningful.
- Record actual printed mass before load testing.
- Inspect the first layer and side walls; reject any print with visible wall separation, under-extrusion, or corner lifting.
- After testing, compare measured failure/deflection against Load Case 2 first, because LC2 governs this design family.

