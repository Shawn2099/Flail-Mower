"""build_enclosure_v2_mfg.py - MANUFACTURING v2 of the flail enclosure.
Same frozen profile as build_enclosure_b123d.py (all gates still hold).
DFM changes (ease of manufacture in every aspect):
  M1 shell = ONE laser-cut flat development, 10 brake bends at UNIFORM 20deg pitch (one press setup).
  M2 cheeks BOLTED (6x M10 each) to shell edge flanges - no jig welding, no weld distortion,
     coaxial bores via transfer-drill + ream at assembly.
  M3 liner: drop-in BOLTED 3mm wear plate (6x M8 buttons), not spot-welded.
  M4 curtains: 22 loose chains -> 12 slit rubber strips (6+6 staggered, conveyor-belt stock).
     Matches Berta/MechMaxx practice; fine for clean-ground scope (stones excluded by design).
  M5 counter-knife = ONE laser-cut comb part (bar + teeth, single nesting), bolted.
  M6 lip wear edge = standard 40x6 flat bar, bolted (replaceable, no edge build-up).
  M7 fasteners: M10 everywhere sheet-level (one spanner size); M8 buttons liner; M14 only at UCF205.
  M8 L/R cheek = SAME part number (symmetric hole pattern, flip to fit).
  M9 roller from standard 140 OD pipe + weld-in discs + 20mm rod stubs + off-shelf 6004.
  M10 drive all off-shelf: SPZ belts/pulleys taper-lock, UCF205, Mecwin motor. Guard = 3 flat plates.
  M11 motor top-mounted on single plate (photo pattern) with slotted holes (+/-15 for ratio change).
Outputs: enclosure_v2_mfg.step / .stl + BOM + flat-pattern table printed here.
"""
import math, os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
C = (Align.CENTER, Align.CENTER, Align.CENTER)

# ---------------- frozen profile (identical to v1 script) ----------------
RCUT = 158.15
RO = 30.15
ZC = 218.0
WI = 550.0
RROOF = 174.0
GROW = 22.0
OFF = 3.0
SHEET = 4.0
CHEEK = 6.0
LIP_Z = 100.0
RROLL = 70.0
ZROLLC = 70.0
YROLLC = -308.0
ROLL_L = 562.0

def R_of(a):
    r = RROOF
    if a < -40:
        r += (-(a + 40)) / 60.0 * GROW
    return r

AF = 80
ANGS = [80, 60, 40, 20, 0, -20, -40, -60, -80, -100]
_t = (RROOF * math.cos(math.radians(AF)) - (LIP_Z - ZC)) / math.sin(math.radians(AF))
YF = RROOF * math.sin(math.radians(AF)) + _t * math.cos(math.radians(AF))
YH = YF + 5.0
outer = [(YF, LIP_Z - ZC)]
for a in ANGS:
    r = R_of(a) + OFF
    outer.append((r * math.sin(math.radians(a)), r * math.cos(math.radians(a))))

def inward(p, t):
    d = math.hypot(p[0], p[1])
    k = (d - t) / d
    return (p[0] * k, p[1] * k)

inner = [inward(p, SHEET) for p in outer]

worst = 1e9
for i in range(len(inner) - 1):
    for j in range(41):
        s = j / 40
        y = inner[i][0] + (inner[i + 1][0] - inner[i][0]) * s
        z = inner[i][1] + (inner[i + 1][1] - inner[i][1]) * s
        worst = min(worst, math.hypot(y, z) - RCUT)
print(f"lip Y {YF:.1f} | min inner clearance {worst:.2f} mm (profile unchanged from v1)")
assert worst >= 10.0

pts_out = [(y, z + ZC) for (y, z) in outer]
pts_in = [(y, z + ZC) for (y, z) in inner]

def wire_yz(pts):
    return Polyline(*[Vector(0, y, z) for (y, z) in pts], close=True)

def xcyl(r, length, yc, zc, xc=0.0):
    return Cylinder(r, length, align=C).rotate(Axis.Y, 90).translate((xc, yc, zc))

# ---------------- M1: one-piece shell ----------------
shell = extrude(Face(wire_yz(pts_out + pts_in[::-1])), amount=WI / 2, both=True)

# flat-pattern development (outer chords; shop adds bend allowance per its table)
chords = [math.hypot(pts_out[i+1][0] - pts_out[i][0], pts_out[i+1][1] - pts_out[i][1])
          for i in range(len(pts_out) - 1)]
print(f"shell development: {len(chords)} flats, cut size {sum(chords):.0f} x {WI:.0f}, "
      f"10 bends @20deg pitch inner r>=6 (ONE press setup)")

# ---------------- M2/M8: bolted common cheek, 6x M10 ----------------
y_min = YROLLC - RROLL - 12.0
y_max = YF + 12.0
z_min = 15.0
z_max = ZC + RROOF + OFF + 8.0
bolt_rows = [40.0, 200.0, 360.0]
cheeks = []
for sgn in (1, -1):
    x0 = sgn * WI / 2
    plate = Box(CHEEK, y_max - y_min, z_max - z_min).translate(
        (x0 + sgn * CHEEK / 2, (y_min + y_max) / 2, (z_min + z_max) / 2))
    plate = plate - xcyl(26.0, CHEEK + 4, 0.0, ZC, x0 + sgn * CHEEK / 2)
    plate = plate - xcyl(21.0, CHEEK + 4, YROLLC, ZROLLC, x0 + sgn * CHEEK / 2)
    for zb in bolt_rows:  # M10 assembly bolts front+rear columns
        for yb in (y_min + 30.0, y_max - 30.0):
            plate = plate - xcyl(5.5, CHEEK + 4, yb, zb, x0 + sgn * CHEEK / 2)
    cheeks.append(plate)

# ---------------- M9: roller, standard pipe ----------------
roller = xcyl(RROLL, ROLL_L, YROLLC, ZROLLC) - xcyl(RROLL - 4.0, ROLL_L - 2, YROLLC, ZROLLC)
axles = [xcyl(10.0, 34.0, YROLLC, ZROLLC, sgn * (ROLL_L / 2 + 12.0)) for sgn in (1, -1)]

# ---------------- deflector (flat plate, unchanged) ----------------
rE = R_of(-100.0) + OFF
yE = rE * math.sin(math.radians(-100.0))
zE = rE * math.cos(math.radians(-100.0)) + ZC
dy = -45.0 * math.sin(math.radians(50))
dz = -45.0 * math.cos(math.radians(50))
deflector = Box(550, 45.0, 4.0).rotate(Axis.X, math.degrees(math.atan2(dz, dy)))
deflector = deflector.translate((0, yE + dy / 2, zE + dz / 2))

# ---------------- M5: counter-knife comb, ONE laser part (tips at RCUT+10) ----------------
aC = -40.0
rC = RCUT + 10.0 + 40.0
yC = rC * math.sin(math.radians(aC))
zC = rC * math.cos(math.radians(aC)) + ZC
comb_bar = Box(500, 40.0, 8.0)
teeth = [Box(40.0, 30.0, 8.0).translate((-250.0 + 25.0 + k * 50.0, -25.0, 0.0)) for k in range(10)]
comb = comb_bar.fuse(*teeth).rotate(Axis.X, 90.0 - aC).translate((0, yC, zC))

# ---------------- M3: bolt-in liner (3mm, hugs inner roof 30..90deg) ----------------
liner = Box(548, 176.0, 3.0).rotate(Axis.X, -60.0).translate((0, 146.0, 302.2))

# ---------------- M6: lip wear edge, standard flat bar ----------------
lipbar = Box(550, 40.0, 6.0).translate((0, YF - 3.0, LIP_Z - 20.0 + 3.0))

# ---------------- rear flap + clamp bars (M7: M10) ----------------
flap = Box(550, 8.0, zE - 25.0).translate((0, yE - 4.0, (zE + 25.0) / 2))
clamp = Box(550, 30.0, 6.0).translate((0, yE - 4.0, zE - 15.0))

# ---------------- M4: 12 rubber strips (6+6 staggered) ----------------
strips = []
for k in range(6):
    x = -275.0 + 45.0 + k * 90.0
    strips.append(Box(80.0, 8.0, 125.0).translate((x - 40.0, YH - 4.0, 102.5)))
    strips.append(Box(80.0, 8.0, 110.0).translate((x - 40.0 + 45.0, YH - 16.0, 110.0 - 7.5)))
strip_header = Box(550, 12.0, 12.0).translate((0, YH - 6.0, 159.0))

# ---------------- skids (flat, bolted) ----------------
skids = [Box(6.0, 320.0, 90.0).translate((sgn * 286.0 - 3.0, -210.0, 45.0)) for sgn in (1, -1)]

# ---------------- torque tube ----------------
torque = Box(550, 40.0, 40.0).translate((0, -140.0, 298.0))

# ---------------- M10/M11: UCF flange plates + motor plate + motor + guard ----------------
ucf = [Box(10.0, 110.0, 110.0).translate((sgn * (WI / 2 + CHEEK + 5.0) - 5.0, 0.0, ZC)) for sgn in (1, -1)]
motor_plate = Box(300.0, 300.0, 8.0).translate((100.0, -60.0, 399.0))
motor_feet = [Box(100.0, 40.0, 20.0).translate((60.0, -60.0, 412.0)),
              Box(100.0, 40.0, 20.0).translate((140.0, -60.0, 412.0))]
motor = Cylinder(80.0, 260.0, align=C).rotate(Axis.Y, 90).translate((100.0, -60.0, 502.0))
guard = Box(2.0, 260.0, 300.0).translate((356.0, -40.0, 300.0))

# ---------------- rotor reference ----------------
drum = xcyl(60.3 / 2, 500, 0.0, ZC) - xcyl(60.3 / 2 - 5.4, 500, 0.0, ZC)
shaft = xcyl(12.5, 700, 0.0, ZC)

assy = Compound([shell, *cheeks, roller, *axles, deflector, comb, liner, lipbar, flap, clamp,
                 strip_header, *strips, *skids, torque, *ucf, motor_plate, *motor_feet, motor, guard,
                 drum, shaft])
export_step(assy, os.path.join(HERE, "enclosure_v2_mfg.step"))
export_stl(assy, os.path.join(HERE, "enclosure_v2_mfg.stl"))
bb = assy.bounding_box()
print(f"bbox X {bb.min.X:.0f}..{bb.max.X:.0f} Y {bb.min.Y:.0f}..{bb.max.Y:.0f} Z {bb.min.Z:.0f}..{bb.max.Z:.0f}")

print("""
=========== BOM v2-mfg (process-coded) ===========
1  shell 4mm MS, 1pc development ~Lx550      LASER + 10 bends (1 setup)   |
2  cheek 6mm MS, 2x SAME P/N (flip)         LASER + ream 52H8/42          | M10x12
3  liner 3mm MS drop-in                     LASER                         | M8x6 button
4  lip bar 40x6, 550 LG                      BUY flat bar, cut            | M10x5
5  roller 140x4 pipe 562 + discs + 20 rod   SAW + weld + BUY 6004x2       |
6  deflector Hardox 4, 45x550                LASER                        | M10x4
7  comb knife 8mm, 1pc nested                LASER                        | M10x4
8  flap belt 8mm 550x200 + clamp bar         SLIT + flat bar              | M10x5
9  strips belt 8mm 12x (6x125+6x110)         SLIT                         | M10x12 + rod
10 skids Hardox 6, 2x                        LASER                        | M10x8
11 torque SHS40x40x3 550 + gussets 4x        SAW + weld                   |
12 UCF205 2x / SPZ 2x / pulleys 2x taper    BUY                          | M14x8
13 motor plate 8mm + slots                   LASER                        |
14 guard 3 plates 2mm                        LASER + 2 bends              |
Unique laser P/N: 8 | buy-outs: 7 | weld: roller + torque only | 1 spanner (M10)
================================================""")
