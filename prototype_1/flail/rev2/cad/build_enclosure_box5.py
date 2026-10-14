"""build_enclosure_box5.py - 5-FACE BOX enclosure (THE BUILD).
1 plasma development (front+top+rear, 2 manual bends ~80deg) + 2 bolted cheeks.
Single-cut accepted; plasma + manual bends + stitch welds. Same rotor/drive/guards as v2.
Profile corners, rel-centre (abs Z = +218): lip (205,100) / FTC (160,405) / RTC (-170,405) / MT (-210,180).
Outputs: enclosure_box5.step / .stl next to this script.
"""
import math, os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
C = (Align.CENTER, Align.CENTER, Align.CENTER)

RCUT = 158.15
ZC = 218.0
WI = 550.0
SHEET = 4.0
CHEEK = 4.0            # 4mm cheeks + doubler plates at UCF (lightened; see audit)
RROLL = 57.15            # roller radius (100NB-Light 114.3x3.65 STOCK)
ZROLLC = 57.15           # roller centre height (sits on ground, top at 114.3)
ROLL_L = 562.0
# corners (Y rel, Z abs)
CORN = [(205.0, 100.0), (160.0, 405.0), (-170.0, 405.0), (-210.0, 180.0)]
outer = [(y, z - ZC) for (y, z) in CORN]

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
print(f"min inner-panel to tip-circle clearance: {worst:.2f} mm (want >= 15)")
assert worst >= 15.0, "panel too tight for manual build!"

pts_out = [(y, z + ZC) for (y, z) in outer]
pts_in = [(y, z + ZC) for (y, z) in inner]
dev = [math.hypot(pts_out[i+1][0]-pts_out[i][0], pts_out[i+1][1]-pts_out[i][1]) for i in range(3)]
print(f"development: front {dev[0]:.0f} + top {dev[1]:.0f} + rear {dev[2]:.0f} = {sum(dev):.0f} x {WI:.0f}, 2 bends ~80deg r>=8")

def wire_yz(pts):
    return Polyline(*[Vector(0, y, z) for (y, z) in pts], close=True)

def xcyl(r, length, yc, zc, xc=0.0):
    return Cylinder(r, length, align=C).rotate(Axis.Y, 90).translate((xc, yc, zc))

# ---------------- shell: 4mm band ----------------
shell = extrude(Face(wire_yz(pts_out + pts_in[::-1])), amount=WI / 2, both=True)
print(f"shell volume: {shell.volume / 1e3:.1f} cm3")

# ---------------- cheeks: chamfered top corners (front+rear triangles above shell removed) ----------------
YROLLC = -210.0 - 86.0 * math.sin(math.radians(50)) - 10.0 - RROLL
y_min = YROLLC - RROLL - 12.0
y_max = 205.0 + 12.0
z_top = 413.0
CHAM = 70.0   # corner cut size; keeps all bores/bolts (nearest M10 clears by 13+)
cheeks = []
for sgn in (1, -1):
    x0 = sgn * WI / 2
    hexpts = [(y_min, 15.0), (y_max, 15.0), (y_max, z_top - CHAM),
              (y_max - CHAM, z_top), (y_min + CHAM, z_top), (y_min, z_top - CHAM)]
    plate = extrude(Face(Polyline(*[Vector(x0 + sgn * CHEEK / 2, y, z) for (y, z) in hexpts],
                                  close=True)), amount=CHEEK / 2, both=True)
    plate = plate - xcyl(26.0, CHEEK + 4, 0.0, ZC, x0 + sgn * CHEEK / 2)
    plate = plate - xcyl(21.0, CHEEK + 4, YROLLC, 70.0, x0 + sgn * CHEEK / 2)
    for zb in (40.0, 200.0, 340.0):
        for yb in (y_min + 30.0, y_max - 30.0):
            plate = plate - xcyl(5.5, CHEEK + 4, yb, zb, x0 + sgn * CHEEK / 2)
    cheeks.append(plate)

# ---------------- roller: 114.3x3.65 tube + stub axles dia-20 ----------------
roller = xcyl(RROLL, ROLL_L, YROLLC, ZROLLC) - xcyl(RROLL - 3.65, ROLL_L - 2, YROLLC, ZROLLC)
axles = [xcyl(10.0, 34.0, YROLLC, ZROLLC, sgn * (ROLL_L / 2 + 12.0)) for sgn in (1, -1)]

# ---------------- deflector from mount ----------------
yE, zE = -210.0, 180.0
dy = -86.0 * math.sin(math.radians(50))
dz = -86.0 * math.cos(math.radians(50))
deflector = Box(550, 86.0, 4.0).rotate(Axis.X, math.degrees(math.atan2(dz, dy)))
deflector = deflector.translate((0, yE + dy / 2, zE + dz / 2))
print(f"deflector tip Z {(zE + dz):.0f}, gap {(zE + dz) - 2 * RROLL:.0f} (want 8-20)")
assert 8.0 <= ((zE + dz) - 2 * RROLL) <= 20.0, "deflector gap out of band!"

# ---------------- comb + hanger straps (tips at RCUT+12, bar clear of roof) ----------------
aC = -40.0
rC = RCUT + 12.0 + 40.0
yC = rC * math.sin(math.radians(aC))
zC = rC * math.cos(math.radians(aC)) + ZC
comb = Box(500, 40.0, 8.0).fuse(*[Box(40.0, 30.0, 8.0).translate((-225.0 + k * 50.0, -25.0, 0.0)) for k in range(10)])
comb = comb.rotate(Axis.X, 90.0 - aC).translate((0, yC, zC))
straps = [Box(40.0, 8.0, 70.0).translate((sgn * 150.0 - 20.0, -151.8, 366.0)) for sgn in (1, -1)]

# ---------------- flap + clamp / curtains / lip bar ----------------
flap = Box(550, 8.0, 155.0).translate((0, -210.0, 102.5))
clamp = Box(550, 30.0, 6.0).translate((0, -210.0, 165.0))
YH = 210.0
strip_header = Box(550, 12.0, 12.0).translate((0, YH - 6.0, 159.0))
strips = []
for k in range(6):
    x = -275.0 + 45.0 + k * 90.0
    strips.append(Box(80.0, 8.0, 125.0).translate((x - 40.0, YH - 4.0, 102.5)))
    strips.append(Box(80.0, 8.0, 110.0).translate((x + 5.0, YH - 16.0, 110.0)))
lipbar = Box(550, 40.0, 6.0).translate((0, 188.0, 97.0))

# ---------------- side skirts (5mm rubber, bottom Z20, per L2) ----------------
skirts = [Box(2.0, 560.0, 60.0).translate((sgn * 274.0, -60.0, 50.0)) for sgn in (1, -1)]

# ---------------- top-panel stiffener (audit fix: bolted 30x4 flat, clears tip top by 21) ----------------
stiffener = Box(550, 30.0, 4.0).translate((0, -5.0, 399.0))

# ---------------- skids / torque / drive visuals / rotor ----------------
skids = [Box(6.0, 280.0, 90.0).translate((sgn * 283.0, -200.0, 45.0)) for sgn in (1, -1)]
# torque tube EXTERNAL backbone on roof (JD pattern) + gussets to cheeks.
# (Inside position at Y-120/Z318 clashed the tip envelope by ~22mm - FreeCAD audit catch.)
torque = Box(550, 40.0, 40.0).translate((0, -190.0, 425.0)) - Box(534.0, 34.8, 34.8).translate((0, -190.0, 425.0))
gussets = [Box(6.0, 60.0, 60.0).translate((sgn * 269.0 - 3.0, -190.0, 415.0)) for sgn in (1, -1)]
ucf = [Box(10.0, 110.0, 110.0).translate((sgn * 288.0, 0.0, ZC)) for sgn in (1, -1)]
doublers = [Box(4.0, 150.0, 150.0).translate((sgn * 281.0, 0.0, ZC)) for sgn in (1, -1)]

# ---------------- drive: SPZ 100x3-1610 1:1 (Fenner/Pix/Optibelt stock) ----------------
# Rotor: 1610 bush bore 25+key (stock). Motor: KEYED variant (confirm bore 24/25/28 at order).
# Motor shaft pos below = placeholder coaxial with motor body; VERIFY vs Mecwin drawing (slots absorb +/-15).
PUL_D = 100.0
PX = 318.0            # belt plane centre x (pulley inner face 4 clear of UCF outer 293)
MS_Y, MS_Z = -60.0, 511.0
pulleys = [xcyl(52.0, 42.0, 0.0, ZC, PX), xcyl(52.0, 42.0, MS_Y, MS_Z, PX)]

def _belt_loop(xc):
    rO, rI = 56.0, 48.0
    p1, p2 = (0.0, ZC), (MS_Y, MS_Z)
    dx, dz = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dz)
    a_d = math.atan2(dz, dx)
    wire = []
    for (c, a0, a1) in ((p2, a_d + math.pi / 2, a_d - math.pi / 2),
                        (p1, a_d - math.pi / 2, a_d - 3 * math.pi / 2)):
        pts = []
        for k in range(11):
            a = a0 + (a1 - a0) * k / 10
            pts.append((c[0] + rO * math.cos(a), c[1] + rO * math.sin(a)))
        wire += pts
    wout = Polyline(*[Vector(xc, y, z) for (y, z) in wire], close=True)
    return wout

belts = []
for xb in (PX - 12.0, PX):
    wo = _belt_loop(xb)
    belts.append(extrude(Face(wo), amount=4.0, both=True))
CC = math.hypot(MS_Y, MS_Z - ZC)
print(f"pulleys SPZ100x3-1610 @x{PX:.0f}, C~{CC:.0f} -> belt L~{2*CC + math.pi*PUL_D:.0f}: stock SPZ 900/912/925, pick at fit-up")
motor_plate = Box(300.0, 290.0, 6.0).translate((100.0, 15.0, 408.0))
for (px, py) in ((0.0, 130.0), (200.0, 130.0), (0.0, -115.0), (200.0, -115.0)):
    motor_plate = motor_plate - Cylinder(30.0, 10.0, align=C).translate((px, py, 408.0))
# pockets: 4x dia-60 lightening, clear of feet and mount slots
motor_feet = [Box(100.0, 40.0, 20.0).translate((60.0, -60.0, 421.0)),
              Box(100.0, 40.0, 20.0).translate((140.0, -60.0, 421.0))]
motor = Cylinder(80.0, 260.0, align=C).rotate(Axis.Y, 90).translate((100.0, -60.0, 511.0))
guard = Box(2.0, 280.0, 450.0).translate((356.0, -40.0, 375.0))
guard_sides = [Box(67.0, 2.0, 450.0).translate((323.5, -180.0, 375.0)),
               Box(67.0, 2.0, 450.0).translate((323.5, 100.0, 375.0))]
drum = xcyl(60.3 / 2, 500, 0.0, ZC) - xcyl(60.3 / 2 - 3.65, 500, 0.0, ZC)
shaft = xcyl(12.5, 700, 0.0, ZC)

assy = Compound([shell, stiffener, *cheeks, *doublers, roller, *axles, deflector, comb, *straps, lipbar, flap, clamp,
                 strip_header, *strips, *skids, *skirts, torque, *gussets, *ucf, motor_plate, *motor_feet, motor, guard,
                 *guard_sides, *pulleys, *belts, drum, shaft])
export_step(assy, os.path.join(HERE, "enclosure_box5.step"))
export_stl(assy, os.path.join(HERE, "enclosure_box5.stl"))
bb = assy.bounding_box()
print(f"bbox X {bb.min.X:.0f}..{bb.max.X:.0f} Y {bb.min.Y:.0f}..{bb.max.Y:.0f} Z {bb.min.Z:.0f}..{bb.max.Z:.0f}")
export_step(assy, os.path.join(HERE, "enclosure_box5.step"))
export_stl(assy, os.path.join(HERE, "enclosure_box5.stl"))
bb = assy.bounding_box()

# ---------------- closed-loop export: CAD-measured values for the sim to verify ----------------
import json
parts_weigh = {}
for _n, _o in [("shell", shell), ("cheeks", cheeks), ("roller", roller), ("comb", comb),
               ("deflector", deflector), ("torque", torque)]:
    _items = _o if isinstance(_o, list) else [_o]
    parts_weigh[_n] = round(sum(_p.volume for _p in _items) / 1e9 * 7850.0, 2)
with open(os.path.join(HERE, "enclosure_cad.json"), "w") as _f:
    json.dump({
        "lip": [CORN[0][0], CORN[0][1]], "corners_rel": [[y, z - ZC] for (y, z) in CORN],
        "r_cut": RCUT, "r_roll": RROLL, "roller_centre": [round(YROLLC, 2), ZROLLC],
        "deflector_tip": [round(yE + dy, 2), round(zE + dz, 2)],
        "measured_min_clearance": round(worst, 2),
        "measured_deflector_gap": round((zE + dz) - 2 * RROLL, 2),
        "part_mass_kg": parts_weigh,
        "bbox": [[round(v, 1) for v in (bb.min.X, bb.min.Y, bb.min.Z)],
                 [round(v, 1) for v in (bb.max.X, bb.max.Y, bb.max.Z)]],
    }, _f, indent=1)
print("WROTE enclosure_cad.json (closed-loop for sim)")
export_step(assy, os.path.join(HERE, "enclosure_box5.step"))
export_stl(assy, os.path.join(HERE, "enclosure_box5.stl"))
bb = assy.bounding_box()
print(f"bbox X {bb.min.X:.0f}..{bb.max.X:.0f} Y {bb.min.Y:.0f}..{bb.max.Y:.0f} Z {bb.min.Z:.0f}..{bb.max.Z:.0f}")

print("""
=========== BOM box-5 (plasma + manual) ===========
1  development 4mm MS 867x550, 2 bends    PLASMA + 2 manual bends (template) |
1b stiffener 30x4 flat 550 (bolted M10x4, audit fix for top-panel buzz) |
2  cheek 4mm MS, 2x SAME P/N (flip)        PLASMA-pilot 8, drill 11/15/26/42  | M10x12
2b doubler 4mm 150x150 2x at UCF          PLASMA                            | (UCF bolts)
2c angle clips 25x25x4x40, 12x (cheek-to-shell seam, stitch-weld to shell) | M10 nuts
3  lip bar 40x6 550                         BUY flat, cut                     | M10x5
4  roller 114.3x3.65 (100NB-L STOCK) 562  SAW + weld discs + 20 rod; BUY 6004x2 |
5  deflector MS 4, 86x550                   PLASMA                            | M10x4
6  comb 8mm 1pc + 2 straps                  PLASMA                            | M10x6
7  flap + clamp bar / 12 strips belt        SLIT                              | M10x17
8  skids 6mm 280x90 2x / torque SHS40x40x2.6 PLASMA / SAW+weld                | M10x8
9  UCF205/SPZ/pulleys/motor                 BUY                               | M14x8
9b pulleys 2x SPZ 100x3-1610 (Fenner/Pix stock): rotor bush 1610 bore 25+key; motor bush 1610 bore=keyed shaft (confirm Mecwin) | -
9c belts 2x SPZ now (grooves 1-2); 3rd belt adds 5kW later, NO pulley change. Length at fit-up (C~299: 900/912/925) | -
ACTION: order Mecwin 3kW with KEYED shaft; confirm bore (24/25/28) then buy motor 1610 bush.
Unique plasma P/N: 8 | weld: roller + torque + clips + 4 corner stitches | 1 spanner M10
================================================""")
