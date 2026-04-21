# MEEN 305 Equation Dependency Map (Project-Specific)

This document turns your equation sheet + standard Solid Mechanics conventions into one connected analysis model for the project beam.

## 1) Project Inputs (Per Team)

Required inputs:
- Span between supports: $L = 8$ in
- Beam total length: 9 in
- Load case 1: point load $P_1 = 5$ lb at $a_1 = L/2$
- Load case 2: point load $P_2 = 2 + \text{Team\#}$ lb at
  $a_2 = 2 + \frac{\text{Team\#}}{2}$ in from support A
- Material properties: $E$, $\nu$, density $\rho$, yield/allowable stress
- Safety factor target: $\mathrm{FoS}_{\min} \ge 1.5$
- Geometry parameterization (examples):
  - Rectangular: $b(x), h(x)$
  - Tube: $d_o(x), d_i(x)$
  - I/H/T: flange/web dimensions as functions of $x$

Recommended additional inputs for printed beams:
- Orientation factor $k_{\text{orient}} \in (0,1]$
- Infill factor $k_{\text{infill}} \in (0,1]$
- Effective modulus and allowable stress:
  - $E_{\text{eff}} = k_{\text{orient}} k_{\text{infill}} E_{\text{bulk}}$
  - $\sigma_{\text{allow,eff}} = k_{\text{orient}} k_{\text{infill}} \sigma_{\text{allow,bulk}}$

## 2) Statics -> Reactions -> Internal Loads

For a simply supported beam with one point load $P$ at $x=a$:
- $R_A = P\frac{L-a}{L}$
- $R_B = P\frac{a}{L}$

Shear diagram:
- $V(x) = R_A$ for $0 \le x < a$
- $V(x) = R_A - P$ for $a < x \le L$

Moment diagram:
- $M(x) = R_A x$ for $0 \le x < a$
- $M(x) = R_A x - P(x-a)$ for $a < x \le L$

Program requirement connection:
- User enters $(L,P,a)$
- Program outputs $R_A,R_B$, $V(x)$ plot, $M(x)$ plot

## 3) Geometry -> Section Properties

At each $x$, compute cross-section properties from your chosen topology:
- Area: $A(x)$
- Second moment (bending axis): $I_z(x)$
- Section modulus: $S_z(x)=\frac{I_z(x)}{c(x)}$

Examples:
- Solid rectangle: $A=bh$, $I_z=\frac{bh^3}{12}$, $S_z=\frac{bh^2}{6}$
- Circular tube: $A=\frac{\pi}{4}(d_o^2-d_i^2)$,
  $I=\frac{\pi}{64}(d_o^4-d_i^4)$,
  $S=\frac{I}{d_o/2}$

Program requirement connection:
- Plot $I_z(x)$ and $S_z(x)$
- Plot outer profile in $x$-$y$ and $x$-$z$ views

## 4) Internal Loads + Properties -> Stress

### 4.1 Bending normal stress (dominant for this project)

Using standard beam convention:
- $\sigma_x(x,y)= -\frac{M_z(x) y}{I_z(x)}$
- Outer-fiber max magnitude:
  $\sigma_{b,\max}(x)=\frac{|M_z(x)|}{S_z(x)}$

### 4.2 Shear stress (include in von Mises)

If needed for non-negligible shear regions:
- General beam relation: $\tau=\frac{VQ}{It}$
- For quick conservative screening in rectangles:
  $\tau_{\max}\approx\frac{3V}{2A}$

### 4.3 von Mises stress (project-required justification)

Class-convention 3D form from your sheet is valid generally.
For beam-dominated plane stress approximation:
- $\sigma_{vm}(x) \approx \sqrt{\sigma_x(x)^2 + 3\tau(x)^2}$

If bending dominates and shear is small:
- $\sigma_{vm}(x) \approx |\sigma_x(x)|$

Program requirement connection:
- Compute and plot $\sigma_{vm}(x)$ for each load case

## 5) Stress -> Factor of Safety

Use your class failure criterion based on material behavior and assignment convention.
A practical project definition:
- $\mathrm{FoS}(x)=\frac{\sigma_{\text{allow,eff}}}{\sigma_{vm}(x)}$
- Constraint: $\min_x \mathrm{FoS}(x) \ge 1.5$ for both load cases

If your instructor prefers yield strength directly, replace $\sigma_{\text{allow,eff}}$ accordingly.

Program requirement connection:
- Plot $\mathrm{FoS}(x)$
- Report global minimum FoS for each load case

## 6) Moment + EI -> Slope and Deflection

Euler-Bernoulli beam equation:
- $E_{\text{eff}} I_z(x)\,v''(x)=M_z(x)$
- Slope: $\theta_z(x)=v'(x)$

Boundary conditions for simple supports:
- $v(0)=0$, $v(L)=0$

For variable $I_z(x)$, do numerical integration (or piecewise symbolic if simple).

Program requirement connection:
- Plot $\theta_z(x)$ and $v(x)$
- Report max deflection location and value for both load cases

## 7) Geometry + Density -> Weight (Objective)

Volume:
- $V_{beam}=\int_0^L A(x)\,dx$

Mass and weight:
- $m=\rho V_{beam}$
- $W=mg$

Project objective:
- Minimize beam weight while satisfying all safety/deflection/manufacturing constraints.

## 8) Optional Stability Check (Use Engineering Judgment)

Global Euler buckling is usually for axial compression members, not pure simply-supported bending.
Still, if your topology introduces slender compressive struts/webs, screen with:
- $P_{cr}=\frac{\pi^2 E I}{(K L_c)^2}$
- Ensure local compressive forces stay below buckling threshold with FoS.

Include this only where physically relevant to your chosen topology.

## 9) Full Dependency Chain (What Graders Want to See)

1. Input $(L,P,a)$ + geometry functions + material data.
2. Solve reactions $(R_A,R_B)$.
3. Build $V(x), M(x)$.
4. Compute $A(x), I_z(x), S_z(x)$ from geometry.
5. Compute $\sigma_x, \tau, \sigma_{vm}$.
6. Compute $\mathrm{FoS}(x)$.
7. Compute $\theta_z(x), v(x)$ from $M/(EI)$.
8. Compute weight from $A(x)$ integration.
9. Apply constraints for BOTH loading cases.
10. Iterate dimensions/parameters to minimize weight.

If any step is missing, your model is not fully coupled.

## 10) Optimization Formulation You Can Implement Now

Decision variables (example):
- $\mathbf{d} = [H_{L/2}, n, b_0, b_1, t_{min}, \dots]$

Objective:
- $\min\; W(\mathbf{d})$

Subject to (for load cases 1 and 2):
- $\min_x \mathrm{FoS}_1(x;\mathbf{d}) \ge 1.5$
- $\min_x \mathrm{FoS}_2(x;\mathbf{d}) \ge 1.5$
- $|v_1(x;\mathbf{d})| \le v_{allow}$ (if defined by your team/instructor)
- $|v_2(x;\mathbf{d})| \le v_{allow}$
- Manufacturing constraints:
  - $h(x) \ge h_{min}$, $b(x) \ge b_{min}$
  - Wall thickness $t(x) \ge t_{print,min}$
  - No taper to zero at supports

Recommendation for your report:
- Show 20 designs in appendix, then clearly identify feasible set and final optimum.

## 11) What To Focus On Extensively (Criterion 1)

This is your high-impact checklist for the Theory and Analysis section:
- Explicitly list every governing equation used.
- For each equation, state input variables and where they came from.
- Show the equation handoff chain (e.g., $M \rightarrow \sigma \rightarrow \sigma_{vm} \rightarrow \mathrm{FoS}$).
- Show how both load cases are enforced simultaneously.
- Explain where class assumptions are used:
  - linear elasticity
  - small deflections
  - beam theory applicability
  - ideal supports/loading
  - printed-material effective property assumptions
- Identify the governing location and governing load case.
- Prove optimality logic: among feasible designs, minimum-weight design wins.

## 12) Program Output Checklist (Directly Aligned to Prompt)

Your program should output, for each load case:
- $R_A, R_B$
- $V(x)$ and $M(x)$ plots with units
- $I_z(x)$ and $S_z(x)$ plots
- Geometry/profile plots in frontal and top views
- $\sigma_{vm}(x)$ and $\mathrm{FoS}(x)$ plots
- $\theta_z(x)$ and $v(x)$ plots
- Beam weight
- Pass/fail summary vs constraints

---

## Suggested Next Build Step

Create a single analysis workbook/script with two tabs/modules:
- `load_case_1`
- `load_case_2`

Both should call the same geometry/property functions so optimization is consistent across loading conditions.
