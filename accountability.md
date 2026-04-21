# Accountability

This document maps the MEEN 305 final-project analysis requirements to the current implementation.

Line references below reflect the current versions of `beam_solver.py` and `optimize_beam.py`.

## Core requirement coverage

| Requirement | Exact code location | What to say in the presentation |
| --- | --- | --- |
| User inputs must include span, load magnitude, and load location. | `beam_solver.py` lines 688-730 and 753-759 | The CLI accepts span plus explicit load inputs for Load Case 1 and optional overrides for Load Case 2. |
| Program must also be able to generate the project sample case. | `beam_solver.py` lines 571-585 and 646-685 | `default_geometry()` and `build_load_cases()` generate the built-in project sample when `--geometry-mode sample` is used. |
| Program must take basic tapered geometric dimensions as input. | `beam_solver.py` lines 50-219 and 588-643 | The beam accepts tapered outer width, tapered outer height, wall thickness, and spanwise web-opening ratios for lightening features. |
| Geometry inputs must be checked for physically valid dimensions. | `beam_solver.py` lines 61-104 | Validation checks positive dimensions, wall-thickness feasibility, and whether the lightening openings leave enough ligament. |
| Program must support both required loading conditions. | `beam_solver.py` lines 42-46, 294-350, and 646-685 | Load Case 1 is upright, and Load Case 2 is analyzed after a 90 degree rotation using the active section properties for that orientation. |
| Program must calculate reactions, shear, and moment automatically. | `beam_solver.py` lines 245-270 and 301-311 | These lines compute `R_A`, `R_B`, `V(x)`, and `M(x)` from the applied point load. |
| Shear and moment plots must be generated with labeled units. | `beam_solver.py` lines 493-537 | `plot_load_case()` generates the shear and bending-moment plots with labeled axes and units. |
| Program must compute and plot second moment of area and section modulus. | `beam_solver.py` lines 177-188 and 451-490 | The solver computes the active section properties and plots them in `geometry_properties.png`. |
| Program should automatically plot the outer dimensions in the front and top planes. | `beam_solver.py` lines 392-448 | `plot_outer_dimension_views()` generates the front-view and top-view profiles, plus the opening-ratio profile used for lightening features. |
| Relevant material properties must be user inputs. | `beam_solver.py` lines 16-38 and 736-751 | Elastic modulus, allowable stress, density, orientation factor, and infill factor are all input parameters. |
| Program must compute and plot von Mises stress and factor of safety. | `beam_solver.py` lines 313-350 and 509-520 | The solver computes `sigma_vm(x)` and `FoS(x)` and stores the governing values and locations. |
| Program must compute and plot vertical deflection and slope. | `beam_solver.py` lines 273-291 and 527-537 | Numerical integration enforces simple-support deflection boundary conditions and produces both slope and deflection plots. |
| Program should automatically calculate beam weight. | `beam_solver.py` lines 337-350 | Beam volume is integrated from the tapered area model and converted to weight. |
| If beam self-weight is neglected in stress/deflection analysis, that assumption must be clearly stated. | `beam_solver.py` line 770 | The solver prints the self-weight-neglect assumption explicitly in the console summary. |

## What is now emphasized in the design model

| Design emphasis | Exact code location | Why it matters |
| --- | --- | --- |
| Global minimum FoS over the entire beam and both load cases | `beam_solver.py` lines 337-350 and `optimize_beam.py` lines 193-290 | The optimizer tracks the true governing minimum FoS and its `x` location, rather than only reporting a generic pass/fail. |
| Holes / lightening features between supports | `beam_solver.py` lines 105-188 and `optimize_beam.py` lines 154-171, 519-838 | Spanwise web-opening ratios parameterize weight-reducing features and feed area, second moment, shear area, plots, and auto-written equations. |
| Targeting FoS close to 1.5 instead of leaving the beam heavily overbuilt | `optimize_beam.py` lines 193-290 and 1041-1090 | The optimizer penalizes excess FoS margin and underutilized stress envelope so feasible designs move closer to the project target. |

## Analysis output files

| Output file | Exact generating lines | Why it matters |
| --- | --- | --- |
| `outer_dimension_views.png` | `beam_solver.py` lines 392-448 | Shows the required outer-dimension views and the opening-ratio profile used for the lightening pattern. |
| `geometry_properties.png` | `beam_solver.py` lines 451-490 | Shows second moment of area and section modulus along the beam. |
| `load_case_1_results.png` and `load_case_2_results.png` | `beam_solver.py` lines 493-537 | Show shear, moment, von Mises stress, factor of safety, slope, and deflection for both load cases. |

## Optimization and design-study automation

The optimization companion lives in `optimize_beam.py`.

| Automation feature | Exact code location | What it does |
| --- | --- | --- |
| Search and constraint configuration structures | `optimize_beam.py` lines 26-100 | Defines optimizer settings, variable bounds, and per-design summary objects. |
| Global design-space sampling | `optimize_beam.py` lines 102-124 | Generates stratified beam candidates across the allowed geometry and opening ranges. |
| Elite local refinement | `optimize_beam.py` lines 126-151 | Refines around the best candidates to improve the lightest feasible design. |
| Variable set -> beam geometry conversion | `optimize_beam.py` lines 154-171 | Converts each sampled parameter set into a `TaperedRectangularTube`. |
| Automatic constraint evaluation for both load cases | `optimize_beam.py` lines 193-290 | Computes weight, global minimum factor of safety, governing location, maximum deflection, utilization penalties, and pass/fail status for every candidate. |
| Full design-trail export | `optimize_beam.py` lines 317-421 | Writes every evaluated design to `design_study.csv`, including governing FoS location and opening ratios. |
| Auto-generated equation substitution in Markdown | `optimize_beam.py` lines 382-516 and 519-643 | Writes the numerical "show the work" equations into `optimization_report.md`. |
| Auto-generated equation substitution in LaTeX | `optimize_beam.py` lines 424-516 and 645-838 | Writes compile-ready LaTeX equations, substitutions, and figures into `optimization_report.tex`. |
| Beam variable map visualization | `optimize_beam.py` lines 841-924 | Creates `beam_parameter_map.png` showing the geometry variables, load locations, and opening-ratio summary. |
| Best-design plot generation | `optimize_beam.py` lines 927-949 | Reuses the solver to generate the geometry and load-case plots for the selected best design. |
| Main optimization workflow | `optimize_beam.py` lines 1041-1123 | Parses inputs, runs the search, selects the best candidate, and writes all optimization outputs. |

## Optimization outputs that support the presentation

| Output file | Exact generating lines | Why it matters |
| --- | --- | --- |
| `optimization_outputs/design_study.csv` | `optimize_beam.py` lines 317-421 and 1093 | Gives the full trail of tried designs for ideation accountability. |
| `optimization_outputs/best_design.json` | `optimize_beam.py` lines 767-791 and 1094 | Stores the selected design, governing load case, governing location, and geometry variables in machine-readable form. |
| `optimization_outputs/beam_parameter_map.png` | `optimize_beam.py` lines 841-924 and 1104-1105 | Visualizes the beam variables and load positions for the report/presentation. |
| `optimization_outputs/optimization_report.md` | `optimize_beam.py` lines 519-643 and 1107-1116 | Gives a readable project note with equations, substitutions, and plots. |
| `optimization_outputs/optimization_report.tex` | `optimize_beam.py` lines 645-838 and 1117-1126 | Gives a LaTeX-ready report that can be compiled later into the final deliverable. |
| `optimization_outputs/best_design/*.png` | `optimize_beam.py` lines 927-949 and 1096-1102 | Gives plot evidence for the chosen optimized candidate. |

## Notes for the presentation

- The static sketches in `diagram_assets.py` are presentation assets only. The requirement-compliant analysis and optimization plots are generated by `beam_solver.py` and `optimize_beam.py`.
- The beam family now explicitly includes lightening openings, so the optimizer can emphasize "holes and other stuff in between" instead of only changing the outer tube taper.
- The governing metric now being tracked is the minimum factor of safety anywhere along the beam across both load cases.
- The optimizer now follows the project’s intended logic more closely: make the stress/FoS distribution more uniform, then drive the governing minimum FoS toward 1.5 without violating the project constraints.
- Commands verified in the current repo state:
  - `python beam_solver.py`
  - `python optimize_beam.py --output-dir optimization_outputs`
