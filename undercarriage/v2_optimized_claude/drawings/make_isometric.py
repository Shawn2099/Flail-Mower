#!/usr/bin/env python3
"""make_isometric.py - isometric line projection of the UC-V2 assembly (simplified).

Visible edges only; the near outer plate is removed so both plate pairs and the
running gear can be seen.  Labels are placed on projected feature points.
"""
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from build123d import (
    Align, Axis, Box, Compound, Cylinder, Location, Plane, SlotCenterToCenter,
    extrude,
)

ROOT = pathlib.Path(__file__).resolve().parent
C = 1001.3
RSP = 105.26
ZC = 133.3
TY = 260.0
BELT = 12.0
LUG = 22.0
TRACK_W = 180.0
ROLL_X = (-300.0, 0.0, 300.0)
ROLL_Z = 91.2
ROLL_R = 114.3 / 2
IDL_X = 500.6
WHEEL_Y = 140.0

# projected 2D position of a 3D point for the isometric camera
RX, RY = 0.7071067811865476, 0.7071067811865476
UX, UY, UZ = -0.331294578, 0.331294578, 0.883452208


def proj(p):
    x, y, z = p
    return (RX * x + RY * y, UX * x + UY * y + UZ * z)


def cyl_y(r, w, x, y, z):
    return Cylinder(r, w, align=(Align.CENTER, Align.CENTER, Align.CENTER)
                    ).rotate(Axis.X, 90).moved(Location((x, y, z)))


def track(yc):
    ro = RSP + BELT / 2 + LUG
    ri = RSP - BELT / 2
    outer = Plane.XZ * SlotCenterToCenter(C, 2 * ro)
    inner = Plane.XZ * SlotCenterToCenter(C, 2 * ri)
    face = outer - inner
    band = extrude(face, amount=TRACK_W)
    bb = band.bounding_box()
    # The slot is built on Plane.XZ at z=0; move its loop centre to ZC and
    # centre the 180 mm width on the track centreline yc.
    band = band.moved(Location((0, yc - TRACK_W / 2 - bb.min.Y, ZC)))
    return band


parts = []
# near outer plate (y=-360) omitted; both inners and the far outer are shown
for y in (-160.0, 160.0, 360.0):
    parts.append(Box(1240, 6, 220, align=(Align.CENTER, Align.CENTER, Align.CENTER)
                     ).moved(Location((0, y, 140))))
tracks = []
for yc in (-TY, TY):
    t = track(yc)
    parts.append(t)
    tracks.append(t)
# --- geometry verification: track must sit on ground and surround its wheels ---
RO = RSP + BELT / 2 + LUG
for yc, t in zip((-TY, TY), tracks):
    bb = t.bounding_box()
    print(f"track yc={yc:+.1f}: X {bb.min.X:.2f}..{bb.max.X:.2f} "
          f"Y {bb.min.Y:.2f}..{bb.max.Y:.2f} "
          f"Z {bb.min.Z:.2f}..{bb.max.Z:.2f}")
    assert abs((bb.min.Y + bb.max.Y) / 2 - yc) < 0.01, "track not centred on yc"
    assert abs((bb.min.Z + bb.max.Z) / 2 - ZC) < 0.01, "track loop centre not ZC"
    assert abs(bb.min.Y - (yc - TRACK_W / 2)) < 0.01
    assert abs(bb.max.Y - (yc + TRACK_W / 2)) < 0.01
    assert abs(bb.min.Z) < 0.10, "track not on ground"
    assert abs(bb.max.X - (C / 2 + RO)) < 0.01
    for dy in (-62, 62):
        assert bb.min.Y <= yc + dy <= bb.max.Y, "roller outside track width"
    print(f"  wheel y={yc:+.1f} / {yc-62:+.1f} / {yc+62:+.1f} within track; "
          f"roller bottom z={ROLL_Z-ROLL_R:.2f}, track inner bottom z={ZC-RSP+BELT/2:.2f}")
    assert abs((ROLL_Z - ROLL_R) - (ZC - RSP + BELT / 2)) < 0.05
for yc in (-TY, TY):
    for x in ROLL_X:
        for dy in (-62, 62):
            parts.append(cyl_y(ROLL_R, 40, x, yc + dy, ROLL_Z))
    for dy in (-62, 62):
        parts.append(cyl_y(100, 40, IDL_X, yc + dy, ZC))
    parts.append(cyl_y(RSP, 16, -500.6, yc, ZC))
    parts.append(cyl_y(97.1, 4, -500.6, yc - 120 if yc > 0 else yc + 120, ZC))
    parts.append(cyl_y(20, 240, -500.6, yc, ZC))
    for sy in (-103, 103):
        parts.append(Box(100, 50, 150).moved(Location((-500.6, yc + sy, ZC))))
for y in (-69, 69):
    parts.append(Box(200, 130, 190).moved(Location((-460, y, 345))))
for x in (-150, 150):
    for y in (-100, 100):
        parts.append(Box(80, 80, 20).moved(Location((x, y, 165))))
for y in (-100, 100):
    parts.append(Box(10, 60, 80).moved(Location((-370, y, 170))))
for x, z in ((-386, 190), (-170, 135), (130, 135), (565, 105)):
    parts.append(Box(40, 314, 40).moved(Location((x, 0, z))))
for y in (-120, -40, 40, 120):
    parts.append(Box(300, 40, 40).moved(Location((-475, y, 230))))

assy = Compound(children=parts)
vis, hid = assy.project_to_viewport((1, -1, 0.75), (0, 0, 1), (0, 0, 0))
print("visible", len(vis), "hidden", len(hid))

fig = plt.figure(figsize=(20, 11), facecolor="white")
ax = fig.add_axes([0.02, 0.115, 0.68, 0.815])
for e in vis:
    pts = [e @ (i / 40) for i in range(41)]
    ax.plot([p.X for p in pts], [p.Y for p in pts], "k-", lw=0.8)
ax.set_aspect("equal")
ax.axis("off")
ax.set_xlim(-780, 780)
ax.set_ylim(-480, 690)

# R outer deck is removed; show its location as a light dotted outline so the
# R outer-deck callout has something to point at.
ys = -360.0
corners = [(-620, ys, 30), (620, ys, 30), (620, ys, 250), (-620, ys, 250)]
ax.add_patch(Polygon([proj(p) for p in corners], closed=True, fill=False,
                     ec="0.55", lw=0.8, ls=(0, (4, 3))))

# Numbered balloons sit outside the drawing on a clean perimeter; every leader
# has an arrowhead at the feature.  L = +Y (far side), R = -Y (near side).
callouts = [
    # numbered clockwise around the perimeter: top 1-6, left 7-9, bottom 10-13
    # number, text, feature (x,y,z), balloon (u,v)
    (1, "R MOTOR", (-460, -69, 440), (-650, 640)),
    (2, "L MOTOR", (-460, 69, 440), (-450, 640)),
    (3, "TRACK — 180 × 72 × 37", (0, -260, 266), (-150, 640)),
    (4, "MAIN FRAME", (150, 0, 155), (50, 640)),
    (5, "L INNER SIDE PLATE (Y+)", (400, 160, 245), (250, 640)),
    (6, "L OUTER SIDE PLATE (Y+)", (400, 360, 245), (550, 640)),
    (7, "TRACK SPROCKET 72z9", (-500.6, -260, 133.3), (-740, 400)),
    (8, "ROLLER STATION 1", (-300, -322, 91.2), (-740, 200)),
    (9, "ROLLER STATION 2", (0, -322, 91.2), (-740, 0)),
    (10, "ROLLER STATION 3", (300, -322, 91.2), (-400, -450)),
    (11, "R OUTER SIDE PLATE (Y-) - dotted", (600, -360, 250), (-200, -450)),
    (12, "IDLER STATION", (500.6, -260, 133.3), (50, -450)),
    (13, "R INNER SIDE PLATE (Y-)", (500, -160, 220), (300, -450)),
]

for n, text, p3, b in callouts:
    px, py = proj(p3)
    ax.annotate("", xy=(px, py), xytext=b,
                arrowprops=dict(arrowstyle="-|>", mutation_scale=11, lw=0.9,
                                color="0.15", shrinkA=20, shrinkB=2), zorder=5)
    ax.plot([px], [py], marker="o", ms=3.0, color="k", zorder=6)
    ax.add_patch(plt.Circle(b, 19, facecolor="white", edgecolor="k",
                            linewidth=1.1, zorder=7))
    ax.text(b[0], b[1], str(n), fontsize=13, weight="bold",
            ha="center", va="center", zorder=8)

# legend panel - no text over the drawing
leg = fig.add_axes([0.725, 0.115, 0.255, 0.815])
leg.set_xlim(0, 1)
leg.set_ylim(0, 1)
leg.axis("off")
leg.text(0.0, 0.975, "LEGEND", fontsize=16, weight="bold", va="top")
for i, (n, text, p3, b) in enumerate(callouts):
    y = 0.905 - i * 0.060
    leg.text(0.035, y, str(n), fontsize=12.0, weight="bold",
             ha="center", va="center",
             bbox=dict(boxstyle="circle,pad=0.24", fc="white", ec="k", lw=0.9))
    leg.text(0.10, y, text, fontsize=13.0, ha="left", va="center")
leg.text(0.0, 0.105, "L = +Y (far side); R = −Y (near side).", fontsize=12.0,
         weight="bold", va="center")
leg.text(0.0, 0.068, "R outer side plate removed - dotted outline.", fontsize=12.0,
         weight="bold", va="center")
leg.text(0.0, 0.030, "Simplified GA; not for manufacture.", fontsize=12.0,
         va="center")

fig.text(0.36, 0.965, "UC-V2  —  ISOMETRIC VIEW  (NTS, SIMPLIFIED GA)",
         fontsize=24, weight="bold", ha="center", va="top")
fig.text(0.36, 0.025,
         "Near track shown; the far track is behind the far inner side plate — see GA-005 for both tracks.\n"
         "Visible edges only; dimensions mm; FRONT = +X (right).",
         ha="center", va="bottom", fontsize=11.0, linespacing=1.35)

fig.savefig(ROOT / "ga_isometric.png", dpi=200, bbox_inches="tight",
            facecolor="white")
# A3 landscape cover, matching the rest of the pack.
fig.set_size_inches(16.54, 11.69)
fig.savefig(ROOT / "ga_isometric.pdf", format="pdf", facecolor="white")
print("wrote ga_isometric.png / ga_isometric.pdf")
