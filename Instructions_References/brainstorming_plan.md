# MEEN 305 Project Brainstorming + Action Outline

## 1) What You Are Really Being Graded On

Primary technical criterion (your focus):
- Did we identify the relevant equations?
- Did we connect those equations correctly into one coherent model?
- Did we use that model to make optimization decisions (not just compute one-off numbers)?

Execution criterion:
- Did the final printed design reflect the model assumptions and constraints?
- Was print orientation/infill/material choice handled intentionally?

## 2) Project Mindset (Equation-First)

Treat this as a coupled design problem:
- Mechanics equations predict performance/failure.
- Geometry variables control those equations.
- Print/manufacturing choices modify effective behavior.
- Optimization is selecting variables to maximize your chosen objective while satisfying constraints.

## 3) Core Modeling Skeleton (Fill in With Class Equations)

Build your model in this order:

1. Define design variables
- Cross-section dimensions (for example: b, h, wall thickness)
- Span/length choices if allowed
- Print settings affecting effective properties (infill %, orientation category)

2. Define loads and boundary conditions
- Force type, application location, support condition
- Any limits from test setup/rules

3. Write governing equations (from your equation sheet/class)
- Internal reactions (statics)
- Shear V(x), moment M(x)
- Bending stress relation
- Shear stress relation if needed
- Deflection relation and limits
- Buckling/stability relation if relevant
- Failure criterion (maximum stress, factor of safety, etc.)

4. Map geometry -> section properties
- Area A
- Second moment of area I
- Section modulus S
- Distance to extreme fiber c

5. Map print choices -> material/effective properties
- E_eff and strength_eff assumptions by orientation/infill
- Conservative reduction factors for layer-line weakness

6. Define objective function
- Maximize allowable load before failure, OR
- Minimize mass for required load, OR
- Maximize stiffness-to-weight ratio

7. Define constraints
- Stress <= allowable
- Deflection <= allowable
- Buckling safety >= required
- Geometry/build volume limits
- Print-time/credit constraints

## 4) Equation-Integration Checklist (Most Important)

Use this as your "did we connect everything" checklist:
- Loads -> reactions done from statics.
- Reactions -> V(x), M(x) done.
- M_max feeds bending stress equation.
- Geometry feeds I, c, and therefore bending stress.
- Geometry and E_eff feed deflection equation.
- If slender members exist, geometry and E_eff feed buckling check.
- Allowable stress/strength adjusted for print orientation/infill assumptions.
- Governing failure mode identified (stress, deflection, buckling, layer-line delamination, etc.).
- Objective/constraint setup matches the identified governing mode.

If one arrow in this chain is missing, the model is incomplete.

## 5) Optimization Strategy (Practical)

Start simple and escalate:

Phase A: Baseline hand-calculation model
- One candidate geometry
- Compute stresses/deflection/FOS
- Identify likely governing mode

Phase B: Parametric sweep (spreadsheet or script)
- Sweep key dimensions and maybe infill/orientation category
- Track objective + all constraints for each design
- Produce feasible set

Phase C: Choose finalists
- Pick top 2-3 candidates balancing performance and printability
- Include one "robust" conservative design and one aggressive design

Phase D: Print-informed update
- Adjust model with realistic print assumptions (anisotropy, imperfect bonding)
- Re-rank finalists

## 6) What To Focus On Most (Your First Criterion)

Focus Area 1: Correct equation selection
- Use only relevant equations but cover all plausible failure mechanisms.

Focus Area 2: Equation coupling
- Explicitly show how outputs from one equation become inputs to another.

Focus Area 3: Assumption transparency
- State each assumption (linear elastic, small deflection, effective isotropic/anisotropic treatment).
- Explain expected impact if assumption is wrong.

Focus Area 4: Sensitivity
- Show which variables most influence performance (often h in bending-dominated cases).

Focus Area 5: Governing mode logic
- Clearly justify which criterion actually controls final design.

## 7) Print Reality Considerations to Integrate Into Model

From the RPS guidance:
- PLA is default; keep base model with PLA properties.
- Layer-line direction is a major failure driver.
- Infill affects effective stiffness/strength.

Modeling move:
- Introduce orientation factor k_orient and infill factor k_infill so:
  - E_eff = k_orient * k_infill * E_bulk
  - sigma_allow,eff = k_orient * k_infill * sigma_allow,bulk
- Use conservative ranges if exact data unavailable.

## 8) Concrete Deliverables You Should Prepare

- One-page equation map (flowchart style): load -> internal forces -> stress/deflection -> constraints -> objective.
- Table of symbols/units/assumptions.
- Parametric sweep plots (objective and constraints).
- Final design decision matrix (why winner beats alternatives).
- Print plan: orientation, infill, wall settings, expected failure mode.

## 9) Work Plan You Can Follow This Week

1. Day 1: Gather all governing equations from class + equation sheet and classify by role (stress, deflection, stability, failure).
2. Day 1: Build equation dependency map.
3. Day 2: Build baseline spreadsheet model and verify with one hand-check.
4. Day 3: Run parametric sweep and identify feasible region.
5. Day 4: Down-select 2-3 designs, include print constraints.
6. Day 5: Final model update + print settings selection + documentation polish.

## 10) Questions to Answer Next (Before Final Modeling)

- What is the exact objective required by your instructor (max load? min weight? both)?
- What are fixed vs variable geometric dimensions?
- What are explicit pass/fail constraints from project instructions?
- Is failure judged by load at break, deflection limit, or both?
- Are we expected to include uncertainty/safety factor formally?

---

## Immediate Next Step

Create a project-specific "Equation Dependency Map" with your exact class equations and variable names. Once you share the exact project PDF/equation sheet details, we can turn this brainstorming outline into a complete, equation-by-equation implementation plan.
