# Print Test Shortlist

Generated on 2026-04-24.

This shortlist follows the updated priority: minimize weight first while keeping the closed-tube print-safe gates.

Use `print_settings.md` for the slicer setup. Prefer the STLs in `3d-models-print-oriented/`; they are rotated 45 degrees about the beam length to avoid the closed-tube floating-cantilever warning. Import at `2540%` uniform scale, or set X length to `228.6 mm`, because the generated mesh coordinates are in inches.

## Print Order

| Print | Candidate | Why print it |
| ---: | --- | --- |
| 1 | `01_overall_rank__continuous_uniform_both_load_cases_9in_corrected__eval_0219__w_0.03983__fos_1.761` | Lightest accepted print-safe beam. Weight `0.03983 lbf`, FoS `1.761`, deflection `0.11057 in`. |
| 2 | `02_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1066__w_0.04048__fos_1.674` | Second-lightest and still stiff. Weight `0.04048 lbf`, deflection `0.12217 in`. |
| 3 | `05_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1075__w_0.04297__fos_1.520` | Best near-target FoS option among the light front-runners. Good check for running close to FoS `1.5`. |
| 4 | `04_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1018__w_0.04291__fos_1.649` | Similar weight to Print 3 but with more FoS margin. Useful side-by-side comparison. |
| 5 | `08_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_0463__w_0.04394__fos_1.629` | Slightly heavier, very smooth slope metric, and good print-safe geometry. |

## Print Gates

All five are closed tubes with:

- max web opening ratio = `0.000`
- wall thickness >= `0.060 in`
- residual web ligament >= `0.140 in`
- shell area ratio >= `0.320`
- max dimension slope <= `0.140 in/in`
- max deflection <= `0.165 in`
- min FoS >= `1.5`
