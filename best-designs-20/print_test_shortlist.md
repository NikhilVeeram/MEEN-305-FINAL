# Print Test Set

Generated on 2026-04-24.

This record tracks the actual printed candidates from the weight-ranked `best-designs-20` set. Only ranks 02, 03, and 04 were printed for the current physical test pass. Rank 01, rank 05, and the remaining ranked candidates were not printed in this pass.

Use `print_settings.md` for the slicer setup. Prefer the STLs in `3d-models-print-oriented/`; they are rotated 45 degrees about the beam length to avoid the closed-tube floating-cantilever warning. Import at `2540%` uniform scale, or set X length to `228.6 mm`, because the generated mesh coordinates are in inches.

Actual supported slice note: the first real slice used monotonic patterns throughout, included supports, and kept the base profile speeds unchanged. For the next print pass, try to remove supports where possible or block any support that would be trapped inside the closed tube.

## Actual Printed Candidates

Candidate 02 is the expected favorite because it is the lightest printed beam. Candidates 03 and 04 are backup/comparison prints with more weight and different FoS/deflection tradeoffs. Test all three and use the lightest beam that does not fail as the report candidate.

| Printed rank | Candidate | Current role |
| ---: | --- | --- |
| 02 | `02_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1066__w_0.04048__fos_1.674` | Expected best choice if it survives testing. Lightest printed candidate: weight `0.04048 lbf`, FoS `1.674`, deflection `0.12217 in`. |
| 03 | `03_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1062__w_0.04179__fos_1.846` | Heavier backup/comparison print with higher modeled FoS: weight `0.04179 lbf`, FoS `1.846`, deflection `0.10640 in`. |
| 04 | `04_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1018__w_0.04291__fos_1.649` | Heaviest of the printed set, useful if 02/03 fail or show print defects: weight `0.04291 lbf`, FoS `1.649`, deflection `0.14060 in`. |

## Not Printed In This Pass

- Rank 01: `01_overall_rank__continuous_uniform_both_load_cases_9in_corrected__eval_0219__w_0.03983__fos_1.761`
- Rank 05: `05_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1075__w_0.04297__fos_1.520`
- Ranks 06-20

## Print Gates

The printed candidates are closed tubes with:

- max web opening ratio = `0.000`
- wall thickness >= `0.060 in`
- residual web ligament >= `0.140 in`
- shell area ratio >= `0.320`
- max dimension slope <= `0.140 in/in`
- max deflection <= `0.165 in`
- min FoS >= `1.5`
