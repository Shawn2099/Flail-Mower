#!/usr/bin/env python3
"""laser_set.py - remaining laser DXFs (single-purpose, parametric)."""
import math, pathlib
root = pathlib.Path(__file__).resolve().parent

def dxf_open(f): f.write("0\nSECTION\n2\nENTITIES\n")
def dxf_close(f, note):
    f.write(f"0\nTEXT\n8\nNOTES\n10\n-100.0\n20\n-60.0\n30\n0.0\n40\n5.0\n1\n{note}\n")
    f.write("0\nENDSEC\n0\nEOF\n")
def circle(f, x, y, r):
    f.write(f"0\nCIRCLE\n8\n0\n10\n{x:.2f}\n20\n{y:.2f}\n30\n0.0\n40\n{r:.2f}\n")
def line(f, x1, y1, x2, y2):
    f.write(f"0\nLINE\n8\n0\n10\n{x1:.2f}\n20\n{y1:.2f}\n30\n0.0\n11\n{x2:.2f}\n21\n{y2:.2f}\n31\n0.0\n")
def ring(name, od, idd, t, note, notch=None):
    with open(root / f"{name}.dxf", "w") as f:
        dxf_open(f); circle(f, 0, 0, od / 2); circle(f, 0, 0, idd / 2)
        if notch:  # keyway notch in bore (laser, finish at outsource)
            w, d = notch
            line(f, -w/2, 0, -w/2, d); line(f, w/2, 0, w/2, d); line(f, -w/2, d, w/2, d)
        dxf_close(f, f"{note} {t}MM - QTY ON BOM")
def rect_holes(name, sx, sy, holes, note):
    with open(root / f"{name}.dxf", "w") as f:
        dxf_open(f)
        x0, y0 = -sx/2, -sy/2
        for a, b in [((x0,y0),(x0+sx,y0)),((x0+sx,y0),(x0+sx,y0+sy)),((x0+sx,y0+sy),(x0,y0+sy)),((x0,y0+sy),(x0,y0))]:
            line(f, a[0],a[1],b[0],b[1])
        for x, y, d in holes: circle(f, x, y, d/2)
        dxf_close(f, note)

ring("backplate_roller_OD1053_ID65_6mm", 105.3, 65, 6,
     "ROLLER BACKPLATE x12 - weld inside 100NB pipe")
ring("backplate_idler_OD190_ID65_6mm", 190.0, 65, 6,
     "IDLER BACKPLATE x4 - weld inside 200 OD tube")
ring("cheek_OD114_ID65_6mm", 114.3, 65, 6, "ROLLER CHEEK x24 (old v2)")
ring("ring_D200_ID150_8mm", 200, 150, 8, "IDLER RING x20")
ring("hub76_ID42_8mm", 76, 42, 8, "SPROCKET HUB RING x12 (stack 44 + keyway at outsource)", notch=(12, 8))
ring("hub65_ID52_8mm", 65, 52, 8, "DISC HUB RING (5/disc, Loctite 638)")
rect_holes("flange_mid_140x70_8mm", 140, 70, [(-50,-15,14),(50,-15,14),(-50,15,14),(50,15,14)], "FLANGE x6 - MID+REAR 4xD14 (weld to SHS40 end, bolt M12x4)")
rect_holes("flange_front_50x70_8mm", 50, 70, [(0,-15,14),(0,15,14)], "FLANGE-FRONT x2 - 2xD14 (weld to SHS40 end, bolt M12x2)")
# guard: 140 x 270 flat, 3 vent slots 80 x 8 (rounded ends)
with open(root / "guard_flat_1p5mm.dxf", "w") as f:
    dxf_open(f)
    sx, sy = 140, 270
    x0, y0 = -sx / 2, -sy / 2
    for a, b in [((x0, y0), (x0 + sx, y0)), ((x0 + sx, y0), (x0 + sx, y0 + sy)),
                 ((x0 + sx, y0 + sy), (x0, y0 + sy)), ((x0, y0 + sy), (x0, y0))]:
        line(f, a[0], a[1], b[0], b[1])
    for cy in (-60, 0, 60):
        r = 4
        line(f, -40, cy - r, 40, cy - r)
        line(f, -40, cy + r, 40, cy + r)
        f.write(f"0\nARC\n8\n0\n10\n-40.00\n20\n{cy:.2f}\n30\n0.0\n40\n4.00\n50\n90.0\n51\n270.0\n")
        f.write(f"0\nARC\n8\n0\n10\n40.00\n20\n{cy:.2f}\n30\n0.0\n40\n4.00\n50\n270.0\n51\n90.0\n")
    dxf_close(f, "CHAIN GUARD x2 - 140x270x1.5 - 3 VENT SLOTS 80x8 - BEND AT FIT-UP")
print("laser set done")
