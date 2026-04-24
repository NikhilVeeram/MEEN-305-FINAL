# Best Designs 20

Top 20 feasible corrected 9 in beam candidates for report review and print testing.

This version is closed-tube only. Web openings were removed from the accepted
top 20 because continuous longitudinal openings can create discontinuous print
paths in this simplified mesh family.

Ranking formula: `fos_3to7_std + 4*weight + 0.8*max_deflection + 0.5*abs(min_fos - 1.5)`.

The formula keeps Load Case 2 FoS flatness over x=3..7 dominant while still accounting for mass, deflection, and safety-margin closeness.

Hard print gates:

- max web opening ratio = `0.000`
- wall thickness >= `0.060 in`
- residual web ligament >= `0.140 in`
- shell area ratio >= `0.320`
- max dimension slope <= `0.140 in/in`
- max deflection <= `0.165 in`
- min FoS >= `1.5`

## Folders

- `ranked-designs/`: one folder per top-20 candidate, prefixed with report rank.
- `3d-models/`: generated STL/OBJ/DXF/preview assets after running `scripts/beam_3d_models.py`.
- `report-packages/`: packaged copies of each ranked candidate after 3D generation.
- `ranking_summary.csv`: compact table for report selection.
- `print_test_shortlist.md`: recommended five-print order.

Archived non-top-20 ranked candidates: `archive/ranked-design-candidates/ranked_candidates_after_top20.csv`.
