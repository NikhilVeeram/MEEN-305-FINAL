# Archived Printability Report for Legacy Saved Beam Solutions

## Scope

This is a historical report for the older saved solution families now stored in
the archive. For the active design family, see
[active_continuous_design_summary.md](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/docs/notes/active_continuous_design_summary.md).

This report reviews every saved optimization solution in the repo, using each
folder's `best_design.json` as the design definition. I analyzed 32 saved
solutions total.

The question here is not just whether a result is structurally feasible in the
solver, but whether it is realistically printable as an FDM beam for the MEEN
305 project.

## Method Used

Each solution was checked against three levels of printability:

1. Hard geometry validation from `beam_solver.py`
   - wall thickness must be at least `0.040 in`
   - all beam dimensions must stay above `0.150 in`
   - remaining web ligament must stay above `max(t, 0.060 in)`

2. Durability / manufacturability screens from `optimize_beam.py`
   - minimum residual web ligament at least `0.080 in`
   - minimum shell area ratio at least `0.180`
   - height ratio at most `2.40`
   - width ratio at most `2.40`
   - max profile slope at most `0.25 in/in`
   - stress concentration factor at most `10.0`

3. Bridge-span check for practical PLA printing
   - because these are hollow tubes, very large inner widths mean the top
     surface has to bridge across open air
   - I treated `max inner width > 1.0 in` as a caution flag for support-free
     PLA printing

Verdict meanings:

- `Yes`: passes the repo's printability checks and does not show a major bridge
  warning
- `Conditional`: can probably be printed, but it has manufacturing risk and is
  not a strong print candidate as modeled
- `No`: fails the repo's own hard geometry validation, so it should not be
  treated as printable as-is

## Overall Findings

- `12` solutions are good print candidates.
- `18` solutions are printable only with clear cautions.
- `2` solutions are not printable as modeled because they fail hard geometry
  validation.
- Every saved solution already has a matching STL in [archived mesh exports](c:/Users/nikhi/Documents/GitHub/MEEN-305-FINAL/archive/deprecated_assets/models_3d),
  but having an STL does not mean the geometry is actually a good print.
- The current selected design in `optimization_outputs/` is structurally
  feasible, but it is not one of the strongest print candidates because its
  ligament is too small and its taper is too aggressive.
- The lightest strong print candidate is `optimization_v2_E` at `0.02939 lbf`.
- The strongest "final-style" connected option is
  `optimization_final` / `optimization_connected_v2_6060`, both at
  `0.03018 lbf` and both passing the printability checks cleanly.

## Detailed Results

| Design | Printable? | Weight (lbf) | Min FoS | Analysis |
| --- | --- | ---: | ---: | --- |
| `optimization_connected_2026` | Yes | 0.05103 | 2.288 | Passes validation, durability, and bridge checks. |
| `optimization_connected_4242` | Yes | 0.05003 | 2.594 | Passes validation, durability, and bridge checks. |
| `optimization_connected_7777` | Yes | 0.03968 | 2.051 | Passes validation, durability, and bridge checks. |
| `optimization_connected_v2_3030` | Yes | 0.03643 | 1.591 | Passes validation, durability, and bridge checks. |
| `optimization_connected_v2_6060` | Yes | 0.03018 | 1.634 | Passes validation, durability, and bridge checks. This is one of the best overall print candidates. |
| `optimization_connected_v2_9191` | Yes | 0.04215 | 1.551 | Passes validation, durability, and bridge checks. |
| `optimization_connected_v3` | Yes | 0.09583 | 1.804 | Passes validation, durability, and bridge checks, but it is much heavier than the lighter passing options. |
| `optimization_final` | Yes | 0.03018 | 1.634 | Passes validation, durability, and bridge checks. This is the cleanest "final" candidate for printing. |
| `optimization_opening_smoke` | Conditional | 0.07581 | 17.286 | Geometry is printable, but shell area ratio is low and the `1.187 in` inner bridge span is large for support-free PLA. |
| `optimization_outputs` | Conditional | 0.04117 | 1.584 | Structurally feasible, but not a clean print candidate. Residual ligament is only `0.0709 in`, height ratio is `4.73`, and profile slope is `0.352 in/in`. |
| `optimization_smoke_test` | Conditional | 0.10285 | 13.855 | Geometry passes the repo rules, but the `1.042 in` inner bridge span makes it a support-sensitive print. |
| `optimization_smoke_test_2` | Conditional | 0.10285 | 13.855 | Same conclusion as `optimization_smoke_test`: printable, but the `1.042 in` bridge span is large for support-free PLA. |
| `optimization_targeted` | Conditional | 0.06614 | 1.553 | Printable with caution only. Shell area ratio is low, height ratio is `5.66`, width ratio is `3.19`, slope is `0.408 in/in`, and stress concentration exceeds the repo limit. |
| `optimization_v2_A` | Conditional | 0.05057 | 3.157 | Printable with caution only. Ligament is `0.0765 in`, shell area ratio is low, width ratio is `3.18`, and the `1.311 in` bridge span is large. |
| `optimization_v2_B` | Conditional | 0.04815 | 3.289 | Printable with caution only. Ligament is `0.0708 in`, shell area ratio is low, height ratio is `2.84`, and slope is slightly above the repo limit. |
| `optimization_v2_C` | Conditional | 0.02779 | 1.543 | Very light, but not a clean print candidate. Ligament is only `0.0621 in` and height ratio is `3.42`. |
| `optimization_v2_D` | Conditional | 0.04946 | 1.670 | Printable with caution only. Shell area ratio is low, height ratio is `3.42`, width ratio is `3.38`, and bridge span reaches `1.046 in`. |
| `optimization_v2_E` | Yes | 0.02939 | 1.588 | Passes validation, durability, and bridge checks. This is the lightest strong print candidate in the repo. |
| `optimization_v2_F` | Yes | 0.03270 | 1.564 | Passes validation, durability, and bridge checks. Strong candidate. |
| `optimization_v2_G` | Conditional | 0.02690 | 1.551 | Extremely light, but the residual ligament is only `0.0784 in`, just below the durability threshold. |
| `optimization_v2_H` | Conditional | 0.04285 | 1.550 | Printable with caution only. Ligament is `0.0774 in`, height ratio is `3.19`, and width ratio is `2.68`. |
| `optimization_v2_I` | Conditional | 0.03578 | 1.564 | Printable, but width ratio is `2.79`, so the geometry is more aggressive than the repo's durability guidance allows. |
| `optimization_v2_J` | Conditional | 0.02655 | 1.549 | Very light, but ligament is only `0.0765 in`, so it is not a robust print choice. |
| `optimization_v2_K` | Conditional | 0.03266 | 1.587 | Printable, but width ratio is `2.66`, above the repo's durability target. |
| `optimization_v2_L` | Conditional | 0.04302 | 1.530 | Printable with caution only. Ligament is `0.0650 in`, width ratio is `3.61`, and bridge span reaches `1.142 in`. |
| `optimization_v2_M` | Conditional | 0.02631 | 1.547 | Very light, but ligament is only `0.0752 in`, so it falls below the durability target. |
| `optimization_v2_N` | Yes | 0.03679 | 1.527 | Passes validation, durability, and bridge checks. Good candidate. |
| `optimization_v2_O` | Conditional | 0.03979 | 1.522 | Printable with caution only. Ligament is `0.0658 in`, width ratio is `3.11`, and bridge span is `1.056 in`. |
| `optimization_v2_P` | Conditional | 0.03929 | 1.544 | Printable with caution only. Shell area ratio is low, height ratio is `2.56`, width ratio is `4.08`, slope is `0.269 in/in`, and bridge span is `1.308 in`. |
| `optimization_v2_Q2025` | No | 0.04589 | 1.500 | Not printable as modeled. It fails hard validation because the web opening leaves only `0.0553 in` ligament, below the required `0.065 in`. |
| `optimization_v2_Q42` | No | 0.03818 | 1.547 | Not printable as modeled. It fails hard validation because the web opening leaves only `0.0556 in` ligament, below the required `0.060 in`. |
| `optimization_v2_Q7777` | Yes | 0.03454 | 1.522 | Passes validation, durability, and bridge checks. Good candidate. |

## Recommendation

If the goal is to choose a solution that is both light and realistically
printable, the best short list is:

- `optimization_v2_E`
- `optimization_final`
- `optimization_connected_v2_6060`
- `optimization_v2_F`
- `optimization_v2_Q7777`

If the goal is to keep the current named "final" solution, `optimization_final`
is a defensible choice.

If the goal is to keep the current "selected design" in `optimization_outputs/`,
I would recommend revising it before printing. It is not impossible to print,
but it is more aggressive than the cleaner passing candidates already saved in
the repo.
