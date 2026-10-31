#!/usr/bin/env python3
"""build_v2_idler.py - connected D200 idler disc.

Audit 2026-10-29: 5 tread rings OD200/ID150 + a 65/52 hub had NO structural
connection between r75 and r32.5. Replace the middle ring with an 8 mm web
OD150/ID65: 4 rings (32) + web (8) = 40 overall, same tread width and mass,
hub welded to the web, web welded to the ring stack.

Outputs: idler_web.step, idler_ring.step (unchanged), idler_disc.step (union
for mass/view), web_D200_ID65_8mm.dxf (laser).
"""
import pathlib
import ezdxf
from build123d import Align, Cylinder, Location, export_step

ROOT = pathlib.Path(__file__).resolve().parent


def ring(od, id_, t):
    return Cylinder(od / 2, t, align=(Align.CENTER, Align.CENTER, Align.CENTER)) - \
           Cylinder(id_ / 2, t, align=(Align.CENTER, Align.CENTER, Align.CENTER))


def at(shape, z):
    return shape.moved(Location((0, 0, z)))


ring8 = ring(200, 150, 8)
web6 = ring(150, 65, 6)
hub = ring(65, 52, 40)

parts = []
for z in (16, 8, 0, -8, -16):       # 5 rings, 8 mm each = 40 tread
    parts.append(at(ring8, z))
parts.append(at(web6, 0))           # web 150/65 x6 inside the bore, centred
parts.append(at(hub, 0))            # hub 65/52 x40
assy = parts[0]
for p in parts[1:]:
    assy = assy + p
assy = assy.clean()

export_step(ring8, str(ROOT / "idler_ring.step"))
export_step(web6, str(ROOT / "idler_web.step"))
export_step(assy, str(ROOT / "idler_disc.step"))
print("ring", round(ring8.volume / 1000, 2), "web", round(web6.volume / 1000, 2),
      "assy kg", round(assy.volume * 7850e-9, 3))

doc = ezdxf.new("R2010")
msp = doc.modelspace()
for od, id_ in ((200, 150), (150, 65)):
    msp.add_circle((0, 0), od / 2)
    msp.add_circle((0, 0), id_ / 2)
msp.add_text("IDLER WEB D200/ID65 x6 - E250 - 4 OFF",
             dxfattribs={"height": 6}).set_placement((-60, -110))
doc.saveas(ROOT / "web_D200_ID65_8mm.dxf")
print("wrote web DXF")
