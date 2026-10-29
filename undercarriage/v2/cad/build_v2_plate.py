#!/usr/bin/env python3
"""build_v2_plate.py - side plate solid from plate_holes.json (STEP for mass/CAD).

Mirrors freecad_build.py cuts so side_plate.step and the FCStd plate agree.
Run plate_dxf.py after any JSON change for the laser DXF.
"""
import json, pathlib
from build123d import (
    Align, Box, Cylinder, Location, Polyline, export_step, extrude, make_face,
)

ROOT = pathlib.Path(__file__).resolve().parent
spec = json.loads((ROOT / "plate_holes.json").read_text())
P = spec["plate"]
T = P["T"]

plate = extrude(make_face(Polyline(*[(x, y) for x, y in P["outline"]],
                                  close=True)), T)

ZMIN = (Align.CENTER, Align.CENTER, Align.MIN)


def hole(x, y, d):
    return (Location((x, y, -1)) * Cylinder(d / 2, T + 2, align=ZMIN))


for h in spec["holes"]:
    t = h["t"]
    if t in ("roller", "axle", "gusset14"):
        for x, y in h["xy"]:
            plate -= hole(x, y, h["d"])
    elif t == "vslot":
        r = h["w"] / 2
        for s in h["slots"]:
            L = s["y1"] - s["y0"]
            x = s["x"]
            plate -= (Location((x, (s["y0"] + s["y1"]) / 2, -1)) *
                      Box(h["w"], L - h["w"], T + 2,
                          align=(Align.CENTER, Align.CENTER, Align.MIN)))
            plate -= hole(x, s["y0"] + r, h["w"])
            plate -= hole(x, s["y1"] - r, h["w"])
    elif t == "idler_slot":
        r = h["w"] / 2
        x, y = h["x"], h["y"]
        plate -= (Location((x + h["travel"] / 2, y, -1)) *
                  Box(h["travel"] - h["w"], h["w"], T + 2,
                      align=(Align.CENTER, Align.CENTER, Align.MIN)))
        plate -= hole(x, y, h["w"])
        plate -= hole(x + h["travel"], y, h["w"])

for p in spec["pockets"]:
    r = p["obround"]
    rh = (p["y2"] - p["y1"]) / 2
    ym = (p["y1"] + p["y2"]) / 2
    plate -= (Location(((p["x1"] + p["x2"]) / 2, ym, -1)) *
              Box(p["x2"] - p["x1"] - 2 * r, 2 * rh, T + 2,
                  align=(Align.CENTER, Align.CENTER, Align.MIN)))
    plate -= (Location((p["x1"] + r, ym, -1)) *
              Cylinder(rh, T + 2, align=ZMIN))
    plate -= (Location((p["x2"] - r, ym, -1)) *
              Cylinder(rh, T + 2, align=ZMIN))

plate = plate.clean()
export_step(plate, str(ROOT / "side_plate.step"))
print("side_plate.step volume cm3", round(plate.volume / 1000, 2),
      "mass kg", round(plate.volume * 7850e-9, 3))
