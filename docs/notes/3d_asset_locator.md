# 3D Asset Locator

Scan date: 2026-04-24.

This note records what is in the current working directory for the beam 3D/model assets, where each relevant item lives, and which outputs should be treated as current.

## 3D Appearance

The current corrected export, `continuous_uniform_both_load_cases_9in_corrected`, looks like a long, continuous rectangular beam with a closed box/tube-style body. In the preview it reads as a mostly straight 9 in member with a subtly varying envelope: wider/taller end regions, a narrower middle width, and no web openings. The mesh is faceted along the length, so the exported preview shows repeated cross-section slices and triangulated side faces.

The actual optimized dimensions behind that look are:

| Item | Value |
| --- | --- |
| Total length | 9.0 in |
| Supports | x = 0.5 in and x = 8.5 in |
| Widths, left/mid/right | 0.5211 / 0.2943 / 0.5211 in |
| Heights, left/mid/right | 0.6585 / 0.7128 / 0.6585 in |
| Wall thickness | 0.0508 in |
| Openings, left/mid/right | 0 / 0 / 0 |
| Weight | 0.04079 lbf |
| Governing FoS | 1.503, Load Case 2 at x = 5.500 in |

The newer `lc2_8lb_edge_support_trial_*` runs do not currently have STL/OBJ/DXF mesh exports in `designs/model_exports`. Based on their JSON geometry, Trial C would look much more sculpted than the corrected submission export: asymmetric, lighter, with web openings on the left and right sections and a larger right-side opening ratio. It is not packaged as a 3D model yet.

## Current Source Of Truth

Use this design as the current corrected reference:

| Purpose | Path | Modified |
| --- | --- | --- |
| Corrected active run folder | `designs/active_runs/continuous_uniform_both_load_cases_9in_corrected` | 2026-04-23 12:20:31 |
| Best design data | `designs/active_runs/continuous_uniform_both_load_cases_9in_corrected/best_design.json` | 2026-04-23 12:20:30 |
| Markdown report | `designs/active_runs/continuous_uniform_both_load_cases_9in_corrected/optimization_report.md` | 2026-04-23 12:20:31 |
| LaTeX report | `designs/active_runs/continuous_uniform_both_load_cases_9in_corrected/optimization_report.tex` | 2026-04-23 12:20:31 |
| Full design study | `designs/active_runs/continuous_uniform_both_load_cases_9in_corrected/design_study.csv` | 2026-04-23 12:20:31 |
| Parameter map | `designs/active_runs/continuous_uniform_both_load_cases_9in_corrected/beam_parameter_map.png` | 2026-04-23 12:20:30 |

## Current 3D Export Files

These are the current corrected mesh and preview outputs.

| Item | Path | Modified | Size |
| --- | --- | --- | --- |
| STL mesh | `designs/model_exports/continuous_mesh_exports_9in_corrected/continuous_uniform_both_load_cases_9in_corrected.stl` | 2026-04-23 12:20:31 | 1625.5 KB |
| OBJ mesh | `designs/model_exports/continuous_mesh_exports_9in_corrected/continuous_uniform_both_load_cases_9in_corrected.obj` | 2026-04-23 12:20:31 | 203.6 KB |
| DXF sketch | `designs/model_exports/continuous_mesh_exports_9in_corrected/continuous_uniform_both_load_cases_9in_corrected.dxf` | 2026-04-23 12:20:31 | 32.4 KB |
| 3D preview PNG | `designs/model_exports/continuous_mesh_exports_9in_corrected/continuous_uniform_both_load_cases_9in_corrected_preview.png` | 2026-04-23 12:20:31 | 325.8 KB |
| Export README | `designs/model_exports/continuous_mesh_exports_9in_corrected/README.md` | 2026-04-23 12:20:31 | 1.0 KB |

## Current Packaged Deliverable

This folder duplicates the corrected export plus report/data assets for handoff.

| Item | Path | Modified |
| --- | --- | --- |
| Package folder | `designs/packages/continuous_design_deliverables_9in_corrected/continuous_uniform_both_load_cases_9in_corrected` | 2026-04-23 12:20:31 |
| Package STL | `designs/packages/continuous_design_deliverables_9in_corrected/continuous_uniform_both_load_cases_9in_corrected/continuous_uniform_both_load_cases_9in_corrected.stl` | 2026-04-23 12:20:31 |
| Package OBJ | `designs/packages/continuous_design_deliverables_9in_corrected/continuous_uniform_both_load_cases_9in_corrected/continuous_uniform_both_load_cases_9in_corrected.obj` | 2026-04-23 12:20:31 |
| Package DXF | `designs/packages/continuous_design_deliverables_9in_corrected/continuous_uniform_both_load_cases_9in_corrected/continuous_uniform_both_load_cases_9in_corrected.dxf` | 2026-04-23 12:20:31 |
| Package preview | `designs/packages/continuous_design_deliverables_9in_corrected/continuous_uniform_both_load_cases_9in_corrected/continuous_uniform_both_load_cases_9in_corrected_preview.png` | 2026-04-23 12:20:31 |
| Package best design | `designs/packages/continuous_design_deliverables_9in_corrected/continuous_uniform_both_load_cases_9in_corrected/best_design.json` | 2026-04-23 12:20:31 |
| Package design study | `designs/packages/continuous_design_deliverables_9in_corrected/continuous_uniform_both_load_cases_9in_corrected/design_study.csv` | 2026-04-23 12:20:31 |
| Package reports | `designs/packages/continuous_design_deliverables_9in_corrected/continuous_uniform_both_load_cases_9in_corrected/optimization_report.md` and `.tex` | 2026-04-23 12:20:31 |
| Package plots | `designs/packages/continuous_design_deliverables_9in_corrected/continuous_uniform_both_load_cases_9in_corrected/best_design/*.png` | 2026-04-23 12:20:31 |

## Active Run Inventory

These are the non-archived optimization runs under `designs/active_runs`.

| Run | Modified | Status | Mesh export |
| --- | --- | --- | --- |
| `continuous_uniform_both_load_cases_9in_corrected` | 2026-04-23 12:20:31 | Current corrected reference | Yes, in `designs/model_exports/continuous_mesh_exports_9in_corrected` |
| `continuous_uniform_both_load_cases` | 2026-04-22 11:58:08 | Older pre-correction comparison | Yes, in `designs/model_exports/continuous_mesh_exports` |
| `continuous_uniform_load_case_1` | 2026-04-22 11:58:08 | Older pre-correction comparison | Yes, in `designs/model_exports/continuous_mesh_exports` |
| `continuous_uniform_load_case_2` | 2026-04-22 11:58:08 | Older pre-correction comparison | Yes, in `designs/model_exports/continuous_mesh_exports` |
| `lc2_8lb_edge_support_trial_a` | 2026-04-24 10:38:42 | New local trial, untracked by git | No mesh export found |
| `lc2_8lb_edge_support_trial_b` | 2026-04-24 10:38:42 | New local trial, untracked by git | No mesh export found |
| `lc2_8lb_edge_support_trial_c_focused` | 2026-04-24 10:41:09 | New local trial, untracked by git | No mesh export found |

## Active Run Geometry Snapshot

| Run | Widths L/M/R | Heights L/M/R | Openings L/M/R | Wall | Weight | Min FoS | Governing |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `continuous_uniform_both_load_cases_9in_corrected` | 0.5211 / 0.2943 / 0.5211 | 0.6585 / 0.7128 / 0.6585 | 0.000 / 0.000 / 0.000 | 0.0508 | 0.04079 | 1.503 | LC2 at x = 5.500 in |
| `continuous_uniform_both_load_cases` | 0.4244 / 0.4326 / 0.4244 | 0.3920 / 0.3500 / 0.3920 | 0.000 / 0.000 / 0.000 | 0.0820 | 0.03752 | 1.526 | LC2 at x = 5.000 in |
| `continuous_uniform_load_case_1` | 0.6903 / 0.3967 / 0.6903 | 0.3500 / 0.3500 / 0.3500 | 0.000 / 0.000 / 0.000 | 0.0797 | 0.04212 | 1.601 | LC2 at x = 4.000 in |
| `continuous_uniform_load_case_2` | 0.5413 / 0.4126 / 0.5413 | 0.5765 / 0.3615 / 0.5765 | 0.000 / 0.000 / 0.000 | 0.0600 | 0.03568 | 1.543 | LC2 at x = 4.000 in |
| `lc2_8lb_edge_support_trial_a` | 0.2040 / 0.2324 / 0.3527 | 0.7402 / 1.1500 / 0.9048 | 0.313 / 0.135 / 0.095 | 0.0558 | 0.04462 | 1.502 | LC2 at x = 5.500 in |
| `lc2_8lb_edge_support_trial_b` | 0.2217 / 0.4303 / 0.1921 | 0.4542 / 0.7382 / 0.4500 | 0.306 / 0.000 / 0.500 | 0.0477 | 0.02811 | 1.582 | LC2 at x = 5.500 in |
| `lc2_8lb_edge_support_trial_c_focused` | 0.2217 / 0.4300 / 0.2000 | 0.6671 / 0.6834 / 0.7812 | 0.306 / 0.000 / 0.625 | 0.0460 | 0.02926 | 1.501 | LC2 at x = 8.500 in |

## Older Non-Archived Mesh Exports

These are still outside the archive but should be treated as pre-correction references.

| Folder | Contains | Latest modified |
| --- | --- | --- |
| `designs/model_exports/continuous_mesh_exports` | 3 designs, each with STL/OBJ/DXF and preview PNG | 2026-04-22 12:19:25 |
| `designs/packages/continuous_design_deliverables/continuous_uniform_both_load_cases` | STL/OBJ/DXF, preview, reports, plots | 2026-04-22 12:19:25 |
| `designs/packages/continuous_design_deliverables/continuous_uniform_load_case_1` | STL/OBJ/DXF, preview, reports, plots | 2026-04-22 12:19:22 |
| `designs/packages/continuous_design_deliverables/continuous_uniform_load_case_2` | STL/OBJ/DXF, preview, reports, plots | 2026-04-22 12:19:23 |

## Whole CWD Mesh Scan

Across the full cwd, the scan found:

| Category | Count |
| --- | --- |
| Mesh/CAD files, STL/OBJ/DXF | 156 |
| Preview PNG files matching `*_preview.png` | 63 |
| Non-archived mesh/CAD files under `designs` | 24 |
| Archived mesh/CAD files under `archive` | 132 |
| Non-archived preview PNG files under `designs` | 8 |
| Archived preview PNG files under `archive` | 55 |

## Archived Model Clusters

Everything below is under `archive/deprecated_assets` and should be treated as historical unless intentionally resurrected.

| Folder | Mesh/CAD files | Types | Latest modified |
| --- | ---: | --- | --- |
| `archive/deprecated_assets/legacy_continuous_design_deliverables/optimization_continuous_uniform_all` | 3 | STL/OBJ/DXF | 2026-04-22 11:58:36 |
| `archive/deprecated_assets/legacy_continuous_design_deliverables/optimization_continuous_uniform_load1` | 3 | STL/OBJ/DXF | 2026-04-22 11:58:34 |
| `archive/deprecated_assets/legacy_continuous_design_deliverables/optimization_continuous_uniform_load2` | 3 | STL/OBJ/DXF | 2026-04-22 11:58:35 |
| `archive/deprecated_assets/legacy_continuous_design_deliverables/optimization_final` | 3 | STL/OBJ/DXF | 2026-04-22 11:58:37 |
| `archive/deprecated_assets/legacy_continuous_design_deliverables/sample_geometry` | 3 | STL/OBJ/DXF | 2026-04-22 12:18:32 |
| `archive/deprecated_assets/legacy_continuous_mesh_exports` | 15 | STL/OBJ/DXF | 2026-04-22 12:18:32 |
| `archive/deprecated_assets/models_3d` | 66 | STL/OBJ | 2026-04-22 11:37:25 |
| `archive/deprecated_assets/models_3d_relevant` | 18 | STL/OBJ/DXF | 2026-04-22 11:52:12 |
| `archive/deprecated_assets/relevant_design_packages/optimization_final` | 3 | STL/OBJ/DXF | 2026-04-22 11:52:09 |
| `archive/deprecated_assets/relevant_design_packages/optimization_outputs` | 3 | STL/OBJ/DXF | 2026-04-22 11:52:07 |
| `archive/deprecated_assets/relevant_design_packages/optimization_revised_soft_symmetric` | 3 | STL/OBJ/DXF | 2026-04-22 11:52:12 |
| `archive/deprecated_assets/relevant_design_packages/optimization_revised_symmetric_balanced` | 3 | STL/OBJ/DXF | 2026-04-22 11:52:11 |
| `archive/deprecated_assets/relevant_design_packages/optimization_revised_symmetric_light` | 3 | STL/OBJ/DXF | 2026-04-22 11:52:10 |
| `archive/deprecated_assets/relevant_design_packages/sample_geometry` | 3 | STL/OBJ/DXF | 2026-04-22 11:52:06 |

