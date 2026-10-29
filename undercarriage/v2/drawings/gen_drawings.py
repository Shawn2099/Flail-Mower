# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""gen_drawings.py - UC-V2 A3 drawing pack.

All geometry comes from the frozen CAD: plate_holes.json, the DXFs and the
measured STEP solids. Run:  python gen_drawings.py [sheet ...]
Outputs one PDF+PNG per sheet in this folder.
"""
import json, math, pathlib, sys
from dwg_kit import Sheet, View
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parents[1]
CAD = ROOT / "cad"
OUT = ROOT / "drawings"
OUT.mkdir(exist_ok=True)

TOTAL = json.loads((CAD / "mass_audit.json").read_text())["total_kg"]
MASS = f"{TOTAL:.1f} kg"

# ---- frozen geometry (mm) -------------------------------------------------
C = 1001.3                 # loop centre distance
RSP = 105.26               # 9T x 72 pitch sprocket radius
ZC = 133.3                 # loop centre height
TY = 260.0                 # track centre y
BELT = 12.0
LUG = 22.0
PLATE_T = 6.0
PLATE_Y = 100.0            # plate centre offset from track centre
PLATE_Z0, PLATE_Z1 = 30.0, 250.0
ROLL_X = (-300.0, 0.0, 300.0)
ROLL_Z = 91.2
ROLL_R = 114.3 / 2
IDL_X, IDL_R = 500.6, 100.0
WHEEL_Y = 140.0
CHAIN_C = 168.66
PIN_R = 12.7 / math.sin(math.pi / 14) / 2
W48_R = 12.7 / math.sin(math.pi / 48) / 2
TRACK_L = C + 2 * (RSP + BELT / 2 + LUG)

PLATE = json.loads((CAD / "plate_holes.json").read_text())["plate"]


def stadium_pt(s, r, zc=ZC, c=C):
    """Point + outward normal at arc length s on a stadium of radius r."""
    arc = math.pi * r
    tot = 2 * c + 2 * arc
    s %= tot
    if s < c:
        return (-c / 2 + s, zc + r), (0.0, 1.0)
    s -= c
    if s < arc:
        a = math.pi / 2 - s / r
        return (c / 2 + r * math.cos(a), zc + r * math.sin(a)), (math.cos(a), math.sin(a))
    s -= arc
    if s < c:
        return (c / 2 - s, zc - r), (0.0, -1.0)
    s -= c
    a = -math.pi / 2 - s / r
    return (-c / 2 + r * math.cos(a), zc + r * math.sin(a)), (math.cos(a), math.sin(a))


def draw_track(v, lugs=True):
    for r in (RSP - BELT / 2, RSP + BELT / 2):
        pts = [stadium_pt(s, r, zc=ZC)[0] for s in
               [i * 4 for i in range(int((2 * C + 2 * math.pi * r) / 4) + 1)]]
        v.poly(pts, close=True, style="thin")
    if lugs:
        per = 2 * C + 2 * math.pi * RSP
        n = int(round(per / 72.0))
        for i in range(n):
            s = i * 72.0
            (x, z), (nx, nz) = stadium_pt(s, RSP)
            tx, tz = -nz, nx
            half_w, h = 15.0, LUG
            p1 = (x + tx * half_w + nx * (BELT / 2), z + tz * half_w + nz * (BELT / 2))
            p2 = (x - tx * half_w + nx * (BELT / 2), z - tz * half_w + nz * (BELT / 2))
            p3 = (p2[0] + nx * h, p2[1] + nz * h)
            p4 = (p1[0] + nx * h, p1[1] + nz * h)
            v.poly([p1, p2, p3, p4], close=True, style="thin")


def external_tangents(c1, r1, c2, r2):
    dx, dz = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dx, dz)
    th = math.atan2(dz, dx)
    al = math.acos(max(-1, min(1, (r1 - r2) / d)))
    out = []
    for s in (1, -1):
        a = th + s * al
        p1 = (c1[0] + r1 * math.cos(a), c1[1] + r1 * math.sin(a))
        p2 = (c2[0] + r2 * math.cos(a), c2[1] + r2 * math.sin(a))
        out.append((p1, p2))
    return out


def draw_chain(v):
    c1, c2 = (-500.65, ZC), (-460.0, 297.0)
    for p, q in external_tangents(c1, W48_R, c2, PIN_R):
        v.line(p[0], p[1], q[0], q[1], "out")
    v.circle(*c1, W48_R, "hid")
    v.circle(*c2, PIN_R, "out")
    v.circle(*c1, 20, "thin")
    v.circle(*c2, 10, "thin")


# ===========================================================================
def ga_side():
    s = Sheet("UCV2-GA-001", "GENERAL ARRANGEMENT - SIDE ELEVATION", 1, 14,
              "1:5", "-", "1", MASS, notes=[
                  "1. Near side plate removed for clarity; running gear shown true.",
                  "2. Datum: ground at lug tips z=0, X travel, Z up. Dimensions mm.",
                  "3. Track loop: 37 links x 72 pitch, R105.26, C1001.3 (closure 0).",
                  "4. Chain plane y=+/-140; 48T/14T 428, 60 links, C~170.",
                  "5. Overall W826 over UCFL208 flanges; plates 726; track 700.",
                  "6. Motor body y 4..134 (inboard); chain runs at y=140, outboard of motor.",
                  "7. Loop centre z=133.3; roller centre z=91.2. Call-outs 1-10 below."])
    v = View(s, 0.2, 190, 140, "SIDE ELEVATION  (1:5)", (14, 282))
    # ground
    v.line(-660, 0, 660, 0, "thin")
    for x in range(-660, 661, 50):
        v.line(x, 0, x - 6, -7, "thin")
    draw_track(v)
    # sprocket exact profile
    v.dxf(str(CAD / "sprocket_72z9.dxf"), dx=-500.65, dy=ZC, style="out")
    # idler + rollers
    v.circle(IDL_X, ZC, IDL_R, "out")
    v.circle(IDL_X, ZC, 32.5, "thin")
    v.circle(IDL_X, ZC, 26, "thin")
    for x in ROLL_X:
        v.circle(x, ROLL_Z, ROLL_R, "out")
        v.circle(x, ROLL_Z, 32.5, "thin")
        v.circle(x, ROLL_Z, 26, "thin")
    # side plate outline (near side removed -> thin reference)
    pts = [(x, y + PLATE_Z0) for x, y in PLATE["outline"]]
    v.poly(pts, close=True, style="thin")
    # beams / tie / rails / front beam
    for x0, x1, z0, z1 in ((-170, -130, 115, 155), (130, 170, 115, 155),
                           (-386, -346, 170, 210), (-625, -325, 210, 250),
                           (565, 605, 85, 125)):
        v.rect(x0, z0, x1 - x0, z1 - z0, "thin")
    # motors + pinion shaft
    for x0 in (-560,):
        v.rect(x0, 250, 200, 190, "out")
        v.line(x0 + 100, 297, -460, 297, "out")
    # deck pads / lugs
    for x0 in (-190, 110):
        v.rect(x0, 155, 80, 20, "thin")
    v.rect(-375, 130, 10, 80, "thin")
    # chain + guard
    draw_chain(v)
    v.rect(-575, 30, 140, 270, "hid")
    # dimensions (feature -> line; negative off = below the part)
    v.dim_h(-TRACK_L / 2, TRACK_L / 2, 0, f"{TRACK_L:.0f} track", -22)
    v.dim_h(-620, 620, 0, "1240 frame", -16)
    v.dim_h(-300, 300, ROLL_Z, "600 roller centres", 40)
    v.line(-360, 441, 740, 441, "dim")
    v.line(500.6, 267, 700, 267, "dim")
    v.dim_v(740, 0, 441, "441", 7)
    v.dim_v(700, 0, 267, "267", 7)
    # ten callouts in a spaced row above the view (all outside the machine)
    zc = 650.0
    v.balloon(-460, 440, -750, zc, 6)     # motor
    v.balloon(-500.6, 238, -550, zc, 4)   # sprocket
    v.balloon(-500.6, 133, -350, zc, 8)   # axle
    v.balloon(-370, 195, -150, zc, 10)    # lift lug
    v.balloon(0, 148, 50, zc, 2)          # roller
    v.balloon(150, 175, 250, zc, 9)       # deck pad
    v.balloon(170, 135, 450, zc, 7)       # beam
    v.balloon(300, 250, 650, zc, 5)       # plate
    v.balloon(500.6, 233, 850, zc, 3)     # idler
    v.balloon(600, 238, 1050, zc, 1)      # track
    # large legend, outside the view
    s.ax.add_patch(plt.Rectangle((12, 62), 204, 36, fill=False, ec="k", lw=0.8))
    s.ax.text(14, 100, "CALL-OUTS", fontsize=9, weight="bold", va="bottom")
    legend = [(1, "RUBBER TRACK 180x72x37"), (2, "ROLLER D114.3"),
              (3, "IDLER D200"), (4, "SPROCKET 72z9"), (5, "SIDE PLATE 6mm"),
              (6, "MOTOR 1.2 kW"), (7, "BEAM SHS40"), (8, "AXLE D40"),
              (9, "DECK PAD 80x80"), (10, "LIFT LUG")]
    for i, (n, txt) in enumerate(legend):
        col, row = divmod(i, 5)
        x = 16 + col * 102
        y = 94 - row * 6.4
        s.ax.text(x, y, str(n), fontsize=11, weight="bold", va="center")
        s.ax.text(x + 7, y, txt, fontsize=7.0, va="center")
    s.save(OUT / "UCV2-GA-001")


def ga_plan():
    s = Sheet("UCV2-GA-002", "GENERAL ARRANGEMENT - PLAN & END VIEW", 2, 14,
              "1:7", "-", "1", MASS, notes=[
                  "1. Track centres 520; plate gauge 200; overall 826 over UCFL.",
                  "2. Deck pads: x +/-150, y +/-100, top z175 (4x M12).",
                  "3. Motors 2x 1.2 kW on rails at z250..441, pinions at y +/-140.",
                  "4. Lift lugs at x=-370, y +/-100."])
    p = View(s, 1 / 7, 115, 205, "PLAN  (1:7)", (14, 282))
    for yc in (-TY, TY):
        p.rect(-TRACK_L / 2, yc - 90, TRACK_L, 180, "thin")
        p.line(-TRACK_L / 2, yc, TRACK_L / 2, yc, "cen")
        for x in ROLL_X + (IDL_X, -500.6):
            p.line(x, yc - 80, x, yc + 80, "cen")
        # wheels / sprockets, hidden under belt
        p.circle(-500.65, yc, RSP, "hid")
        p.circle(IDL_X, yc, 100, "hid")
        p.circle(-500.6, yc - 120 if yc > 0 else yc + 120, W48_R, "hid")
    for yc in (-TY, TY):
        for dy in (-PLATE_Y, PLATE_Y):
            p.rect(-620, yc + dy - 3, 1240, 6, "out")
    for x0, w in ((-386, 40), (-170, 40), (130, 40), (565, 40)):
        p.rect(x0, -157, w, 314, "thin")
    for y0 in (-140, -60, 20, 100):
        p.rect(-625, y0, 300, 40, "thin")
    p.rect(-560, 4, 200, 130, "out")
    p.rect(-560, -134, 200, 130, "out")
    for x in (-190, 110):
        for y in (-140, 60):
            p.rect(x, y, 80, 80, "thin")
    p.dim_h(-620, 620, 0, "1240", -64)
    p.dim_h(-TRACK_L / 2, TRACK_L / 2, 0, f"{TRACK_L:.0f}", -76)
    p.dim_h(-190, -110, 140, "80", 4)
    # ---------------- end view ----------------
    e = View(s, 1 / 7, 305, 105, "END VIEW  (1:7)", (270, 182))
    for yc in (-TY, TY):
        e.rect(yc - 90, 22, 180, 12, "thin")          # belt bottom
        e.rect(yc - 33, 34, 66, 40, "thin")           # horns
        for yy in (yc - 62, yc + 62):
            e.rect(yy - 20, 34, 40, 114.3, "hid")     # roller discs
        e.rect(yc - 4, 28, 8, 210, "hid")             # 72z pack
        e.rect(yc - 100 - 3, 30, 6, 220, "out")       # inner plate
        e.rect(yc + 100 - 3, 30, 6, 220, "out")       # outer plate
        e.rect(yc + 103 if yc > 0 else yc - 153, 58, 50, 150, "thin")  # UCFL
    # 48T wheels + axle + chain planes
    for yy in (-WHEEL_Y, WHEEL_Y):
        e.rect(yy - 2, 32.6, 4, 201, "hid")
        e.line(yy, 22, yy, 238, "cen")
    e.line(-410, ZC, 410, ZC, "out")
    e.rect(-160, 155, 320, 20, "thin")                # deck beam/pads
    for yy in (-134, 4):
        e.rect(yy, 250, 130, 190, "thin")             # motors
    e.line(-413, 0, 413, 0, "thin")                   # ground
    e.line(-413, 58, -413, -14, "dim")
    e.line(413, 58, 413, -14, "dim")
    e.dim_h(-413, 413, -63, "826", 7)
    e.dim_h(-260, 260, -154, "520", 7)
    e.dim_h(-90, 90, -244, "180", 7)
    e.dim_v(465, 0, 441, "441", 7)
    e.dim_v(420, 0, 267, "267", 7)
    e.dim_v(-440, 0, 175, "175", 7)
    s.save(OUT / "UCV2-GA-002")


def table(s, x, y, cols, rows, widths, title=None, fs=8.8, rh=7.2):
    """Simple sheet-space table, top-left at (x,y)."""
    w = sum(widths)
    if title:
        s.ax.text(x, y + 3, title, fontsize=fs + 0.8, weight="bold", va="bottom")
    for j, c in enumerate(cols):
        xx = x + sum(widths[:j])
        s.ax.add_patch(plt.Rectangle((xx, y - rh), widths[j], rh, fill=False,
                                     ec="k", lw=0.6))
        s.ax.text(xx + 1, y - rh / 2, c, fontsize=fs, weight="bold",
                  va="center")
    for i, row in enumerate(rows):
        yy = y - rh * (i + 2)
        for j, c in enumerate(row):
            xx = x + sum(widths[:j])
            s.ax.add_patch(plt.Rectangle((xx, yy), widths[j], rh, fill=False,
                                         ec="k", lw=0.4))
            s.ax.text(xx + 1, yy + rh / 2, str(c), fontsize=fs, va="center")
    return y - rh * (len(rows) + 2)


def sect_rect(v, cy, cz, w, h, bore=0.0, style="thin"):
    """Hatched section rectangle centred (cy,cz), horizontal bore through it."""
    if bore:
        th = (h - bore) / 2
        v.hatch_rect(cy - w / 2, cz + bore / 2, w, th)
        v.hatch_rect(cy - w / 2, cz - h / 2, w, th)
        v.line(cy - w / 2, cz + bore / 2, cy + w / 2, cz + bore / 2, style)
        v.line(cy - w / 2, cz - bore / 2, cy + w / 2, cz - bore / 2, style)
        v.line(cy - w / 2, cz + h / 2, cy + w / 2, cz + h / 2, "out")
        v.line(cy - w / 2, cz - h / 2, cy + w / 2, cz - h / 2, "out")
        v.line(cy - w / 2, cz - h / 2, cy - w / 2, cz + h / 2, "out")
        v.line(cy + w / 2, cz - h / 2, cy + w / 2, cz + h / 2, "out")
    else:
        v.hatch_rect(cy - w / 2, cz - h / 2, w, h)


def track_section(v):
    """Track + horns in the Y-Z plane, local y (track centre = 0)."""
    v.rect(-90, 22.0, 180, 12, "thin")          # bottom belt
    v.rect(-90, 232.6, 180, 12, "thin")         # top belt
    for y0 in (-84, -15, 54):
        v.rect(y0, 0, 30, 22, "thin")           # bottom lugs
        v.rect(y0, 244.6, 30, 22, "thin")       # top lugs
    v.rect(-33, 34.0, 66, 40, "thin")           # bottom horns
    v.rect(-33, 192.6, 66, 40, "thin")          # top horns


def ga_roller_section_v2():
    s = Sheet("UCV2-GA-003", "SECTION A-A - ROLLER STATION", 3, 14, "1:1.5",
              "IS2062 / EN8", "1 station", "-", notes=[
                  "1. Section at x=0, looking forward (+X). Local y=0 at track centre.",
                  "2. Two discs per station at y=+/-62, w40, D114.3, 1x 6205 each.",
                  "3. Disc bottom 34.05 on belt inner 34.04 (0.01 clearance).",
                  "4. Plate 6mm at y=+/-100; disc-to-plate gap 15.",
                  "5. Shaft D25 L260 clamped by collars at both plates; washer + R-pin.",
                  "6. No top roller: top run is unsupported (MBS: slack side).",
                  "7. Track overall height 267 at idler; top run 238.6 at mid-span."])
    v = View(s, 1 / 1.5, 150, 82, "SECTION A-A  (1:1.5)", (14, 282))
    track_section(v)
    # plates
    for yc in (-100, 100):
        sect_rect(v, yc, 140, 6, 220)
    # discs: outer rectangle with 25 bore, bearing at centre
    for yc in (-62, 62):
        sect_rect(v, yc, 91.2, 40, 114.3, bore=25)
        # bearing 6205 as a clean white cartridge (52 OD x 15 wide)
        v.rect(yc - 7.5, 65.2, 15, 52, "thin", fill="white")
        v.rect(yc - 7.5, 78.7, 15, 25, "thin")
    # shaft + collars + washer + pin
    v.rect(-130, 78.7, 260, 25, "thin")
    for yc in (-109, 109):
        v.rect(yc - 6, 71.2, 12, 40, "thin", fill="white")
    v.rect(115, 66.2, 4, 50, "thin")
    v.circle(121, 91.2, 3, "thin")
    v.line(-130, 91.2, 130, 91.2, "cen")
    # dims
    v.dim_h(-62, 62, 148.3, "124", 13)
    v.dim_h(-82, -42, 148.3, "40", 3)
    v.dim_h(-100, 100, 250, "200 gauge", 18)
    v.dim_h(-90, 90, 22, "180 rubber track", -36)
    v.dim_h(-33, 33, 74, "66 horn", 31)
    v.dim_v(-100, 0, 34.05, "34.05", -17)
    v.line(130, 91.2, 150, 91.2, "dim")
    v.dim_v(150, 0, 91.2, "91.2", 7)
    v.leader(62, 148.3, 95, 205, "Ø114.3 x40 disc (12 off)", ha="right")
    v.leader(125, 91.2, 150, 150, "Ø25 shaft L260")
    v.leader(-100, 70, -160, 30, "6mm plate (4 off)")
    v.leader(62, 65.2, 110, 30, "6205-2RS x1/disc")
    v.leader(-109, 71.2, -175, 150, "Ø25 collar x16", ha="left")
    v.leader(117, 66.2, 142, 75, "washer + R-pin")
    v.leader(0, 212.6, 30, 185, "track horns 66x40")
    s.save(OUT / "UCV2-GA-003")


def ga_drive_section():
    s = Sheet("UCV2-GA-004", "SECTION B-B - DRIVE STATION", 4, 14, "1:1.5",
              "EN8 / IS2062", "1 station", "-", notes=[
                  "1. Section at x=-500.6, looking forward. Local y=0 at track centre.",
                  "2. 48T plane y=-120 (global 140); 72z pack y=0 (global 260); axle centre z=133.3.",
                  "3. Axle D40 L300: keyways y=142..157 (48T) and 238..282 (72z hub).",
                  "4. UCFL208 outboard 363..413; axle end 410 -> 47mm engagement.",
                  "5. D40 collars (OD60) trap the 48T wheel and the 72z hub.",
                  "6. Chain plane y=140 (global), 120 inboard of track centre."])
    v = View(s, 1 / 1.5, 150, 82, "SECTION B-B  (1:1.5)", (14, 282))
    track_section(v)
    for yc in (-100, 100):
        sect_rect(v, yc, 140, 6, 220)
    # 48T wheel: tooth plate 138..142 (local -122..-118), hub -118..-103
    sect_rect(v, -120, 133.3, 4, 194.2, bore=40)
    v.rect(-118, 95.3, 15, 76, "thin", fill="white")
    v.rect(-118, 113.3, 15, 40, "thin")
    # 72z pack + hub (hub drawn in front as a clean cartridge)
    sect_rect(v, -4, 133.3, 8, 210.5, bore=40)
    sect_rect(v, 4, 133.3, 8, 210.5, bore=40)
    v.rect(-22, 95.3, 44, 76, "thin", fill="white")
    v.rect(-22, 113.3, 44, 40, "thin")
    # axle with keyway notches
    v.rect(-150, 113.3, 300, 40, "thin")
    v.rect(-118, 118.3, 15, 5, "out")       # keyway at 48T hub
    v.rect(-22, 118.3, 44, 5, "out")        # keyway at 72z hub
    # collars
    for yc in (-128, 28):
        v.rect(yc - 6, 103.3, 12, 60, "thin")
    # UCFL outboard: housing 50, bore 40
    sect_rect(v, 128, 133.3, 50, 150, bore=40)
    # dims
    v.dim_v(150, 103.3, 153.3, "Ø40 axle", 6)
    v.leader(-120, 171.3, -160, 240, "48T wheel 4 + 15 hub", ha="left")
    v.leader(0, 171.3, 35, 205, "72z pack 2x8 + hub 44")
    v.leader(153, 208.3, 165, 235, "UCFL208, 40 bore")
    v.leader(-128, 103.3, -165, 55, "Ø40 collar, Ø60 OD")
    v.leader(-10, 123.3, -65, 50, "keyway 12JS9")
    s.save(OUT / "UCV2-GA-004")


def p_plate():
    s = Sheet("UCV2-P-001", "SIDE PLATE - FLAT PATTERN", 5, 14, "1:4",
              "IS2062 E250Br 6mm", "4 (2L+2R)", "10.59 kg", notes=[
                  "1. ONE DXF, mirror for L/R; etch part mark on non-show face.",
                  "2. Hole datum: X=0 at mid, Z=0 at plate bottom; table z is global.",
                  "3. Break all edges 1x45; corner radii R15 laser.",
                  "4. Plate seats: D26 roller (3), D45 axle, 26x50 idler slot, 15x40 UCFL slots (clear D45).",
                  "5. 14x D14 holes take the beam flanges (schedule P-007).",
                  "6. 2 obround pockets 20R; no ribs (6mm dent-governed, see margins)."])
    v = View(s, 0.25, 210, 175, "FLAT PATTERN  (1:4)", (14, 282))
    v.dxf(str(CAD / "side_plate.dxf"))
    v.dim_h(-620, 620, -34, "1240", 8)
    v.dim_v(620, 0, 220, "220", 8)
    v.leader(560, 220, 530, 240, "6mm plate", ha="right")
    v.leader(-590, 190, -550, 240, "R15 (4)")
    v.leader(480.6, 103.3, 545, 140, "26x50 idler slot")
    v.leader(-510, 110, -580, 200, "Ø45 axle", ha="right")
    v.leader(-500.6, 43, -560, 75, "15x40 UCFL slot (2)", ha="right")
    v.leader(300, 61.2, 345, 95, "Ø26 roller (3)")
    v.text(0, -55, "DATUM: X0 = MID, Z0 = PLATE BOTTOM (z = local y + 30)",
           size=6, ha="center")
    rows = [
        ["A", "-300 / 0 / +300", "91.2", "Ø26", "3"],
        ["B", "+480.6", "133.3", "26 x 50", "1"],
        ["C", "-500.6", "133.3", "Ø45", "1"],
        ["D", "-500.6", "73 / 193", "15 x 40", "2"],
        ["E", "per P-007", "120..205", "Ø14", "14"],
        ["F1", "-280..-130", "160..230", "150 x 70", "1"],
        ["F2", "250..430", "140..230", "180 x 90", "1"],
    ]
    table(s, 12, 150, ["ID", "x", "z", "size", "qty"], rows,
          [10, 42, 34, 30, 10], "HOLE TABLE (mm)")
    s.save(OUT / "UCV2-P-001")


def roller_section(v, x0=0.0):
    # shell 114.3/105.3 x28 between 2x6 cheeks (overall 40)
    v.hatch_rect(x0 + 6, 52.65, 28, 4.5)
    v.hatch_rect(x0 + 6, -57.15, 28, 4.5)
    # cheeks OD114/ID65 x6
    for xx in (x0, x0 + 34):
        v.hatch_rect(xx, 32.5, 6, 24.65)
        v.hatch_rect(xx, -57.15, 6, 24.65)
    # hub 65/52 x40
    v.hatch_rect(x0, 26, 40, 6.5)
    v.hatch_rect(x0, -32.5, 40, 6.5)
    # bearing 6205 52/25 x15 (grey cartridge) + hatched shaft
    for zz in (12.5, -26):
        v.rect(x0 + 12.5, zz, 15, 13.5, "thin", fill="0.88")
        v.line(x0 + 16.5, zz, x0 + 16.5, zz + 13.5, "thin")
        v.line(x0 + 23.5, zz, x0 + 23.5, zz + 13.5, "thin")
    v.rect(x0 - 8, -12.5, 56, 25, "thin", fill="0.72")
    # bore + hub bore lines
    v.line(x0, 12.5, x0 + 40, 12.5, "thin")
    v.line(x0, -12.5, x0 + 40, -12.5, "thin")
    v.line(x0, 26, x0 + 40, 26, "thin")
    v.line(x0, -26, x0 + 40, -26, "thin")


def p_roller_v2():
    s = Sheet("UCV2-P-002", "ROLLER DRUM D114.3 - ASSEMBLY", 6, 14, "1:1",
              "MS-ERW + E250", "12", "1.37 + brg", notes=[
                  "1. Shell 100NB-M 114.3x4.5 x28 + 2x6 cheeks = 40 overall (STRUCTURAL).",
                  "2. Hub: 5 laser rings OD65/ID52x8 = 40 long, Loctite 638 stack.",
                  "3. 1x 6205-2RS press + circlip 52x1.5. Sealed, no grease.",
                  "4. Weld cheeks OUTSIDE only, 3mm fillet, stitch then continuous.",
                  "5. Grind tread flush; no bead above OD114.3; runout <1.0.",
                  "6. Fit: hub OD into cheek ID65 with 0.05-0.15 Loctite gap."])
    v = View(s, 1.0, 70, 180, "SECTION  (1:1)", (14, 282))
    roller_section(v, 0)
    v.line(0, 0, 40, 0, "cen")
    v.dim_h(0, 40, -75, "40", 8)
    v.dim_h(0, 6, 72, "6", 5)
    v.dim_v(52, 0, 57.15, "57.15", 5)
    v.dim_v(70, -57.15, 57.15, "Ø114.3", 6)
    v.leader(20, 57.15, 25, 80, "shell 114.3x4.5 x28")
    v.leader(3, 32.5, -25, 65, "cheek 6x2 (40 overall)")
    v.leader(20, 32.5, 55, 50, "hub 65/52 (5x8)")
    v.leader(20, 26, -25, 50, "6205-2RS + circlip", ha="left")
    # end view
    e = View(s, 1.0, 205, 180, "END VIEW  (1:1)", (183, 282))
    for r, st in ((57.15, "out"), (32.5, "thin"), (26, "thin"), (12.5, "thin")):
        e.circle(0, 0, r, st)
    e.center(0, 0, 62)
    e.dim_v(70, -57.15, 57.15, "Ø114.3", 6)
    e.leader(0, 57.15, 15, 72, "tread")
    e.leader(32.5, 0, 50, 0, "Ø65 hub")
    e.leader(26, 0, 45, -20, "Ø52 brg")
    e.leader(12.5, 0, 35, -35, "Ø25 bore")
    rows = [["1", "shell 114.3x4.5x28", "MS-ERW", "1", "0.34"],
            ["2", "cheek OD114/ID65x6", "E250", "2", "0.32"],
            ["3", "hub ring OD65/ID52x8", "E250", "5", "0.08"],
            ["4", "6205-2RS", "COTS", "1", "0.13"],
            ["5", "circlip 52x1.5", "COTS", "1", "-"]]
    table(s, 290, 250, ["#", "part", "mat", "qty", "kg"], rows,
          [8, 56, 20, 10, 10], "DRUM PARTS")
    s.save(OUT / "UCV2-P-002")


def p_idler_v2():
    s = Sheet("UCV2-P-003", "IDLER DISC D200 - ASSEMBLY", 7, 14, "1:1.5",
              "E250 + EN8", "4", "5.37 + brg", notes=[
                  "1. 5 laser rings OD200/ID150x8 = 40 wide tread, welded stack.",
                  "2. Web OD150/ID65x6 sits INSIDE the bore at mid-width (audit fix 2026-10-29).",
                  "3. Web is STRUCTURAL: connects tread to hub; weld both sides.",
                  "4. Hub: 5 rings OD65/ID52x8 = 40, Loctite 638.",
                  "5. 1x 6205-2RS press + circlip; no skim (flap-disc max 1mm).",
                  "6. Idler runs on belt inner R99.26; 0.7mm radial preload accepted.",
                  "7. D25 shaft shown for reference (see P-004)."])
    v = View(s, 1 / 1.5, 70, 150, "SECTION  (1:1.5)", (14, 282))
    # 5 tread rings 8 wide, OD200/ID150, z -100..100
    for x in (0, 8, 16, 24, 32):
        v.hatch_rect(x, 75, 8, 25)
        v.hatch_rect(x, -100, 8, 25)
    # central web OD150/ID65 x6 inside the bore (connects tread to hub)
    v.hatch_rect(17, 32.5, 6, 42.5)
    v.hatch_rect(17, -75, 6, 42.5)
    # hub 40 x 65/52
    v.hatch_rect(0, 26, 40, 6.5)
    v.hatch_rect(0, -32.5, 40, 6.5)
    # bearing + shaft
    for zz in (12.5, -26):
        v.rect(12.5, zz, 15, 13.5, "thin", fill="0.88")
        v.line(16, zz, 16, zz + 13.5, "thin")
        v.line(24, zz, 24, zz + 13.5, "thin")
    v.rect(-8, -12.5, 56, 25, "thin", fill="0.72")
    v.line(0, 12.5, 40, 12.5, "thin")
    v.line(0, -12.5, 40, -12.5, "thin")
    v.line(0, 26, 40, 26, "thin")
    v.line(0, -26, 40, -26, "thin")
    v.line(0, 0, 40, 0, "cen")
    v.dim_h(0, 40, -120, "40 (5x8)", 8)
    v.dim_v(40, -100, 100, "Ø200", 20)
    v.dim_v(40, 0, 100, "R100", 30)
    v.dim_v(40, -75, 75, "Ø150", 42)
    v.leader(4, 100, -10, 120, "5 rings 8mm")
    v.leader(20, 75, 35, 60, "web 150/65 x6")
    v.leader(20, 32.5, 35, 42, "hub 65/52")
    v.leader(20, 26, 20, -35, "6205 + circlip")
    e = View(s, 1 / 1.5, 220, 150, "END VIEW  (1:1.5)", (195, 282))
    for r, st in ((100, "out"), (75, "thin"), (32.5, "thin"),
                  (26, "thin"), (12.5, "thin")):
        e.circle(0, 0, r, st)
    e.center(0, 0, 105)
    e.dim_v(115, -100, 100, "Ø200", 6)
    e.leader(0, 75, 20, 90, "ID150")
    rows = [["1", "ring OD200/ID150x8", "E250", "5", "0.86"],
            ["2", "web OD150/ID65x6", "E250", "1", "0.68"],
            ["3", "hub ring OD65/ID52x8", "E250", "5", "0.08"],
            ["4", "6205-2RS", "COTS", "1", "0.13"],
            ["5", "circlip 52x1.5", "COTS", "1", "-"]]
    table(s, 305, 250, ["#", "part", "mat", "qty", "kg"], rows,
          [7, 48, 18, 10, 10], "DISC PARTS", rh=7.4)
    s.save(OUT / "UCV2-P-003")


def p_shafts():
    s = Sheet("UCV2-P-004", "SHAFT D25 x260  &  AXLE D40 x300", 8, 14, "1:2",
              "EN8 (bright)", "8 + 2", "1.00 / 2.93 kg", notes=[
                  "1. D25 shafts: 8 off L260, EN8; bearing seats Ø25 k5, ends g6; 1x Ø6 cross hole 9 from outboard end.",
                  "2. D40 axles: 2 off L300, EN8, h6; 4 keyways 12JS9 x5 deep (outsource).",
                  "3. Axle keyways: 32..47 and 128..172 from the 48T (inboard) end.",
                  "4. Collars/washer/R-pin shown dashed for position only (COTS).",
                  "5. Chamfer 1x45 both ends; protect keyways with tape for paint."])
    v = View(s, 0.5, 55, 218, "D25 SHAFT  (1:2)", (14, 282))
    v.rect(0, -12.5, 260, 25, "out")
    v.line(0, -12.5, 2, -10.5, "out")
    v.line(2, 10.5, 0, 12.5, "out")
    v.line(260, -10.5, 258, -12.5, "out")
    v.line(258, 12.5, 260, 10.5, "out")
    v.rect(15, -20, 12, 40, "hid")      # inner collar
    v.rect(233, -20, 12, 40, "hid")     # outer collar
    v.rect(245, -25, 4, 50, "hid")      # washer
    v.line(251, -12.5, 251, 12.5, "cen")
    v.circle(251, 0, 3, "hid")
    v.line(0, 0, 260, 0, "cen")
    v.dim_h(0, 260, -12.5, "260", -21)
    v.dim_v(260, -12.5, 12.5, "Ø25 k5", 6)
    v.leader(251, 0, 262, 34, "Ø6 cross hole, 9 from end", ha="left")
    v.leader(21, 20, 40, 40, "D25 collar (2)")
    v.leader(247, 25, 235, 45, "washer + R-pin", ha="right")
    # axle
    a = View(s, 0.5, 55, 120, "D40 AXLE  (1:2)", (14, 282 - 100))
    # outline with keyway notches in the top edge
    a.line(0, -20, 300, -20, "out")
    a.line(0, -20, 0, 20, "out")
    a.line(300, -20, 300, 20, "out")
    for x0, x1 in ((0, 32), (47, 128), (172, 300)):
        a.line(x0, 20, x1, 20, "out")
    for x0, ln in ((32, 15), (128, 44)):
        a.line(x0, 20, x0, 15, "out")
        a.line(x0, 15, x0 + ln, 15, "out")
        a.line(x0 + ln, 15, x0 + ln, 20, "out")
    a.line(0, 0, 300, 0, "cen")
    a.dim_h(0, 300, -20, "300", -15)
    a.dim_v(300, -20, 20, "Ø40 h6", 6)
    for x in (0, 32, 47):
        a.line(x, 20, x, 44, "dim")
    for x in (128, 172):
        a.line(x, 20, x, 58, "dim")
    a.dim_h(0, 32, 42, "32", 5)
    a.dim_h(32, 47, 33, "15", 4)
    a.dim_h(0, 128, 55, "128", 5)
    a.dim_h(128, 172, 46, "44", 4)
    a.leader(39, 20, 66, 82, "12JS9 x5 deep (4 off)")
    a.leader(150, 20, 210, 75, "72z hub keyway")
    a.text(0, -34, "INBOARD (48T)", size=6, ha="left")
    a.text(300, -34, "OUTBOARD", size=6, ha="right")
    s.save(OUT / "UCV2-P-004")


def p_sprocket():
    s = Sheet("UCV2-P-005", "SPROCKET 72z9  &  HUB 76/42", 9, 14, "1:2 / 1:1",
              "E250 8mm", "4 + 2", "1.52 / 1.13 kg", notes=[
                  "1. 72 mm pitch, 9 teeth, PD 210.51; laser 8mm E250, 2 plates/side pack.",
                  "2. Tooth profile per sprocket_72z9.dxf; tip R105.26, root R80.",
                  "3. Bore D40; hub carries the 12JS9 keyway (outsource).",
                  "4. Hub: 6 rings OD76/ID42x8 stacked 48, faced to 44; weld to pack.",
                  "5. Pack 2x8 = 16 wide, centred on track (y=+-260); hub 238..282."])
    v = View(s, 0.5, 95, 180, "SPROCKET 72z9  (1:2)", (14, 282))
    v.dxf(str(CAD / "sprocket_72z9.dxf"))
    v.center(0, 0, 108)
    v.dia(0, 0, 105.26, "PD 210.51 (R105.26)", 55, 10)
    v.leader(-56.6, 56.6, -92, 92, "root R80", ha="right")
    v.leader(20, 0, 70, -120, "Ø40 bore")
    v.leader(47.6, 27.5, 80, 60, "6x Ø14 on R55")
    v.leader(90, 45, 120, 85, "9 teeth x 72 pitch")
    v.text(-30, -138, "2 plates / side pack, 8mm each; 6x D14 mount holes", size=6)
    # hub section
    h = View(s, 1.0, 255, 180, "HUB  (1:1)", (228, 282))
    h.rect(0, -38, 44, 76, "thin")
    h.rect(0, -21, 44, 42, "thin", fill="white")
    # keyway 12 wide x5 deep, open into the bore
    h.line(16, 21, 16, 26, "out")
    h.line(16, 26, 28, 26, "out")
    h.line(28, 26, 28, 21, "out")
    h.line(0, 0, 44, 0, "cen")
    h.dim_h(0, 44, -52, "44", 8)
    h.dim_v(-15, -38, 38, "Ø76", 6)
    h.dim_v(58, -21, 21, "Ø42", 6)
    h.leader(14, 20, 30, 40, "12JS9 x5")
    h.text(22, -60, "6x8 rings, faced", size=6)
    rows = [["72z9", "9T x 72, PD210.51, D40, 8mm", "E250", "4", "1.52"],
            ["hub76", "OD76/ID42 x44, 12JS9", "E250", "2", "1.13"]]
    table(s, 300, 255, ["part", "description", "mat", "qty", "kg"], rows,
          [14, 60, 14, 9, 10], "DRIVE PARTS")
    s.save(OUT / "UCV2-P-005")


def p_chain():
    s = Sheet("UCV2-P-006", "CHAIN DRIVE 14T/48T  &  GUARD", 10, 14, "1:2",
              "428 chain / E250 guard", "2 sets", "-", notes=[
                  "1. 428 pitch 12.7; 14T pinion -> 48T wheel, ratio 3.43.",
                  "2. 60 links at C~170 (motor rail slots take up 10-15mm sag).",
                  "3. Chain plane y=+-140; pinion and 48T wheel both on 140.",
                  "4. Chain pull 835N at 81Nm; SF 12 on a 20kN 428 chain.",
                  "5. Guard 1.5mm, 140x270 flat, bend at fit-up; vent slots."])
    v = View(s, 0.5, 110, 150, "CHAIN GEOMETRY  (1:2)", (14, 282))
    c1, c2 = (0, 0), (40.6, 163.7)
    v.circle(*c1, 97.1, "cen")
    v.circle(*c1, 100.0, "thin")
    v.circle(*c2, 28.5, "cen")
    v.circle(*c2, 31.0, "thin")
    for p, q in external_tangents(c1, 97.1, c2, 28.5):
        v.line(p[0], p[1], q[0], q[1], "out")
    v.line(-10, 0, 50, 0, "cen")
    v.line(40.6, 0, 40.6, 170, "cen")
    v.dim((0, 0), (40.6, 163.7), "C 168.66", 10)
    v.line(0, 0, 0, 170, "dim")
    v.line(40.6, 163.7, 40.6, 170, "dim")
    v.line(0, 0, 60, 0, "dim")
    v.line(40.6, 163.7, 60, 163.7, "dim")
    v.dim_h(0, 40.6, 170, "40.6", 18)
    v.dim_v(55, 0, 163.7, "163.7", 6)
    v.dia(0, 0, 97.1, "48T PD194.2", 135, 8)
    v.dia(40.6, 163.7, 28.5, "14T PD57.1", 45, 8)
    # guard
    g = View(s, 0.2, 320, 180, "GUARD  (1:5)", (285, 282))
    g.dxf(str(CAD / "guard_flat_1p5mm.dxf"))
    g.dim_h(-70, 70, -150, "140", 7)
    g.dim_v(85, -135, 135, "270", 7)
    g.leader(0, 135, 20, 150, "1.5mm, bend at fit-up")
    rows = [["pitch", "12.7 (428)", "links", "60"],
            ["14T PD", "57.07", "48T PD", "194.20"],
            ["ratio", "3.43", "pull", "835 N"],
            ["C", "168.66", "sag", "10-15 mm"]]
    table(s, 300, 120, ["item", "value", "item", "value"], rows,
          [24, 30, 24, 26], "CHAIN DATA")
    s.save(OUT / "UCV2-P-006")


def p_frame():
    s = Sheet("UCV2-P-007", "FRAME SECTIONS, FLANGES & BOLT SCHEDULE", 11, 14,
              "1:1 / 1:2", "SHS40x3.2 / E250 8mm", "as listed", "see table", notes=[
                  "1. All beams SHS40x40x3.2, one size; 4x L320 fitted (+1 spare).",
                  "2. Rails 4x L300 at z210..250; motors sit at z250.",
                  "3. Flange mid/rear 140x70x8 (6 off: 4 mid + 2 rear) 4xM12; front 2 off 2xM12.",
                  "4. 28x M12 total per machine (14/side): mid 16, rear 8, front 4.",
                  "5. TVS 8.8, 80Nm, nylock + hardened washer + paint mark.",
                  "6. Weld 3mm fillet tube-to-flange, stitch then continuous."])
    v = View(s, 1.0, 60, 215, "SHS40  (1:1)", (14, 282))
    v.rect(0, 0, 40, 40, "out")
    v.rect(3.2, 3.2, 33.6, 33.6, "out")
    v.hatch_rect(0, 0, 40, 3.2)
    v.hatch_rect(0, 36.8, 40, 3.2)
    v.hatch_rect(0, 3.2, 3.2, 33.6)
    v.hatch_rect(36.8, 3.2, 3.2, 33.6)
    v.dim_h(0, 40, 0, "40", -10)
    v.dim_v(40, 0, 40, "40", 6)
    v.leader(20, 40, 25, 55, "3.2 wall")
    # flange mid
    f = View(s, 0.5, 150, 220, "FLANGE MID  (1:2)", (120, 282))
    f.rect(-70, -35, 140, 70, "out")
    for x, y in ((-50, -15), (50, -15), (-50, 15), (50, 15)):
        f.circle(x, y, 7, "out")
    f.dim_h(-70, 70, -35, "140", -20)
    f.dim_v(70, -35, 35, "70", 15)
    f.leader(50, 15, 60, 40, "4x Ø14")
    f.text(0, -100, "hole pitch 100 x 30", size=6)
    # flange front
    q = View(s, 0.5, 300, 220, "FLANGE FRONT  (1:2)", (270, 282))
    q.rect(-25, -35, 50, 70, "out")
    for y in (-15, 15):
        q.circle(0, y, 7, "out")
    q.dim_h(-25, 25, -35, "50", -20)
    q.dim_v(25, -35, 35, "70", 15)
    q.leader(0, 15, 10, 40, "2x Ø14")
    q.text(0, -100, "hole pitch 30", size=6)
    # beam lengths
    b = View(s, 0.2, 60, 150, "BEAM L320 / RAIL L300  (1:5)", (14, 190))
    b.rect(0, 0, 320, 40, "out")
    b.rect(0, 60, 300, 40, "out")
    b.dim_h(0, 320, -15, "320", 6)
    b.dim_h(0, 300, 45, "300", 6)
    rows = [["mid", "140x70x8", "4", "16"], ["rear", "140x70x8", "2", "8"],
            ["front", "50x70x8", "2", "4"], ["total", "-", "8", "28"]]
    table(s, 240, 150, ["joint", "flange", "qty", "M12"], rows,
          [22, 34, 16, 16], "BOLT SCHEDULE")
    s.save(OUT / "UCV2-P-007")


def p_deck():
    s = Sheet("UCV2-P-008", "DECK INTERFACE  &  LIFT LUGS", 12, 14, "1:1 / 1:10",
              "E250 / MS", "4 pads + 2 lugs", "see table", notes=[
                  "1. 4x deck pads 80x80x20 on mid beams, top z=175.",
                  "2. Pad centres x=+/-150, y=+/-100; M12 slot +/-3 + shim pack.",
                  "3. 2x lift lugs under the rear tie, x=-370, y=+/-100, z130..210.",
                  "4. Lug hole D20; sling rating to be marked at build.",
                  "5. Deck must clear motors (top z441) and overall W826."])
    v = View(s, 1.0, 60, 210, "DECK PAD  (1:1)", (14, 282))
    v.rect(-40, -40, 80, 80, "out")
    for x in (-25, 25):
        v.rect(x - 6, -15, 12, 30, "out", fill="white")
        v.circle(x, -15, 6, "out", fill="white")
        v.circle(x, 15, 6, "out", fill="white")
        v.line(x, -22, x, 22, "cen")
    v.dim_h(-40, 40, -60, "80", 7)
    v.dim_v(55, -40, 40, "80", 7)
    v.leader(0, 15, 25, 55, "2x M12 slot +/-3")
    v.text(0, -70, "80x80x20 pad (4)", size=6)
    # section
    e = View(s, 1.0, 190, 225, "SECTION  (1:1)", (160, 282))
    e.rect(-40, 0, 80, 10, "out")
    e.rect(-40, 10, 80, 10, "thin")
    e.dim_h(-40, 40, -12, "80", 6)
    e.dim_v(-50, 0, 20, "20", 5)
    e.leader(0, 10, 0, 32, "10 pad + 10 post")
    # lift lug: 60x80 face with D20 hole, 10 thick
    l = View(s, 1.0, 285, 190, "LIFT LUG  (1:1)", (250, 282))
    l.rect(-30, 0, 60, 80, "out")
    l.circle(0, 55, 10, "out")
    l.dim_h(-30, 30, -10, "60", 6)
    l.dim_v(42, 0, 80, "80", 6)
    l.leader(0, 55, -5, 35, "Ø20 sling hole", ha="right")
    side = View(s, 1.0, 360, 190, "SIDE", (345, 232))
    side.rect(0, 0, 10, 80, "out")
    side.dim_h(0, 10, -8, "10", 5)
    # position schematic
    p = View(s, 0.1, 120, 100, "PAD / LUG POSITIONS  (1:10)", (190, 145))
    p.rect(-620, -363, 1240, 726, "thin")
    for x in (-190, 110):
        for y in (-140, 60):
            p.rect(x, y, 80, 80, "out")
    for y in (-130, 70):
        p.rect(-400, y, 60, 60, "thin")
    p.dim_h(-150, 150, -450, "300", 6)
    p.dim_v(700, -100, 100, "200", 6)
    p.text(-150, -100, "P", size=8, weight="bold")
    p.text(-150, 100, "P", size=8, weight="bold")
    p.text(150, -100, "P", size=8, weight="bold")
    p.text(150, 100, "P", size=8, weight="bold")
    p.text(-370, -100, "L", size=8, weight="bold")
    p.text(-370, 100, "L", size=8, weight="bold")
    p.text(210, -470, "P = deck pad (4); L = lift lug (2)", size=6, ha="left")
    rows = [["deck pad", "80x80x20", "E250", "4", "0.95"],
            ["lift lug", "10x60x80, Ø20", "MS", "2", "0.35"]]
    table(s, 300, 120, ["part", "size", "mat", "qty", "kg"], rows,
          [22, 36, 16, 10, 12], "DECK PARTS")
    s.save(OUT / "UCV2-P-008")


def p_tension():
    s = Sheet("UCV2-P-009", "TENSIONER  &  SMALL PARTS", 13, 14, "1:1",
              "EN8 / MS", "4 sets", "see table", notes=[
                  "1. Idler slider travel 50; M12 rod pulls the eye/shaft.",
                  "2. Rod M12x110, eye 70x24x50, lug 30x24x40, nut M12 (19 A/F).",
                  "3. Set track sag 20 mid-span; jam nut after setting.",
                  "4. D25 collars x16 (OD40), D40 collars x4 (OD60), washers x8, pins x8."])
    v = View(s, 1.0, 70, 200, "TENSIONER  (1:1)", (14, 282))
    v.rect(-10, -20, 30, 40, "thin")          # lug
    v.line(-30, 0, 80, 0, "out")              # rod
    v.rect(25, -25, 70, 50, "thin")           # eye
    v.circle(60.6, 0, 13, "out")              # idler shaft bore
    v.rect(15, -12, 6, 24, "thin")            # nut
    v.rect(35, -12, 6, 24, "thin")
    v.dim_h(-10, 20, -32, "30", 6)
    v.dim_v(105, -25, 25, "50", 6)
    v.leader(60.6, 13, 75, 45, "idler shaft D26 bore")
    v.dim_h(-10, 40, -40, "50 travel", 7)
    v.balloon(-10, 0, -40, 63, 1)     # lug
    v.balloon(40, 0, 0, 63, 2)        # rod
    v.balloon(60.6, 0, 40, 63, 3)     # eye
    v.balloon(18, 12, 80, 63, 4)      # nut
    # collars
    c = View(s, 1.0, 240, 220, "Ø25 COLLAR  (1:1)", (210, 282))
    c.rect(0, -20, 12, 40, "out")
    c.rect(0, -12.5, 12, 25, "thin", fill="white")
    c.dim_h(0, 12, -30, "12", 5)
    c.dim_v(25, -20, 20, "D40", 5)
    c.leader(6, 20, 15, 30, "M6 grub")
    c.balloon(0, 20, -20, 45, 5)
    # D40 collar (separate view)
    d = View(s, 1.0, 225, 92, "Ø40 COLLAR  (1:1)", (200, 140))
    d.circle(0, 0, 30, "out")
    d.circle(0, 0, 20, "thin")
    d.dim_v(40, -30, 30, "OD60", 5)
    d.rect(50, -30, 12, 60, "out")
    d.dim_h(50, 62, -40, "12", 5)
    d.balloon(30, 30, 45, 55, 6)
    # washer + pin
    w = View(s, 1.0, 310, 220, "WASHER / PIN  (1:1)", (285, 282))
    w.circle(0, 0, 25, "out")
    w.circle(0, 0, 13, "thin")
    w.dim_v(35, -25, 25, "OD50", 5)
    w.leader(0, -25, 15, -40, "4 thk")
    w.rect(45, -3, 40, 6, "out")
    w.text(65, -10, "Ø6x40", size=6)
    rows = [["1", "tension lug", "30x24x40", "MS", "4", "0.20"],
            ["2", "rod", "M12x110", "EN8", "4", "0.10"],
            ["3", "eye", "70x24x50", "MS", "4", "0.52"],
            ["4", "nut", "M12 (19 A/F)", "8.8", "8", "0.02"],
            ["5", "collar", "Ø25 OD40x12", "COTS", "16", "0.07"],
            ["6", "collar", "Ø40 OD60x12", "COTS", "4", "0.15"]]
    table(s, 300, 120, ["#", "part", "size", "mat", "qty", "kg"], rows,
          [7, 22, 36, 14, 10, 12], "SMALL PARTS")
    s.save(OUT / "UCV2-P-009")


def p_bom():
    import json as _json
    data = _json.loads((CAD / "mass_audit.json").read_text())
    s = Sheet("UCV2-P-010", "PARTS LIST / BOM", 14, 14, "-", "as listed",
              "1 machine", f"{data['total_kg']} kg", notes=[
                  "1. Mass measured from STEP at 7850 kg/m3; bought parts catalogue.",
                  f"2. Total {data['total_kg']} kg incl tracks + motors (target 165 kg).",
                  "3. Laser parts: 8 DXFs (plate, sprocket, 2 backplates, hub76, 2 flanges, guard).",
                  "4. Outsource: 8 keyways + 2x 48T bore adapt; laser + machine shop only.",
                  "5. TVS 8.8 fasteners; 80Nm structural M12; nylock + paint mark.",
                  "6. Category masses rounded to 0.1 kg; total is the sum of item masses."])
    def sheet_ref(part):
        p = part.lower()
        if "roller drum" in p:
            return "P-002"
        if "idler drum" in p:
            return "P-003"
        if "plate" in p:
            return "P-001"
        if "roller" in p:
            return "P-002"
        if "idler" in p:
            return "P-003"
        if "shaft" in p or "axle" in p:
            return "P-004"
        if "sprocket" in p or "hub" in p:
            return "P-005"
        if "chain" in p or "guard" in p or "48t" in p:
            return "P-006"
        if "spacer 42.4" in p:
            return "P-002/3"
        if "6205" in p:
            return "P-002/3"
        if "ucfl" in p:
            return "GA-004"
        if any(k in p for k in ("beam", "rail", "flange", "spacer")):
            return "P-007"
        if "deck" in p or "lift" in p:
            return "P-008"
        if any(k in p for k in ("tension", "rod", "eye", "collar",
                                "washer", "pin", "nut")):
            return "P-009"
        if "6205" in p or "ucfl" in p:
            return "GA-003/4"
        if "motor" in p or "track" in p:
            return "GA-001"
        return "-"

    rows = []
    for i, it in enumerate(data["items"], 1):
        rows.append([i, it["category"], it["part"], sheet_ref(it["part"]),
                     it["qty"], f"{it['unit_kg']:.3f}", f"{it['mass_kg']:.1f}"])
    table(s, 12, 270, ["#", "cat", "part", "sheet", "qty", "kg ea", "kg"],
          rows, [7, 18, 100, 16, 8, 14, 14], "PARTS LIST (as drawn)",
          fs=8.4, rh=6.4)
    cat = [[k, v] for k, v in sorted(data["category_kg"].items(),
                                     key=lambda kv: -kv[1])]
    cat.append(["TOTAL", data["total_kg"]])
    table(s, 260, 270, ["category", "kg"], cat, [45, 25], "MASS BY CATEGORY",
          fs=7, rh=6.0)
    s.save(OUT / "UCV2-P-010")


def image_sheet(no, title, img, idx, qty, mass, notes):
    s = Sheet(no, title, idx, 14, "NTS", "MS / E250 / EN8", qty, mass,
              notes=notes)
    ax = s.fig.add_axes([0.025, 0.215, 0.95, 0.745])
    ax.imshow(plt.imread(OUT / img), aspect="equal")
    ax.axis("off")
    s.save(OUT / no)


def p_roller():
    image_sheet("UCV2-P-002", "ROLLER STATION V3 - SIMPLE SPOOL",
                "v3_roller_section.png", 6, "12 drums",
                "3.54 kg/stn", notes=[
                    "1. V3 simple spool: 2 identical drums per station at +/-62.",
                    "2. Pipe + backplate + welded 65/52x22 seat; 52 H7 after welding.",
                    "3. 6205 outer race press in seat; inner race press on Ø25 shaft.",
                    "4. Loose 42.4/35.5x109 spacer between bearing inner races.",
                    "5. No Loctite, no ring stack, no central weld; open outer end.",
                    "6. Bearing at tread centre; track horn clearance 7.5 mm."])


def p_idler():
    image_sheet("UCV2-P-003", "IDLER STATION V3 - SIMPLE SPOOL",
                "v3_idler_section.png", 7, "4 drums",
                "6.33 kg/stn", notes=[
                    "1. V3 simple spool: 2 identical drums per station at +/-62.",
                    "2. 200 OD x5 pipe + backplate + welded 65/52x22 seat.",
                    "3. 6205 press fits; loose 42.4/35.5x109 spacer.",
                    "4. No Loctite, no ring stack, no central weld.",
                    "5. Idler pipe bore clears track horn by 24.2 mm.",
                    "6. Same Ø25 shaft/collars as the roller station."])


def ga_roller_section():
    image_sheet("UCV2-GA-003", "SECTION A-A - ROLLER STATION (V3)",
                "v3_roller_section.png", 3, "1 station", "3.54 kg",
                notes=[
                    "1. V3 simple spool replaces the paired-disc roller.",
                    "2. Track horn tip shown; clearance to spacer 7.5 mm.",
                    "3. Belt/plates/machine envelope per GA-001/GA-002.",
                    "4. 2 identical drums; bearing at tread centre.",
                    "5. No Loctite, no ring stacks, no central weld."])


if __name__ == "__main__":
    which = sys.argv[1:] or [
        "ga_side", "ga_plan", "ga_roller_section", "ga_drive_section",
        "p_plate", "p_roller", "p_idler", "p_shafts", "p_sprocket",
        "p_chain", "p_frame", "p_deck", "p_tension", "p_bom"]
    for name in which:
        globals()[name]()
        print("drew", name)
