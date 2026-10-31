#!/usr/bin/env python3
"""build_v2_axle.py - v2 side axle D40x300 + D40 shaft collar.

Fixes found in the 2026-10-29 audit:
  * axle was L240: only 17 mm engaged in the 50 mm UCFL208 bearing bore
  * keyways were at +-44..76 from centre, matching neither the 48T wheel
    (y=140) nor the 72z sprocket hub (y=238..282)
  * 48T wheel had no axial stop; 72z hub could walk on the axle

Datum for the keyway stations: axle centre = track centre (y=+-260).
48T chain plane y=140 (25 mm hub 132..157, butts inner plate)
72z hub y=238..282 (44 long, sprocket pack 252..268)

KEYWAYS (global y, R side): 142..157 and 238..282, 12JS9 x 5 deep.
Local z = 260 - y, so: z = 103..118 and z = -22..+22.
The L axle is the same solid rotated -90 about X (see freecad_build.py),
which mirrors the keyway stations to y=-136..-155 / -238..-282.
"""
import pathlib
from build123d import Align, Axis, Box, Cylinder, Location, export_step

ROOT = pathlib.Path(__file__).resolve().parent
D, L = 40.0, 300.0
KW, KD = 12.0, 5.0

axle = Cylinder(D / 2, L, align=(Align.CENTER, Align.CENTER, Align.CENTER))

for z0, z1 in ((-22.0, 22.0), (103.0, 118.0)):
    # end-mill slot along Z: straight centre + 2 x R6 ends, 5 deep from OD
    cut = Box(KD, KW, (z1 - z0) - KW,
              align=(Align.MIN, Align.CENTER, Align.CENTER))
    cut = cut.moved(Location((D / 2 - KD, 0, (z0 + z1) / 2)))
    for zc in (z0 + KW / 2, z1 - KW / 2):
        end = Cylinder(KW / 2, KD,
                       align=(Align.CENTER, Align.CENTER, Align.CENTER))
        end = end.rotate(Axis.Y, 90).moved(Location((D / 2 - KD / 2, 0, zc)))
        cut += end
    axle -= cut

axle = axle.clean()
export_step(axle, str(ROOT / "side_axle.step"))
print("axle volume cm3", round(axle.volume / 1000, 2),
      "mass kg", round(axle.volume * 7850e-9, 3))

# COTS-style clamp collar D40, OD60 x 12, radial M6 grub
col = Cylinder(30, 12, align=(Align.CENTER, Align.CENTER, Align.CENTER)) - \
      Cylinder(20, 12, align=(Align.CENTER, Align.CENTER, Align.CENTER))
# radial M6 grub hole at +X (axis along X, cut through the wall)
grub = Cylinder(3, 40, align=(Align.CENTER, Align.CENTER, Align.CENTER))
grub = grub.rotate(Axis.Y, 90).moved(Location((15, 0, 0)))
col -= grub
export_step(col, str(ROOT / "collar_D40_OD60.step"))
print("collar volume cm3", round(col.volume / 1000, 2),
      "mass kg", round(col.volume * 7850e-9, 3))
