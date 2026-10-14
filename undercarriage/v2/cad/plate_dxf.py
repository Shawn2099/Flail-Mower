#!/usr/bin/env python3
"""plate_dxf.py - SINGLE SOURCE plate_holes.json -> side_plate.dxf (v2 frozen plate)."""
import json, math, pathlib
root = pathlib.Path(__file__).resolve().parent
spec = json.loads((root / "plate_holes.json").read_text())
P = spec["plate"]
lines, circles, arcs = [], [], []
pts = P["outline"]
for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
    lines.append((x1, y1, x2, y2))
for h in spec["holes"]:
    t = h["t"]
    if t in ("roller", "axle", "gusset14"):
        for x, y in h["xy"]: circles.append((x, y, h["d"] / 2))
    elif t == "vslot":
        for s in h["slots"]:
            x, r = s["x"], h["w"] / 2
            lines.append((x - r, s["y0"] + r, x - r, s["y1"] - r))
            lines.append((x + r, s["y0"] + r, x + r, s["y1"] - r))
            arcs.append((x, s["y0"] + r, r, 180, 360)); arcs.append((x, s["y1"] - r, r, 0, 180))
    elif h["t"] == "idler_slot":
        x, y, r = h["x"], h["y"], h["w"] / 2
        lines.append((x, y - r, x + h["travel"], y - r))
        lines.append((x, y + r, x + h["travel"], y + r))
        arcs.append((x, y, r, 90, 270)); arcs.append((x + h["travel"], y, r, 270, 90))
for p in spec["pockets"]:
    r = p["obround"]
    lines.append((p["x1"] + r, p["y1"], p["x2"] - r, p["y1"]))
    lines.append((p["x1"] + r, p["y2"], p["x2"] - r, p["y2"]))
    arcs.append((p["x1"] + r, (p["y1"] + p["y2"]) / 2, (p["y2"] - p["y1"]) / 2, 90, 270))
    arcs.append((p["x2"] - r, (p["y1"] + p["y2"]) / 2, (p["y2"] - p["y1"]) / 2, 270, 90))
with open(root / "side_plate.dxf", "w") as f:
    f.write("0\nSECTION\n2\nENTITIES\n")
    for x1, y1, x2, y2 in lines:
        f.write(f"0\nLINE\n8\n0\n10\n{x1:.2f}\n20\n{y1:.2f}\n30\n0.0\n11\n{x2:.2f}\n21\n{y2:.2f}\n31\n0.0\n")
    for cx, cy, r in circles:
        f.write(f"0\nCIRCLE\n8\n0\n10\n{cx:.2f}\n20\n{cy:.2f}\n30\n0.0\n40\n{r:.2f}\n")
    for cx, cy, r, a0, a1 in arcs:
        f.write(f"0\nARC\n8\n0\n10\n{cx:.2f}\n20\n{cy:.2f}\n30\n0.0\n40\n{r:.2f}\n50\n{a0:.1f}\n51\n{a1:.1f}\n")
    f.write(f"0\nTEXT\n8\nNOTES\n10\n-600.0\n20\n-30.0\n30\n0.0\n40\n6.0\n1\n{spec['etch']}\n")
    f.write(f"0\nTEXT\n8\nNOTES\n10\n-600.0\n20\n250.0\n30\n0.0\n40\n6.0\n1\nCORNERS R15 LASER + {P['corners']}\n")
    f.write("0\nENDSEC\n0\nEOF\n")
print(f"side_plate.dxf: outline {len(P['outline'])}pt, {len(circles)} holes, {len(arcs)} arcs")
