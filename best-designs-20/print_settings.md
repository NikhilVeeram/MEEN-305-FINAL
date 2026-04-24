# Print Settings Record

Generated on 2026-04-24 for the weight-ranked `best-designs-20` beam prints.

These settings are part of the experimental definition. Use the same profile for the print-test shortlist so measured mass, stiffness, and failure behavior are comparable across candidates.

## Import And Scale

- Import file type: `.stl` from `best-designs-20/3d-models/`
- Slicer scale: `2540%` uniform scale, or set X length to `228.6 mm`
- Reason: the generated STL/OBJ coordinates are in inches, and most slicers import unitless mesh files as millimeters.
- Expected final length: `9.000 in` = `228.6 mm`
- Keep scale locked uniformly in X/Y/Z.
- Print orientation: as exported, with the 9 in beam length along the bed and the structural height in Z.

For Rank 01 after correct scaling:

- maximum height: about `15.41 mm`
- maximum width: about `11.85 mm`
- modeled wall thickness: about `1.54 mm`

## Recommended Slicer Profile

Printer/process context:

- Printer: Creality K1 with `0.4 mm` nozzle
- Process base: `0.20mm Standard @Creality K1 (0.4 nozzle)`
- Filament: `RPS Settings - HF PLA`
- Supports: off
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
- Sparse infill pattern: rectilinear/lines if available; otherwise monotonic
- Internal solid infill pattern: monotonic

Temperature and cooling:

- Nozzle: use the calibrated HF PLA value; starting target `220 C`
- Bed: `55-60 C`
- Part cooling: high after the first few layers
- Bridge speed: `25-35 mm/s` if editable

Speed guidance:

- Outer walls: about `60 mm/s`
- Inner walls: about `80-100 mm/s`
- Solid infill: about `80 mm/s`
- Avoid very high-speed defaults for the test parts; strength and dimensional consistency matter more than print time here.

## Why These Settings

The structural model assumes the printed tube walls are contiguous solid material. The top designs use roughly `0.060 in` wall thickness, which is about `1.52 mm`; with a `0.4 mm` nozzle, `3` wall loops plus solid internal fill should make the modeled walls continuous without intentionally filling the hollow beam cavity.

Do not use `15%` sparse infill for the print-test beams. It makes the actual wall behavior depend on the slicer infill pattern instead of the optimized beam geometry.

## Measurement Record

For each printed shortlist beam, record:

- candidate filename
- slicer scale confirmation: `2540%` or X = `228.6 mm`
- printed mass after brim removal
- print time
- visible defects, seams, gaps, or bridge sag
- test orientation and load case
- failure load and failure location
