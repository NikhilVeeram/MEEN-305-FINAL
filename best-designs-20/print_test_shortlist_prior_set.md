# Print Test Shortlist — Prior Set (2026-04-24 Physical Test Pass)

This file records the outcome of the first physical print-and-test pass on the weight-ranked `best-designs-20` set from commit `cf80a41`. That set enforced closed-tube gates with wall thickness ≥ 0.060 in. The current set (see `print_test_shortlist.md`) supersedes this with a lighter 0.040 in wall floor.

---

## What Was Printed

Only ranks 02, 03, and 04 were printed. Rank 01 and rank 05+ were not printed in this pass.

| Printed rank | Candidate | Weight | Min FoS | Print result |
| ---: | --- | --- | --- | --- |
| 02 | `02_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1066__w_0.04048__fos_1.674` | 0.04048 lbf / 18.4 g | 1.674 | **Printed successfully.** Lightest printed candidate. |
| 03 | `03_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1062__w_0.04179__fos_1.846` | 0.04179 lbf / 18.9 g | 1.846 | **Failed to print.** Did not complete or was not usable. |
| 04 | `04_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1018__w_0.04291__fos_1.649` | 0.04291 lbf / 19.5 g | 1.649 | **Printed successfully.** |

---

## Not Printed In This Pass

- Rank 01: `01_overall_rank__continuous_uniform_both_load_cases_9in_corrected__eval_0219__w_0.03983__fos_1.761` — 18.1 g
- Rank 05: `05_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1075__w_0.04297__fos_1.520` — 19.5 g
- Ranks 06–20

---

## Prior-Set Print Gates

- Corrected 9.0 in beam, supports at x = 0.5 in and x = 8.5 in
- Max web opening ratio: 0.000 (solid walls)
- Wall thickness: ≥ 0.060 in
- Residual web ligament: ≥ 0.140 in
- Shell area ratio: ≥ 0.320
- Max dimension slope: ≤ 0.140 in/in
- Max deflection: ≤ 0.165 in
- Min FoS: ≥ 1.5
