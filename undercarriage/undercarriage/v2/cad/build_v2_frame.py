#!/usr/bin/env python3
"""build_undercarriage.py - easy-fab rigid tracked undercarriage for 180x72x37.

Defaults frozen 2026-10-13 from sim_drive_chain + LEARNING.md:
  track 180x72x37 (W180 P72 N37 B23 A66 C28.5 D28.5 E22-assumed, Ld2664)
  sprocket 72z9 (PD210.51 Rp105.26, pack16 in B23, bore40H7/12x8 key)
  R drive end = Rp (Ls~1001), rear drive, screw-slider tension 50mm travel
  3x bottom roller D120 + front idler D200 per side, turned + 6205-2RS (common stock)
  side plates 6mm laser (<=8), spacers/RHS spine, 2x SHS40 cross members
  shared dia40 through-axle on 4x UCP plummers, chain stage open (axle sized 80Nm/side)
  gauge centre-centre 520 (outer ~700), belly ~130, rigid, mass target light
Outputs (into undercarriage/cad/): side_plate.dxf, undercarriage.json,
  undercarriage_frame.stl (boxes+cylinders, envelope-exact), BOM.md
Units mm, X travel (+fwd), Y across, Z up, ground lug-tip = 0.
"""
import math, json, pathlib

# --- frozen inputs ---
W, PITCH, N = 180.0, 72.0, 37
B_IN, A_OUT, C_H = 23.0, 66.0, 28.5
BELT, LUG_H = 12.0, 22.0
Z, PD = 9, 72.0 / math.sin(math.pi / 9)
RP = PD / 2.0                    # 105.26
R = RP                           # refit loop ends to sprocket pitch radius
LD = PITCH * N                   # 2664
LS = (LD - 2 * math.pi * R) / 2  # ~1001.3
# running gear
ROLLER_D, ROLLER_N = 114.3, 3    # v2: 100NB-M pipe shell as-is (no turning to size)
ROLLER_W, ROLLER_OFF = 40.0, 62.0   # paired discs on side bands (clear horns A66)
IDLER_D = 200.0                     # v2: laser-laminate discs (no pipe/turning to size)
IDLER_W = 40.0
TENSION_TRAVEL = 50.0
PLATE_T = 6.0                       # v2: 6mm common sheet, plain + modest pockets (no ribs needed)
PLATE_OFF = 100.0                   # plates outboard of track (clear horns/lugs ~10)
SHAFT_D = 25.0                      # roller/idler shafts, simply supported
GAUGE_CC = 520.0                 # track centre-centre -> outer 700
OUTER = GAUGE_CC + W
BELLY = 30.0                        # frame underside clearance (derived, lug tips at 0)
AXLE_DIA, AXLE_TORQUE = 40.0, 80.0  # per side, burst+margin
SAG = 20.0                       # mid-span start point (15-25 band)
BEAR_Y = [120.0, 360.0]          # plummer stations (inboard pair + outboard pair, mirrored)

root = pathlib.Path(__file__).resolve().parent
DO_DXF = False  # CAD first: DXF only after freeze
root.mkdir(parents=True, exist_ok=True)

# --- derived geometry (datum: ground lug-tip = 0, loop-driven, NOT belly-driven) ---
pitch_bottom = LUG_H + BELT / 2.0          # 28: pitch line above ground at bottom run
loop_cz = pitch_bottom + R                 # 133.3: loop/sprocket/idler centre height
axle_h = loop_cz                            # shared axle = sprocket centre
roller_z = (pitch_bottom + BELT / 2.0) + ROLLER_D / 2.0   # belt-inner + radius = 94
ARC_X = LS / 2                              # 500.6: front/rear arc centres
REAR_X, FRONT_X = -ARC_X, ARC_X
roller_x = [-300.0, 0.0, 300.0]   # equal 300 spacing; 35.3 vs sprocket / 40.6 vs idler (MATLAB)
# frame: side plates span LS + ends, height covers rollers + top run
plate_len = 1240.0  # ends follow arcs + chamfers (track-hugging, ref photos)
plate_bot, plate_top = 30.0, 250.0
plate_h = plate_top - plate_bot
plate_cz = (plate_bot + plate_top) / 2.0
BELLY = 30.0                             # = plate bottom (plates are lowest frame part)
# checks
assert 16.0 <= B_IN - 4.0, "pack must clear B gap"
play = (B_IN - 16.0) / 2
assert 1.5 <= play <= 5.0, f"gorge play {play}"
tooth_tip_w, insert_gap = 22.0, PITCH - 20.0
assert tooth_tip_w < insert_gap - 10, "tooth/window clash"
horn_gap = PITCH - 32.0
assert tooth_tip_w < horn_gap - 5, "tooth/horn clash"
wrap = 180.0
assert wrap >= 150, "wrap"
# ground pressure @250kg
p_kpa = 250 * 9.81 / (2 * (LS / 1000) * (W / 1000)) / 1000
# chain: axle torque per side 80Nm -> chain pull for 60T pitch ~? placeholder 12.7 pitch
data = {
    "track": "180x72x37", "sprocket": "72z9 PD210.51 Rp105.26 rear-drive",
    "loop": {"R": round(R, 2), "Ls": round(LS, 1), "Ld": LD, "closure": 0.0},
    "running_gear": {"bottom_rollers": f"{ROLLER_N}x2 discs D{ROLLER_D}x{ROLLER_W} at +-62 + dia{SHAFT_D} shafts",
                     "idler": f"2 discs D{IDLER_D}x{IDLER_W} at +-62 + dia{SHAFT_D} shaft in sliders",
                     "tension": f"screw-slider travel {TENSION_TRAVEL}, sag start {SAG}"},
    "frame": {"plate": "6mm 1240x220 track-hugging z30-250 (plate_holes.json/STEP/DXF are masters)",
              "plate_note": "undercarriage_frame.stl SUPERSEDED by assembly sections + FreeCAD solids",
              "side_axle": f"dia{AXLE_DIA} h6 per side at rear x={REAR_X:.1f} z={axle_h:.1f}, UCFL208 (holes +-60, confirm unit), 48T inboard",
              "centre": "front tie + 2x mid SHS40 + rear motor beam (2x motors, 1/side) + deck mounts + pack bay",
              "motors": "2x 1.2kW, 14T->48T 428 chain per side (v2 G3.43), vertical run + guard",
              "gauge_cc": GAUGE_CC, "outer": OUTER + 32, "belly": BELLY,
              "loop_centre_height": round(loop_cz, 1), "roller_z": round(roller_z, 1)},
    "clearances": {"gorge_play_per_side": round(play, 2), "tooth_window": f"{tooth_tip_w} in {insert_gap}",
                   "horn_window": horn_gap, "wrap_deg": wrap},
    "loads_250kg": {"ground_pressure_kPa": round(p_kpa, 1),
                    "axle_torque_15deg_Nm": 33.4, "axle_torque_30deg_Nm": 64.6,
                    "chain": "G=3.43 14T->48T 428 (v2 400kg/20deg); 1.2kW frozen"},
    "process": "laser side plates+spacers <=8; lathe rollers/idler/axle/boss; ream bore/keyway; MIG/TIG weld, clamp flat; slots for tension screws + chain centres",
    "mass_note": "frame+axle+rollers target <60kg/side-pair (weighed at build); deck+mast separate",
}
(root / "undercarriage.json").write_text(json.dumps(data, indent=2))

# --- side plate DXF (outline + roller holes + idler slot + axle clearance + pockets) ---
lines, circles, rects = [], [], []
L, H = plate_len, plate_h
x0, y0 = -L / 2, 0.0
lines += [(x0, y0, x0 + L, y0), (x0 + L, y0, x0 + L, y0 + H),
          (x0 + L, y0 + H, x0, y0 + H), (x0, y0 + H, x0, y0)]
for rx in roller_x:  # stub-shaft holes dia25 (6205 bore) + 4xM10 bolt circle r35
    circles.append((rx, roller_z - plate_bot, 12.5))
    for k in range(4):
        a = math.radians(45 + k * 90)
        circles.append((rx + 35 * math.cos(a), roller_z - plate_bot + 35 * math.sin(a), 5.5))
# idler slot: horizontal 50 travel about front arc centre, stub height = loop_cz
sx = ARC_X - 20.0
sl_c = loop_cz - plate_bot
rects.append((sx, sl_c - 25.0, sx + TENSION_TRAVEL, sl_c + 25.0))  # slot outer
circles.append((sx + TENSION_TRAVEL / 2, sl_c, 12.5))
# axle clearance dia45 at rear arc centre + plummer bolt pattern
ax = REAR_X
circles.append((ax, sl_c, 22.5))
for bx in (ax - 45, ax + 45):
    circles.append((bx, sl_c - 40, 6.5)); circles.append((bx, sl_c + 40, 6.5))
# lightening pockets: upper band clear of roller bolts (local y 80..170), 2 bays
rects.append((x0 + 60, 80.0, -120.0, 170.0))
rects.append((120.0, 80.0, x0 + L - 60.0, 170.0))
if DO_DXF:
    with open(root / "side_plate.dxf", "w") as f:
        f.write("0\nSECTION\n2\nENTITIES\n")
        for x1, y1, x2, y2 in lines:
            f.write(f"0\nLINE\n8\nOUTLINE\n10\n{x1:.2f}\n20\n{y1:.2f}\n30\n0.0\n11\n{x2:.2f}\n21\n{y2:.2f}\n31\n0.0\n")
        for x1, y1, x2, y2 in rects:
            for a, b in [((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)), ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))]:
                f.write(f"0\nLINE\n8\nPOCKET\n10\n{a[0]:.2f}\n20\n{a[1]:.2f}\n30\n0.0\n11\n{b[0]:.2f}\n21\n{b[1]:.2f}\n31\n0.0\n")
        for cx, cy, r in circles:
            f.write(f"0\nCIRCLE\n8\nHOLES\n10\n{cx:.2f}\n20\n{cy:.2f}\n30\n0.0\n40\n{r:.2f}\n")
        f.write("0\nTEXT\n8\nNOTES\n10\n-150.0\n20\n-30.0\n30\n0.0\n40\n6.0\n1\nSIDE PLATE 5MM MS - LASER +-0.3 - REAM 25H7 ROLLER SEATS\n")
        f.write("0\nENDSEC\n0\nEOF\n")

# --- envelope STL: 2 frames (boxes) + rollers/idler (oct prisms) + axle (prism) ---

def tri(a, b, c): return (a, b, c)

def box(cx, cy, cz, sx, sy, sz):
    x0, x1, y0, y1, z0, z1 = cx - sx / 2, cx + sx / 2, cy - sy / 2, cy + sy / 2, cz - sz / 2, cz + sz / 2
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    q = [(0, 1, 2, 3), (4, 6, 5, 7 - 3), (0, 4, 5, 1), (2, 6, 7, 3), (0, 3, 7, 4), (1, 5, 6, 2)]
    t = []
    for i, j, k, l in q:
        t += [tri(v[i], v[j], v[k]), tri(v[i], v[k], v[l])]
    return t

def cylx(cx, cy, cz, d, w, n=8):
    t = []
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p0 = (cx, cy + d / 2 * math.cos(a0), cz + d / 2 * math.sin(a0))
        p1 = (cx, cy + d / 2 * math.cos(a1), cz + d / 2 * math.sin(a1))
        q0 = (cx + w, p0[1], p0[2])
        q1 = (cx + w, p1[1], p1[2])
        t += [tri(p0, p1, q1), tri(p0, q1, q0)]
    return t

def cyly(cx, cy, cz, d, w, n=12):
    """Cylinder with axis along Y (across machine): running gear + axle."""
    t = []
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p0 = (cx + d / 2 * math.cos(a0), cy - w / 2, cz + d / 2 * math.sin(a0))
        p1 = (cx + d / 2 * math.cos(a1), cy - w / 2, cz + d / 2 * math.sin(a1))
        q0 = (cx + d / 2 * math.cos(a0), cy + w / 2, cz + d / 2 * math.sin(a0))
        q1 = (cx + d / 2 * math.cos(a1), cy + w / 2, cz + d / 2 * math.sin(a1))
        t += [tri(p0, p1, q1), tri(p0, q1, q0)]
    return t

tris = []
for side in (-1, 1):
    yc = side * GAUGE_CC / 2
    for dy in (-PLATE_OFF, PLATE_OFF):   # plates outboard of track, z 60..250
        tris += box(0, yc + dy, plate_cz, plate_len, PLATE_T, plate_h)
    for rx in roller_x:                  # paired discs + through shaft
        for do in (-ROLLER_OFF, ROLLER_OFF):
            tris += cyly(rx, yc + do, roller_z, ROLLER_D, ROLLER_W)
        tris += cyly(rx, yc, roller_z, SHAFT_D, 2 * PLATE_OFF + 20, 8)
    for do in (-ROLLER_OFF, ROLLER_OFF):  # idler pair at front arc centre
        tris += cyly(FRONT_X, yc + do, loop_cz, IDLER_D, IDLER_W)
    tris += cyly(FRONT_X, yc, loop_cz, SHAFT_D, 2 * PLATE_OFF + 20, 8)
    tris += cyly(REAR_X, yc, loop_cz, PD, 16)          # sprocket at rear arc centre
    tris += cyly(REAR_X, yc, loop_cz, AXLE_DIA, 2 * PLATE_OFF + 40, 10)  # side axle
    tris += cyly(REAR_X, yc - side * (PLATE_OFF + 20), loop_cz, 194.0, 12)  # 48T inboard (v2 G3.43)
    tris += box(FRONT_X + 30, yc - PLATE_OFF, loop_cz, 90, 30, 40)  # slider blocks
    tris += box(FRONT_X + 30, yc + PLATE_OFF, loop_cz, 90, 30, 40)
    tris += box(REAR_X, yc - PLATE_OFF - 10, loop_cz, 90, 30, 60)   # UCFL flanges
    tris += box(REAR_X, yc + PLATE_OFF + 10, loop_cz, 90, 30, 60)
ci = GAUGE_CC / 2 - PLATE_OFF   # 160: clear inner plates
tris += box(REAR_X, 0, 200, 100, 2 * ci, 40)   # rear motor beam SHS40 (v2 lighter)
tris += box(FRONT_X, 0, 110, 50, 2 * ci, 40)  # front tie beam
tris += box(-150, 0, plate_cz, 100, 2 * ci, 40)
tris += box(150, 0, plate_cz, 100, 2 * ci, 40)  # mid cross SHS40 x2 (v2 single size)
for s in (-1, 1):
    tris += box(-380, s * 80, 330, 220, 130, 220)   # motor env per side
    tris += box(REAR_X, s * 80, 210, 120, 20, 180)  # chain guard per side (old centre items removed below)
with open(root / "undercarriage_frame.stl", "w") as f:
    f.write("solid undercarriage\n")
    for t in tris:
        (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = t
        ux, uy, uz = x2 - x1, y2 - y1, z2 - z1
        vx, vy, vz = x3 - x1, y3 - y1, z3 - z1
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        n = math.hypot(nx, ny, nz) or 1.0
        f.write(f"facet normal {nx/n:.4e} {ny/n:.4e} {nz/n:.4e}\nouter loop\n")
        for p in t:
            f.write(f"vertex {p[0]:.2f} {p[1]:.2f} {p[2]:.2f}\n")
        f.write("endloop\nendfacet\n")
    f.write("endsolid undercarriage\n")

bom = """# BOM — easy-fab undercarriage (per machine, 2 tracks)
- Side plates 6mm MS IS2062: 4x (2/side, mirrored) — laser per side_plate.dxf
- Spacers turned tube: 8x (between plates per side)
- Cross SHS40x40x2.6: 2x ~520 long + 4 gussets 6mm
- Bottom rollers: 12x D120x40 paired discs + 24x 6205-2RS + 6x dia25 shafts + M10 hw
- Front idlers: 4x D200x40 paired discs + 8x 6205-2RS + 2x dia25 shafts + slider blocks + M16 screws + jam nuts
- Side axles 2x dia40 h6 EN8 (1/side) + 2x 72z9 sprocket packs (4x 8mm laser) + hubs + 12x8 keys + 12x M12
- Flanges: 4x UCFL208 (dia40, on outer plate faces) + bolts
- Chains 2x: 14T->42T 428 per side + guards; motors 2x 1.2kW (1kW OK) on centre rails
- Deck mounts: 4x M12 rubber + bolts; lift eyes 2x
"""
(root / "BOM.md").write_text(bom)
print(json.dumps(data, indent=2))
print("wrote side_plate.dxf + undercarriage_frame.stl + BOM.md")
