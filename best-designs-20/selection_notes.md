# Selection Notes

Generated on 2026-04-24.

## Weight-First Ranking

The current `best-designs-20` set is ranked by lowest beam weight first. The tie-breakers are:

1. lower maximum deflection
2. FoS closer to `1.5`
3. lower Load Case 2 FoS standard deviation over x = 3..7

The hard print-safe gates are unchanged:

- corrected 9.0 in beam with supports at x = 0.5 in and x = 8.5 in
- closed tube only: max web opening ratio = `0.000`
- wall thickness >= `0.060 in`
- residual web ligament >= `0.140 in`
- shell area ratio >= `0.320`
- max dimension slope <= `0.140 in/in`
- max deflection <= `0.165 in`
- min FoS >= `1.5`

## Lightest Current Pick

Rank 01 is now the lightest print-safe closed-tube candidate:

`01_overall_rank__continuous_uniform_both_load_cases_9in_corrected__eval_0219__w_0.03983__fos_1.761`

Metrics:

- Weight: `0.03983 lbf`
- Minimum FoS: `1.761`
- Maximum deflection: `0.11057 in`
- Wall thickness: `0.06072 in`
- Max opening ratio: `0.000`
- Minimum print ligament: `0.17479 in`

## Folder Map

- `ranked-designs/`: top 20 closed-tube print-safe design folders, ranked by weight.
- `3d-models/`: STL, OBJ, DXF, and preview PNG with filenames matching weight rank.
- `report-packages/`: packaged per-design report folders with copied 3D files and plots.
- `ranking_summary.csv`: compact weight-ranked table.
- `print_test_shortlist.md`: recommended five-print order from the weight-ranked set.

