# Beam Optimization Report

## Search Summary

- Search method: stratified global sampling with elite local refinement
- Total evaluated designs: 3300
- Feasible designs found: 1434
- Minimum required factor of safety: 1.500
- Objective shaping: penalize excess FoS margin and underutilized stress envelope so the design approaches the 1.5 target more closely
- Maximum allowed deflection: not enforced in this run
- Random seed: 2440

## Best Design

- Weight: 0.01967 lbf
- Minimum factor of safety: 1.631
- Excess FoS above target: 0.131
- Governing minimum-FoS load case: Load Case 2 at x = 5.500 in
- Maximum deflection: 0.09100 in
- Uniformity score toward FoS target (0 is best): 0.323573
- Symmetry score (0 is best): 0.000001
- Smoothness score (0 is best): 0.027209
- Durability score (0 is best): 0.000000
- Constraint status: feasible

### Geometry Variables

| Variable | Value |
| --- | ---: |
| Support span $L$ [in] | 8.000 |
| Total beam length $L_{total}$ [in] | 9.000 |
| Support A $x_A$ [in] | 0.500 |
| Support B $x_B$ [in] | 8.500 |
| $b_L$ [in] | 0.312 |
| $b_M$ [in] | 0.543 |
| $b_R$ [in] | 0.312 |
| $h_L$ [in] | 0.451 |
| $h_M$ [in] | 0.754 |
| $h_R$ [in] | 0.451 |
| $t$ [in] | 0.040 |
| $r_L$ [-] | 0.570 |
| $r_M$ [-] | 0.729 |
| $r_R$ [-] | 0.570 |
| $E_{eff}$ [psi] | 297500.0 |
| $\sigma_{allow,eff}$ [psi] | 2380.0 |

### Best-Design Load-Case Metrics

| Load Case | Orientation | Load [lbf] | From Support A [in] | Global x [in] | Min FoS | FoS x [in] | Max Deflection [in] | Max von Mises [psi] |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Load Case 1 | upright | 5.000 | 4.000 | 4.500 | 3.786 | 4.500 | 0.03664 | 628.6 |
| Load Case 2 | side | 8.000 | 5.000 | 5.500 | 1.631 | 5.500 | 0.09100 | 1459.2 |

## Beam Structure and Parameters

![Beam parameter map](beam_parameter_map.png)

![Outer dimension views](best_design/outer_dimension_views.png)

## General Equations

Profiles below are parameterized over the total beam length $0 \le x \le 9.000$ in, while load positions $a$ remain measured from support A.

### Geometry

- $$b(x)=\begin{cases}0.3123 + (0.0514)x, & 0 \le x \le 4.5000\\0.5434 + (-0.0514)(x-4.5000), & 4.5000 < x \le 9.0000\end{cases}$$
- $$h(x)=\begin{cases}0.4510 + (0.0673)x, & 0 \le x \le 4.5000\\0.7540 + (-0.0673)(x-4.5000), & 4.5000 < x \le 9.0000\end{cases}$$
- $$r(x)=\begin{cases}0.5704 + (0.0352)x, & 0 \le x \le 4.5000\\0.7286 + (-0.0352)(x-4.5000), & 4.5000 < x \le 9.0000\end{cases}$$
- Hollow tube area with lightening openings: $A(x)=2b(x)t + [1-r(x)]2t[h(x)-2t]$
- Upright bending second moment: $I(x)=\frac{b(x)h(x)^3-[b(x)-2t][h(x)-2t]^3}{12}-2\frac{t[r(x)(h(x)-2t)]^3}{12}$
- Side-rotated bending second moment: $I_{side}(x)=\frac{h(x)b(x)^3-[h(x)-2t][b(x)-2t]^3}{12}-2\frac{t[r(x)(b(x)-2t)]^3}{12}$
- Section modulus: $S(x)=I(x)/c(x)$ with $c(x)=\text{outer vertical dimension}/2$

### Statics and Stress

- Reactions for a point load $P$ at $x=a$: $R_A=P(L-a)/L$, $R_B=Pa/L$
- Shear and moment: $V(x)$ and $M(x)$ are computed piecewise from the reactions and applied load
- Bending stress: $\sigma_b(x)=|M(x)|/S(x)$
- Shear stress estimate: $\tau(x)=|V(x)|/A_{shear}(x)$ with $A_{shear}(x)=[1-r(x)]2t\,h_{clear}(x)$ for the active orientation
- von Mises stress: $\sigma_{vm}(x)=\sqrt{\sigma_b(x)^2+3\tau(x)^2}$
- Factor of safety: $FoS(x)=\sigma_{allow,eff}/\sigma_{vm}(x)$

### Deflection and Objective

- Euler-Bernoulli relation: $E_{eff}I(x)v''(x)=M(x)$
- Weight objective: $W=\rho\int_0^{L_{total}} A(x)\,dx$
- Search objective used here: minimize weight while enforcing factor-of-safety and optional deflection constraints

## Automatic Equation Substitution

### Effective Material Properties

- $E_{eff} = E \times k_{orientation} \times k_{infill} = 500000.0 \times 0.700 \times 0.850 = 297500.0\ \text{psi}$
- $\sigma_{allow,eff} = \sigma_{allow} \times k_{orientation} \times k_{infill} = 4000.0 \times 0.700 \times 0.850 = 2380.0\ \text{psi}$
- Support positions: $x_A = 0.500\ \text{in}$, $x_B = 8.500\ \text{in}$
- $W = \rho \int_0^{L_{total}} A(x)\,dx = 0.01967\ \text{lbf}$
- Global governing factor of safety is the minimum value over all beam stations and over both load cases.

### Load Case 1

- Active bending orientation: upright (upright section properties)
- Load position from support A: $a = 4.000\ \text{in}$ (global $x = 4.500\ \text{in}$)
- $R_A = P(L-a)/L = 5.000(8.000-4.000)/8.000 = 2.500\ \text{lbf}$
- $R_B = Pa/L = 5.000(4.000)/8.000 = 2.500\ \text{lbf}$
- $FoS_{min} = \sigma_{allow,eff}/\sigma_{vm,max} = 2380.0/628.6 = 3.786$
- Governing location for this load case: $x = 4.500\ \text{in}$
- $\max |v(x)| = 0.03664\ \text{in}$
- $\max |\theta(x)| = 0.015609\ \text{rad}$

### Load Case 2

- Active bending orientation: side (side-rotated section properties)
- Load position from support A: $a = 5.000\ \text{in}$ (global $x = 5.500\ \text{in}$)
- $R_A = P(L-a)/L = 8.000(8.000-5.000)/8.000 = 3.000\ \text{lbf}$
- $R_B = Pa/L = 8.000(5.000)/8.000 = 5.000\ \text{lbf}$
- $FoS_{min} = \sigma_{allow,eff}/\sigma_{vm,max} = 2380.0/1459.2 = 1.631$
- Governing location for this load case: $x = 5.500\ \text{in}$
- $\max |v(x)| = 0.09100\ \text{in}$
- $\max |\theta(x)| = 0.043954\ \text{rad}$


## Automatic Trail of Tried Designs

- Full design study table: `design_study.csv`
- Best design record: `best_design.json`
- Best-design plots folder: `best_design/`
