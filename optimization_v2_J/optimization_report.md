# Beam Optimization Report

## Search Summary

- Search method: stratified global sampling with elite local refinement
- Total evaluated designs: 1200
- Feasible designs found: 687
- Minimum required factor of safety: 1.500
- Objective shaping: penalize excess FoS margin and underutilized stress envelope so the design approaches the 1.5 target more closely
- Maximum allowed deflection: not enforced in this run
- Random seed: 9999

## Best Design

- Weight: 0.02655 lbf
- Minimum factor of safety: 1.549
- Excess FoS above target: 0.049
- Governing minimum-FoS load case: Load Case 1 at x = 4.000 in
- Maximum deflection: 0.08478 in
- Constraint status: feasible

### Geometry Variables

| Variable | Value |
| --- | ---: |
| $L$ [in] | 8.000 |
| $L_{total}$ [in] | 9.000 |
| $b_L$ [in] | 0.350 |
| $b_M$ [in] | 0.350 |
| $b_R$ [in] | 0.512 |
| $h_L$ [in] | 0.809 |
| $h_M$ [in] | 0.380 |
| $h_R$ [in] | 0.741 |
| $t$ [in] | 0.060 |
| $r_L$ [-] | 0.712 |
| $r_M$ [-] | 0.412 |
| $r_R$ [-] | 0.445 |
| $E_{eff}$ [psi] | 297500.0 |
| $\sigma_{allow,eff}$ [psi] | 2380.0 |

### Best-Design Load-Case Metrics

| Load Case | Orientation | Load [lbf] | Location [in] | Min FoS | FoS x [in] | Max Deflection [in] | Max von Mises [psi] |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Load Case 1 | upright | 5.000 | 4.000 | 1.549 | 4.000 | 0.08478 | 1536.6 |
| Load Case 2 | side | 3.000 | 2.500 | 3.598 | 2.490 | 0.06091 | 661.6 |

## Beam Structure and Parameters

![Beam parameter map](beam_parameter_map.png)

![Outer dimension views](best_design/outer_dimension_views.png)

## General Equations

### Geometry

- $$b(x)=\begin{cases}0.3500 + (0.0000)x, & 0 \le x \le 4.0000\\0.3500 + (0.0405)(x-4.0000), & 4.0000 < x \le 8.0000\end{cases}$$
- $$h(x)=\begin{cases}0.8089 + (-0.1072)x, & 0 \le x \le 4.0000\\0.3800 + (0.0902)(x-4.0000), & 4.0000 < x \le 8.0000\end{cases}$$
- $$r(x)=\begin{cases}0.7119 + (-0.0751)x, & 0 \le x \le 4.0000\\0.4116 + (0.0083)(x-4.0000), & 4.0000 < x \le 8.0000\end{cases}$$
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
- Weight objective: $W=\rho\int_0^L A(x)\,dx$
- Search objective used here: minimize weight while enforcing factor-of-safety and optional deflection constraints

## Automatic Equation Substitution

### Effective Material Properties

- $E_{eff} = E \times k_{orientation} \times k_{infill} = 500000.0 \times 0.700 \times 0.850 = 297500.0\ \text{psi}$
- $\sigma_{allow,eff} = \sigma_{allow} \times k_{orientation} \times k_{infill} = 4000.0 \times 0.700 \times 0.850 = 2380.0\ \text{psi}$
- $W = \rho \int_0^L A(x)\,dx = 0.02655\ \text{lbf}$
- Global governing factor of safety is the minimum value over all beam stations and over both load cases.

### Load Case 1

- Active bending orientation: upright (upright section properties)
- $R_A = P(L-a)/L = 5.000(8.000-4.000)/8.000 = 2.500\ \text{lbf}$
- $R_B = Pa/L = 5.000(4.000)/8.000 = 2.500\ \text{lbf}$
- $FoS_{min} = \sigma_{allow,eff}/\sigma_{vm,max} = 2380.0/1536.6 = 1.549$
- Governing location for this load case: $x = 4.000\ \text{in}$
- $\max |v(x)| = 0.08478\ \text{in}$
- $\max |\theta(x)| = 0.027722\ \text{rad}$

### Load Case 2

- Active bending orientation: side (side-rotated section properties)
- $R_A = P(L-a)/L = 3.000(8.000-2.500)/8.000 = 2.062\ \text{lbf}$
- $R_B = Pa/L = 3.000(2.500)/8.000 = 0.938\ \text{lbf}$
- $FoS_{min} = \sigma_{allow,eff}/\sigma_{vm,max} = 2380.0/661.6 = 3.598$
- Governing location for this load case: $x = 2.490\ \text{in}$
- $\max |v(x)| = 0.06091\ \text{in}$
- $\max |\theta(x)| = 0.025554\ \text{rad}$


## Automatic Trail of Tried Designs

- Full design study table: `design_study.csv`
- Best design record: `best_design.json`
- Best-design plots folder: `best_design/`
