# Selection Notes

Generated on 2026-04-24.

## Print-Safe Regeneration

The top 20 was regenerated after a printability audit found that the earlier ranking still allowed thin walls and continuous web openings. The current set is deliberately more conservative.

Hard gates now used for `best-designs-20`:

- corrected 9.0 in beam with supports at x = 0.5 in and x = 8.5 in
- closed tube only: max web opening ratio = `0.000`
- wall thickness >= `0.060 in`
- residual web ligament >= `0.140 in`
- shell area ratio >= `0.320`
- max dimension slope <= `0.140 in/in`
- max deflection <= `0.165 in`
- min FoS >= `1.5`

This means the current top 20 is heavier than the earlier flatness/mass ranking, but it is much more appropriate for actual FDM print tests.

## Current Best Pick

Rank 01 is the best closed-tube candidate by the ranking score:

`01_overall_rank__print_safe_contiguous_closed_tube_seed2502__eval_1113__w_0.04801__fos_1.591`

Metrics:

- Weight: `0.04801 lbf`
- Minimum FoS: `1.591`
- Maximum deflection: `0.16477 in`
- Wall thickness: `0.06309 in`
- Max opening ratio: `0.000`
- Minimum print ligament: `0.24917 in`

Because its deflection is close to the imposed limit, the print-test shortlist starts with Rank 02 instead.

## Print Test Shortlist

Use `print_test_shortlist.md` for the recommended five prints and test order.

Short version:

1. Rank 02: best first print, balanced and smooth.
2. Rank 06: closest to FoS = 1.5 while print-safe.
3. Rank 07: light/stiff corrected comparison.
4. Rank 01: best flatness-ranked closed tube, but near deflection limit.
5. Rank 04: light/stiff conservative backup.

## Folder Map

- `ranked-designs/`: top 20 closed-tube print-safe design folders.
- `3d-models/`: STL, OBJ, DXF, and preview PNG for each top-20 candidate.
- `report-packages/`: packaged per-design report folders with copied 3D files and plots.
- `ranking_summary.csv`: compact ranking table for report selection.
- `print_test_shortlist.md`: five-print shortlist and order.

Non-top-20 feasible corrected closed-tube candidates are archived in:

`archive/ranked-design-candidates/ranked_candidates_after_top20.csv`

