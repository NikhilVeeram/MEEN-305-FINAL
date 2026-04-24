# Best Designs 20

Top 20 feasible corrected 9 in beam candidates for report review and print testing.

Ranking formula: `weight_lbf`, with tie-breakers `max_deflection_in`, `abs(min_fos - 1.5)`, then `fos_3to7_std`.

Weight is the primary ranking target. Load Case 2 flatness over x=3..7 is retained as a reported metric and late tie-breaker.

## Folders

- `ranked-designs/`: one folder per top-20 candidate, prefixed with report rank.
- `3d-models/`: generated STL/OBJ/DXF/preview assets after running `scripts/beam_3d_models.py`.
- `report-packages/`: packaged copies of each ranked candidate after 3D generation.
- `ranking_summary.csv`: compact table for report selection.
- `selection_notes.md`: short explanation of the weight-first ranking.
- `print_test_shortlist.md`: five recommended weight-priority prints.
- `print_settings.md`: slicer settings to use for comparable print-test results.

Archived non-top-20 ranked candidates: `archive/ranked-design-candidates/ranked_candidates_after_top20.csv`.
