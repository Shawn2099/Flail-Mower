"""build_enclosure_b123d.py - parametric flail-mower enclosure from sim_enclosure_design_v2 frozen dims.
All mm. Sim coords: X = rotor axis, Y = fwd+, Z = up, origin ground under rotor centre.
Outputs: enclosure_assy.step, enclosure_assy.stl next to this script.
Run with the project venv: ..\\.venvs\\build123d\\Scripts\\python.exe build_enclosure_b123d.py
"""
import math, os
from build123d import *

HERE = os.path.dirname(os.path.abspath(__file__))
C = (Align.CENTER, Align.CENTER, Align.CENTER)

# ---------------- frozen sim inputs ----------------
RCUT = 158.15          # tip circle radius
RO = 30.15             # drum outer radius
ZC = 218.0             # rotor centre height (abs)
WI = 550.0             # inner width
RROOF = 174.0          # roof radius (Rcut+16)
GROW = 22.0            # scroll growth
OFF = 3.0              # facet bend-line offset outward
SHEET = 4.0            # hood sheet thickness
CHEEK = 6.0            # cheek thickness
LIP_Z = 100.0          # front lip height abs
RROLL = 70.0           # roller radius
ZROLLC = 70.0          # roller centre abs (on ground)
YROLLC = -308.0        # roller centre Y rel (front face 10 behind deflector tip)
ROLL_L = 562.0         # roller length

def R_of(a):
    """volute radius at angle a (deg, +front through top to -rear)."""
    r = RROOF
    if a < -40:
        r += (-(a + 40)) / 60.0 * GROW
    return r

# facet nodes (deg) on arc+OFF; front sheet TANGENT to RROOF circle at 80deg to lip.
# (Straight secant sheet grazed the tip circle at ~2mm; tangent holds full 16 gap.)
AF = 80
ANGS = [80, 60, 40, 20, 0, -20, -40, -60, -80, -100]
_t = (RROOF * math.cos(math.radians(AF)) - (LIP_Z - ZC)) / math.sin(math.radians(AF))
YF = RROOF * math.sin(math.radians(AF)) + _t * math.cos(math.radians(AF))
YH = YF + 5.0          # curtain header Y rel
outer = [(YF, LIP_Z - ZC)]   # lip first (on tangent line)
for a in ANGS:
    r = R_of(a) + OFF
    outer.append((r * math.sin(math.radians(a)), r * math.cos(math.radians(a))))

def inward(p, t):
    """move point p (rel centre) toward rotor centre by t (exact for arc, ~exact for sheet)."""
    d = math.hypot(p[0], p[1])
    k = (d - t) / d
    return (p[0] * k, p[1] * k)

inner = [inward(p, SHEET) for p in outer]

# ---------------- verification: min inner clearance to tip circle ----------------
worst = 1e9
for i in range(len(inner) - 1):
    for j in range(41):
        s = j / 40
        y = inner[i][0] + (inner[i + 1][0] - inner[i][0]) * s
        z = inner[i][1] + (inner[i + 1][1] - inner[i][1]) * s
        worst = min(worst, math.hypot(y, z) - RCUT)
print(f"lip Y {YF:.1f} | min inner-shell to tip-circle clearance: {worst:.2f} mm (want >= 11 typical)")
assert worst >= 10.0, "clearance below allowance!"

# work in abs Z for CAD
pts_out = [(y, z + ZC) for (y, z) in outer]
pts_in = [(y, z + ZC) for (y, z) in inner]

def wire_yz(pts):
    return Polyline(*[Vector(0, y, z) for (y, z) in pts], close=True)

def xcyl(r, length, yc, zc, xc=0.0):
    """cylinder along X, centred at (xc, yc, zc)."""
    return Cylinder(r, length, align=C).rotate(Axis.Y, 90).translate((xc, yc, zc))

# ---------------- shell (4mm band, full inner width) ----------------
shell = extrude(Face(wire_yz(pts_out + pts_in[::-1])), amount=WI / 2, both=True)
print(f"shell volume: {shell.volume / 1e3:.1f} cm3")

# ---------------- cheeks (6mm, outside shell) ----------------
y_min = YROLLC - RROLL - 12.0
y_max = YF + 12.0
z_min = 15.0
z_max = ZC + RROOF + OFF + 8.0
cheeks = []
for sgn in (1, -1):
    x0 = sgn * WI / 2
    plate = Box(CHEEK, y_max - y_min, z_max - z_min).translate(
        (x0 + sgn * CHEEK / 2, (y_min + y_max) / 2, (z_min + z_max) / 2))
    plate = plate - xcyl(26.0, CHEEK + 4, 0.0, ZC, x0 + sgn * CHEEK / 2)        # rotor bore dia-52
    plate = plate - xcyl(21.0, CHEEK + 4, YROLLC, ZROLLC, x0 + sgn * CHEEK / 2) # roller seat dia-42
    cheeks.append(plate)

# ---------------- roller: dia-140 tube wall 4 + stub axles dia-20 ----------------
roller = xcyl(RROLL, ROLL_L, YROLLC, ZROLLC) - xcyl(RROLL - 4.0, ROLL_L - 2, YROLLC, ZROLLC)
axles = [xcyl(10.0, 34.0, YROLLC, ZROLLC, sgn * (ROLL_L / 2 + 12.0)) for sgn in (1, -1)]

# ---------------- deflector: 45 x 550 x 4 @50deg from scroll end ----------------
rE = R_of(-100.0) + OFF
yE = rE * math.sin(math.radians(-100.0))
zE = rE * math.cos(math.radians(-100.0)) + ZC
dy = -45.0 * math.sin(math.radians(50))
dz = -45.0 * math.cos(math.radians(50))
deflector = Box(550, 45.0, 4.0).rotate(Axis.X, math.degrees(math.atan2(dz, dy)))
deflector = deflector.translate((0, yE + dy / 2, zE + dz / 2))
tip_gap = (zE + dz) - (ZROLLC + RROLL)
print(f"deflector tip abs Z {(zE + dz):.0f}, gap over roller {tip_gap:.0f} (want 10-15)")
assert 8.0 <= tip_gap <= 20.0

# ---------------- counter-knife bar at -40deg, tips at Rcut+10 ----------------
aC = -40.0
rC = RCUT + 10.0 + 30.0
yC = rC * math.sin(math.radians(aC))
zC = rC * math.cos(math.radians(aC)) + ZC
ck = Box(500, 60.0, 8.0).rotate(Axis.X, 90.0 - aC).translate((0, yC, zC))

# ---------------- rear flap: 550 x 8, scroll end down to Z25 ----------------
flap = Box(550, 8.0, zE - 25.0).translate((0, yE - 4.0, (zE + 25.0) / 2))

# ---------------- front curtains: header + 22 chains + inner rubber ----------------
header = Box(550, 12.0, 12.0).translate((0, YH - 6.0, 165.0 - 6.0))
chains = [Box(20.0, 3.0, 125.0).translate((-275.0 + 12.5 + k * 25.0 - 10.0, YH - 1.5, 102.5))
          for k in range(22)]
inner_rubber = Box(550, 8.0, 110.0).translate((0, YH - 16.0, 110.0))

# ---------------- skids: 2x 320 x 90 x 6 ----------------
skids = [Box(6.0, 320.0, 90.0).translate((sgn * 286.0 - 3.0, -210.0, 45.0)) for sgn in (1, -1)]

# ---------------- torque tube SHS40x40x3 ----------------
torque = Box(550, 40.0, 40.0).translate((0, -140.0, 298.0))

# ---------------- rotor reference (ghost): drum + shaft ----------------
drum = xcyl(60.3 / 2, 500, 0.0, ZC) - xcyl(60.3 / 2 - 5.4, 500, 0.0, ZC)
shaft = xcyl(12.5, 700, 0.0, ZC)

# ---------------- assembly + export ----------------
assy = Compound([shell, *cheeks, roller, *axles, deflector, ck, flap,
                   header, *chains, inner_rubber, *skids, torque, drum, shaft])
step_path = os.path.join(HERE, "enclosure_assy.step")
stl_path = os.path.join(HERE, "enclosure_assy.stl")
export_step(assy, step_path)
export_stl(assy, stl_path)
bb = assy.bounding_box()
print(f"WROTE {step_path}\nWROTE {stl_path}")
print(f"bbox X {bb.min.X:.0f}..{bb.max.X:.0f} Y {bb.min.Y:.0f}..{bb.max.Y:.0f} Z {bb.min.Z:.0f}..{bb.max.Z:.0f}")
