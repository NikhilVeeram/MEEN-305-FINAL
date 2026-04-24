# Print Settings Record

Generated on 2026-04-24 for the weight-ranked `best-designs-20` beam prints.

These settings are part of the experimental definition. Use the same profile for the printed test set so measured mass, stiffness, and failure behavior are comparable across candidates.

Actual current print/test set: only ranks 02, 03, and 04 were printed. Rank 02 is the expected best candidate if it survives testing, because it is the lightest printed beam.

## Import And Scale

- Import file type: `.stl` from `best-designs-20/3d-models/`
- Slicer scale: `2540%` uniform scale, or set X length to `228.6 mm`
- Reason: the generated STL/OBJ coordinates are in inches, and most slicers import unitless mesh files as millimeters.
- Expected final length: `9.000 in` = `228.6 mm`
- Keep scale locked uniformly in X/Y/Z.
- Preferred print orientation: use `best-designs-20/3d-models-print-oriented/`, which rotates the tube `45 deg` about the 9 in beam length.
- Backup manual orientation: if using files from `best-designs-20/3d-models/`, rotate the part `45 deg` about the long X axis after scaling.
- Actual first supported slice record: supports were included, but the support strategy should still be reduced or removed where practical because trapped internal supports can change measured mass and strength.

For the printed rank 02/03/04 candidates after correct scaling:

- Rank 02 maximum height/width: about `17.08 mm` / `10.60 mm`
- Rank 03 maximum height/width: about `17.99 mm` / `11.33 mm`
- Rank 04 maximum height/width: about `21.65 mm` / `14.22 mm`
- modeled wall thickness: about `1.52-1.53 mm`

## Recommended Slicer Profile

Printer/process context:

- Printer: Creality K1 with `0.4 mm` nozzle
- Process base: `0.20mm Standard @Creality K1 (0.4 nozzle)`
- Filament: `RPS Settings - HF PLA`
- Supports: actual supported test included supports; next iteration should try to eliminate them or restrict them to removable external/build-plate contact only.
- If the slicer still insists on support, use support blockers inside the tube.
- Raft: off
- Brim: on, `3-5 mm`, removed before weighing

Quality:

- Layer height: `0.20 mm`
- First layer height: `0.20 mm`
- Seam: aligned/back corner, not random

Strength:

- Wall loops: `3`
- Top shell layers: `5`
- Top shell thickness: `1.0 mm`
- Top surface density: `100%`
- Bottom shell layers: `5`
- Bottom shell thickness: `1.0 mm`
- Bottom surface density: `100%`
- Sparse infill density: `100%`
- Sparse infill pattern: monotonic for the actual supported test
- Internal solid infill pattern: monotonic

Temperature and cooling:

- Nozzle: use the calibrated HF PLA value; starting target `220 C`
- Bed: `55-60 C`
- Part cooling: high after the first few layers
- Bridge speed: `25-35 mm/s` if editable

Speed guidance:

- Actual supported test kept the base profile speeds unchanged.
- For future controlled comparisons, either keep speed unchanged for every beam or record any speed edits explicitly.

## Why These Settings

The structural model assumes the printed tube walls are contiguous solid material. The top designs use roughly `0.060 in` wall thickness, which is about `1.52 mm`; with a `0.4 mm` nozzle, `3` wall loops plus solid internal fill should make the modeled walls continuous without intentionally filling the hollow beam cavity.

The original as-designed orientation can trigger a floating-cantilever warning because the top wall of a closed tube is treated as a long bridge over the hollow interior. The `45 deg` diamond print orientation turns that roof bridge into gradually supported angled walls, while keeping the beam geometry and test dimensions unchanged.

Do not use `15%` sparse infill for the print-test beams. It makes the actual wall behavior depend on the slicer infill pattern instead of the optimized beam geometry.

## Measurement Record

For each printed test beam, record:

- candidate filename
- slicer scale confirmation: `2540%` or X = `228.6 mm`
- support setting used, including whether supports were internal, external-only, or blocked inside the tube
- infill/surface pattern used; first supported slice used monotonic throughout
- speed profile used; first supported slice kept the base profile speeds unchanged
- printed mass after brim removal
- print time
- visible defects, seams, gaps, or bridge sag
- test orientation and load case
- failure load and failure location
