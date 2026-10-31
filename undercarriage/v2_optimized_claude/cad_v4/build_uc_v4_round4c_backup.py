"""build_uc_v4.py - parametric master for the Kerala flail-mower undercarriage (v2_optimized_claude).
Run:  python -I build_uc_v4.py        (writes uc_v4_assembly.step, uc_v4.json beside this file)
Datum mm: ground lug tip z=0, X travel (+fwd), Y across (right side y>0, left = mirror), Z up.
Round 1 = structure + running gear + drive. NOT yet modelled: fasteners (M12/M14/M16 bolts, keys, keyseats),
chain + guard, motor rails, deck mounts, lift lugs, DXF export. Every catalogue number lives in catalogue.json.
Inputs traced: ACETRAX PDF row 180/60 (IGB24 OGB62 C25 D24.5), 37 links = repo size code, E=22 frozen by user.
"""
import json, math, os, itertools
import numpy as np
from scipy.spatial import ConvexHull
from build123d import *
from bd_warehouse.sprocket import Sprocket
from bd_warehouse.fastener import HexNut, PlainWasher, HexHeadScrew

HERE = os.path.dirname(os.path.abspath(__file__))
CAT = json.load(open(os.path.join(HERE, 'catalogue.json')))
RHO = 7.85e-6  # kg/mm3 steel

# ---------------- parameter block ----------------
pitch, N_LINK, Wt, Z_SPR = 60.0, 37, 180.0, 10
lug, belt = 22.0, 12.0
Rp = pitch / math.sin(math.pi / Z_SPR) / 2            # sprocket pitch radius 97.08
Rtip = Rp * 1.005                                     # +0.5% facet pitch (repo note, unverified in patent)
Rroot = Rp - 25.0
R_in_s = Rp - 6.0                                     # belt-inner radius at sprocket (v2 rule)
OD_ID, T_ID = CAT['pipe_8NB_idler']['od_mm'], CAT['pipe_8NB_idler']['wall_mm']
R_in_i = OD_ID / 2                                    # belt-inner radius at idler
R_pi = R_in_i + 6.0                                   # idler pitch-line radius
Ld = pitch * N_LINK
d_r = R_pi - Rp
C = (Ld - math.pi * (R_pi + Rp)) / 2
for _ in range(6):
    d = math.hypot(C, d_r); b = math.asin(d_r / d)
    C = (Ld - math.pi * (R_pi + Rp) - 2 * b * d_r) / 2
xs, xi = -C / 2, C / 2
zs, zi = lug + belt + R_in_s, lug + belt + R_in_i
RR = CAT['pipe_4NB_roller']['od_mm'] / 2; zr = lug + belt + RR
ROLLERS = [-200.0, 0.0, 195.0]
YC = 430.0                                            # track centre (gauge 860)
TPL = 6.0                                             # side plate thickness
Y_PIN, Y_POUT = YC - 100, YC + 100                    # plate centres
YIN_F = Y_PIN + TPL / 2 - TPL                          # inner plate: faces 327..333
FACE_IN_O, FACE_OUT_I = Y_PIN + TPL / 2, Y_POUT - TPL / 2   # 333 / 527 (between-plate faces)
FACE_IN_I, FACE_OUT_O = Y_PIN - TPL / 2, Y_POUT + TPL / 2   # 327 / 533 (outer faces)
U = CAT['ucfl208']; BRG = CAT['brg6205_2rs']

parts = {}   # name -> (shape, category, mass_kg_override_or_None)
def add(name, shape, cat, mass=None):
    parts[name] = (shape, cat, mass)

def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)

def cy(ro, ri, y0, y1, x, z):
    L = y1 - y0
    s = Cylinder(ro, L)
    if ri > 0: s = s - Cylinder(ri, L + 2)
    return Pos(x, (y0 + y1) / 2, z) * Rot(X=90) * s

# ---------------- side plates ----------------
PTS = [(-505, 30), (520, 30), (545, 55), (545, 255), (515, 270), (-440, 270), (-520, 200), (-520, 55)]
SPC_X, SPC_Z = (-165.0, 165.0), 175.0       # through-spacer tubes joining inner and outer plate
PAD_T = 8.0
BEAM_BOLTS = {'beam_rear': [(-27, -27), (27, -27), (-27, 27), (27, 27)], 'beam_mid1': [(27, 27), (-27, -27)],
              'beam_mid2': [(27, 27), (-27, -27)], 'beam_front': [(-27, -27), (27, -27)]}
BEAM_POS = {'beam_rear': (-230.0, 160.0), 'beam_mid1': (-100.0, 160.0), 'beam_mid2': (100.0, 160.0), 'beam_front': (470.0, 90.0)}  # ROUND3B
def plate(yc, inner=False):
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):
            Polygon(*PTS, align=None)
            for x in ROLLERS:
                with Locations((x, zr)): Circle(13.0, mode=Mode.SUBTRACT)
            with Locations((xs, zs)): Circle(22.5, mode=Mode.SUBTRACT)
            for dz in (-U['J_bolt_spacing_mm'] / 2, U['J_bolt_spacing_mm'] / 2):
                with Locations((xs, zs + dz)): Circle(U['N_bolt_hole_mm'] / 2, mode=Mode.SUBTRACT)
            with Locations((xi + 5, zi)): SlotOverall(85.5, 25.5, mode=Mode.SUBTRACT)
            for wx0, wx1 in ((-300.0, -110.0), (-80.0, 110.0), (140.0, 280.0)):      # ROUND4B windows, webs >= 30 mm
                with Locations(((wx0 + wx1) / 2, 230.0)): RectangleRounded(wx1 - wx0, 40.0, 10.0, mode=Mode.SUBTRACT)
            for sx in SPC_X:
                with Locations((sx, SPC_Z)): Circle(8.5, mode=Mode.SUBTRACT)
            if inner:
                for nm_, (bx, bz) in BEAM_POS.items():
                    for dx, dz in BEAM_BOLTS[nm_]:
                        with Locations((bx + dx, bz + dz)): Circle(5.1, mode=Mode.SUBTRACT)   # M12 tap drill 10.2 (ROUND3C)
            with Locations((-100, 87.0)): RectangleRounded(130, 50, 10, mode=Mode.SUBTRACT)  # between roller holes; z 62..112 keeps >=15 mm to the beam bolt holes (z>=127.9)
            with Locations((100, 87.0)): RectangleRounded(130, 50, 10, mode=Mode.SUBTRACT)
        extrude(amount=TPL)
    return Pos(0, yc + TPL / 2, 0) * p.part
add('plate_in', plate(Y_PIN, True), 'structure'); add('plate_out', plate(Y_POUT, False), 'structure')

# ---------------- UCFL208 (envelope from NSK dims) ----------------
def ucfl(inner):
    fl, hs = U['A1_flange_thk_mm'], U['A0_total_mm'] - U['A1_flange_thk_mm']
    if inner:  y0f, y1f, y0h, y1h = FACE_IN_I - fl, FACE_IN_I, FACE_IN_I - fl - hs, FACE_IN_I - fl
    else:      y0f, y1f, y0h, y1h = FACE_OUT_O, FACE_OUT_O + fl, FACE_OUT_O + fl, FACE_OUT_O + fl + hs
    flange = box(xs - U['L_flange_width_mm'] / 2, xs + U['L_flange_width_mm'] / 2, y0f, y1f,
                 zs - U['H_flange_len_mm'] / 2, zs + U['H_flange_len_mm'] / 2)
    flange = flange - cy(8, 0, y0f - 1, y1f + 1, xs, zs - 72) - cy(8, 0, y0f - 1, y1f + 1, xs, zs + 72)
    house = cy(42.0, 20.0, y0h, y1h, xs, zs)     # housing OD ~84: UNVERIFIED
    flange = flange - cy(20.0, 0, y0f - 1, y1f + 1, xs, zs)
    return flange + house
add('ucfl_in', ucfl(True), 'drive', U['mass_kg']); add('ucfl_out', ucfl(False), 'drive', U['mass_kg'])

# ---------------- drive axle, sprocket z10 laminate, hub, collars ----------------
KEYS = [(236.0, 272.0), (410.0, 450.0)]       # chain-wheel key 12x8x36, sprocket-hub key 12x8x40 (DIN 6885-A, t1=5.0 t2=3.3 UNVERIFIED)
def seat(y0, y1): return box(xs - 6, xs + 6, y0, y1, zs + 15.0, zs + 21.0)
def hubway(y0, y1): return box(xs - 6, xs + 6, y0, y1, zs + 18.5, zs + 23.3)
ax = cy(20.0, 0, 225.0, FACE_OUT_O + U['A0_total_mm'] - 1.0, xs, zs)
for k0, k1 in KEYS: ax = ax - seat(k0, k1)
add('axle', ax, 'drive')   # ends 1 mm inside outer UCFL face
for i_, (k0, k1) in enumerate(KEYS): add(f'key{i_}', box(xs - 6, xs + 6, k0, k1, zs + 15.0, zs + 23.0), 'drive')
add('collar_a', cy(30.0, 20.0, 396.0, 408.0, xs, zs), 'drive'); add('collar_b', cy(30.0, 20.0, 452.0, 464.0, xs, zs), 'drive')
add('hub', cy(38.0, 20.0, 408.0, 452.0, xs, zs) - hubway(*KEYS[1]), 'drive')

def sprocket_plate(y0, y1):
    pts = []
    n = Z_SPR
    ar = math.asin(14.0 / Rroot); at = math.asin(9.0 / Rtip)
    for k in range(n):
        c = 2 * math.pi * k / n
        nxt = 2 * math.pi * (k + 1) / n
        pts += [(Rroot, c - ar), (Rtip, c - at), (Rtip, c + at), (Rroot, c + ar)]
        for j in range(1, 6):
            a = (c + ar) + (nxt - ar - (c + ar)) * j / 6
            pts.append((Rroot, a))
    xy = [(r * math.cos(a), r * math.sin(a)) for r, a in pts]
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):
            Polygon(*xy, align=None)
            Circle(38.0, mode=Mode.SUBTRACT)
            for k in range(5):                       # 5 kidney windows r46..r64
                a0, a1 = math.radians(72 * k + 22), math.radians(72 * k + 50)
                arc_o = [(62 * math.cos(a0 + (a1 - a0) * j / 12), 62 * math.sin(a0 + (a1 - a0) * j / 12)) for j in range(13)]
                arc_i = [(48 * math.cos(a1 - (a1 - a0) * j / 12), 48 * math.sin(a1 - (a1 - a0) * j / 12)) for j in range(13)]
                Polygon(*(arc_o + arc_i), align=None, mode=Mode.SUBTRACT)
            for k in range(5):
                a = math.radians(72 * k)
                with Locations((55 * math.cos(a), 55 * math.sin(a))): Circle(6.5, mode=Mode.SUBTRACT)
        extrude(amount=y1 - y0)
    # sketch plane normal is -Y; placed so slab spans y0..y1
    return Pos(xs, y1, zs) * p.part
add('spr_a', sprocket_plate(YC - 8, YC), 'drive'); add('spr_b', sprocket_plate(YC, YC + 8), 'drive')

# chain wheel (bd_warehouse roller-chain sprocket) + boss, 14T pinion
CW_N = int(os.environ.get('UC_WHEEL_T', 48)); PIN_N = int(os.environ.get('UC_PINION_T', 14))   # ROUND4C swappable: wheel (axle) and pinion (motor) teeth
PCD_CW = 100.0                                                       # bolt circle of the swappable chain-wheel plate (6 x M8)
_PDw, _PDp = 12.7 / math.sin(math.pi / CW_N), 12.7 / math.sin(math.pi / PIN_N)
_cd0 = (_PDw + _PDp) / 2 + 70.0                                       # target centre distance: wheel R + pinion R + 70 mm
_lk0 = 2 * _cd0 / 12.7 + (PIN_N + CW_N) / 2 + ((CW_N - PIN_N) / (2 * math.pi)) ** 2 * 12.7 / _cd0
CH_LINKS = int(os.environ.get('UC_LINKS', 2 * round(_lk0 / 2)))     # even link count (no offset link)
cw = Sprocket(num_teeth=CW_N, chain_pitch=12.7, roller_diameter=8.51, thickness=6.0, bolt_circle_diameter=PCD_CW, num_mount_bolts=6, mount_bolt_diameter=9.0, bore_diameter=64.0)
add('chainwheel', Pos(xs, 231.0, zs) * Rot(X=90) * cw, 'drive')          # swappable plate y 228..234, bolted to the hub flange
cwf = cy(60.0, 20.0, 234.0, 242.0, xs, zs) - hubway(234.0, 242.0)
for k_ in range(6):
    a_ = math.radians(60 * k_); cwf = cwf - cy(3.4, 0, 233.0, 243.0, xs + PCD_CW / 2 * math.cos(a_), zs + PCD_CW / 2 * math.sin(a_))   # M8 tap drill
add('cw_flange', cwf, 'drive')
add('chainwheel_boss', cy(30.0, 20.0, 242.0, FACE_IN_I - U['A0_total_mm'] - 2.0, xs, zs) - hubway(242.0, 275.0), 'drive')
_m8 = HexHeadScrew(size='M8-1.25', length=16.0, fastener_type='iso4017')
for k_ in range(6):
    a_ = math.radians(60 * k_); add(f'cw_bolt{k_}', Pos(xs + PCD_CW / 2 * math.cos(a_), 228.0, zs + PCD_CW / 2 * math.sin(a_)) * Rot(X=90) * _m8, 'drive')
pin = Sprocket(num_teeth=PIN_N, chain_pitch=12.7, roller_diameter=8.51, thickness=6.0)
# pinion plane y=231 = chain-wheel plane (motor shaft y 218..246)
def chain_links(Cc, z1=PIN_N, z2=CW_N, p=12.7): return 2 * Cc / p + (z1 + z2) / 2 + ((z2 - z1) / (2 * math.pi)) ** 2 * p / Cc
lo_, hi_ = 120.0, 260.0
for _ in range(60):
    mid_ = (lo_ + hi_) / 2
    if chain_links(mid_) < CH_LINKS: lo_ = mid_
    else: hi_ = mid_
CH_C = (lo_ + hi_) / 2                                  # centre distance for exactly CH_LINKS links
add('motor_ph', cy(50.0, 0, 80.0, 218.0, xs, zs + CH_C), 'drive', CAT['motor_bm1418zxf']['mass_kg_used'])   # envelope = PLACEHOLDER (no drawing); mass 7.12 kg from one listing (3.0/7.12/10.66 disputed)
add('motor_shaft_ph', cy(10.0, 0, 218.0, 246.0, xs, zs + CH_C), 'drive')
add('pinion', Pos(xs, 231.0, zs + CH_C) * Rot(X=90) * (pin - Cylinder(10, 10)), 'drive')

# ---------------- spools: roller drums (3 stations) and idler drums ----------------
def spool_set(tag, xc, zc, Ro, wall, ext=0.0, onepiece=False):
    """one station: two drums (pipe+backplate+seat ring+6205), spacers, circlips. Right side."""
    Ri = Ro - wall
    thr = 19.0 if ext > 0 else 33.0     # threaded end length: thin nut (idler) vs full nut + washer + 7 mm (rollers)
    for side, mirror in (('i', 1), ('o', -1)):
        def Y(y): return y if mirror == 1 else 2 * YC - y      # mirror about track centre
        def span(a, b):
            lo, hi = sorted((Y(a), Y(b))); return lo, hi
        lo, hi = span(355.0, 395.0);   add(f'{tag}_pipe_{side}', cy(Ro, Ri, lo, hi, xc, zc), 'running')
        lo, hi = span(357.0, 361.0);   add(f'{tag}_back_{side}', cy(Ri, 32.5 if onepiece else 23.0, lo, hi, xc, zc), 'running')   # 4 mm, recessed 2 mm (ROUND4B)
        if not onepiece:
            lo, hi = span(361.0, 379.0)
            seat = cy(32.5, 26.0, lo, hi, xc, zc)
            g0, g1 = span(376.0, 378.15); seat = seat - cy(27.5, 20.0, g0, g1, xc, zc)
            add(f'{tag}_seat_{side}', seat, 'running')
        lo, hi = span(361.0, 376.0);   add(f'{tag}_brg_{side}', cy(26.0, 12.5, lo, hi, xc, zc), 'running', BRG['mass_kg'])
        lo, hi = span(376.075, 378.075); add(f'{tag}_clip_{side}', cy(27.5, 23.0, lo, hi, xc, zc), 'running')
        lo, hi = span(333.0, 361.0) if mirror == 1 else span(333.0, 361.0)
        sp = (FACE_IN_O, 361.0) if mirror == 1 else (499.0, FACE_OUT_I)
        add(f'{tag}_spc_end_{side}', cy(16.0, 12.75, sp[0], sp[1], xc, zc), 'running')
    add(f'{tag}_spc_mid', cy(16.0, 12.75, 376.0, 484.0, xc, zc), 'running')
    if onepiece:   # one rotating weldment: hub tube OD65 bored 46 with two 52 bearing seats + circlip grooves; 70 mm centre groove for the horns
        hub = cy(32.5, 23.0, 355.0, 505.0, xc, zc)
        for (a0, a1, g0, g1) in ((361.0, 378.15, 376.0, 378.15), (481.85, 499.0, 481.85, 484.0)):
            hub = hub - cy(26.0, 0, a0, a1, xc, zc) - cy(27.5, 0, g0, g1, xc, zc)
        add(f'{tag}_hubtube', hub, 'running')
    add(f'{tag}_shaft', cy(12.5, 0, 329.0 - ext, 531.0 + ext, xc, zc) + cy(12.0, 0, 329.0 - ext - thr, 329.0 - ext, xc, zc) + cy(12.0, 0, 531.0 + ext, 531.0 + ext + thr, xc, zc), 'running')
    for y_wash, y_nut, sgn in ((322.7, 301.2, 1), (533.0, 537.3, -1)):
        pass
    nut = HexNut(size='M24-3', fastener_type='iso4035' if ext > 0 else 'iso4032'); wsh = PlainWasher(size='M24', fastener_type='iso7089')
    nb = nut.bounding_box().size.Z; wb = wsh.bounding_box().size.Z
    # bd_warehouse parts extend along +Z from the origin; Rot(X=+90) sends +Z to -Y, Rot(X=-90) to +Y.
    for side, (yw0, yn0, rx) in (('i', (FACE_IN_I - ext, FACE_IN_I - ext - wb, 90)), ('o', (FACE_OUT_O + ext, FACE_OUT_O + ext + wb, -90))):
        add(f'{tag}_wsh_{side}', Pos(xc, yw0, zc) * Rot(X=rx) * wsh, 'running')
        add(f'{tag}_nut_{side}', Pos(xc, yn0, zc) * Rot(X=rx) * nut, 'running')
for k, x in enumerate(ROLLERS): spool_set(f'rol{k}', x, zr, RR, CAT['pipe_4NB_roller']['wall_mm'])
spool_set('idl', xi, zi, R_in_i, T_ID, ext=30.0, onepiece=True)   # ext: shaft passes through the tension blocks (y 297..327 / 533..563)

# ---------------- through-spacer tubes: tie inner and outer plate together (review defect 2) ----------------
nut16 = HexNut(size='M16-2', fastener_type='iso4032'); wsh16 = PlainWasher(size='M16', fastener_type='iso7089')
nb16, wb16 = nut16.bounding_box().size.Z, wsh16.bounding_box().size.Z
for k, sx in enumerate(SPC_X):
    add(f'spc{k}_tube', cy(21.2, 18.0, FACE_IN_O, FACE_OUT_I, sx, SPC_Z), 'structure')
    add(f'spc{k}_rod', cy(8.0, 0, 305.0, 555.0, sx, SPC_Z), 'structure')
    for side, (yw0, yn0, rx) in (('i', (FACE_IN_I, FACE_IN_I - wb16, 90)), ('o', (FACE_OUT_O, FACE_OUT_O + wb16, -90))):
        add(f'spc{k}_wsh_{side}', Pos(sx, yw0, SPC_Z) * Rot(X=rx) * wsh16, 'structure')
        add(f'spc{k}_nut_{side}', Pos(sx, yn0, SPC_Z) * Rot(X=rx) * nut16, 'structure')

# ---------------- tensioner: block on idler shaft, M16 rod, anchor lug ----------------
for side, (yb0, yb1) in (('i', (FACE_IN_I - 30.0, FACE_IN_I)), ('o', (FACE_OUT_O, FACE_OUT_O + 30.0))):
    ym = (yb0 + yb1) / 2
    blk = box(xi - 15, xi + 15, yb0, yb1, zi - 20, zi + 20) - cy(12.75, 0, yb0 - 1, yb1 + 1, xi, zi)
    add(f'tens_block_{side}', blk, 'running')
    lug_hole = Pos(520.0, ym, zi) * Rot(Y=90) * Cylinder(8.5, 20.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    add(f'tens_lug_{side}', box(520.0, 528.0, yb0, yb1, zi - 22.0, zi + 22.0) - lug_hole, 'structure')
    add(f'tens_rod_{side}', Pos(xi + 15.0, ym, zi) * Rot(Y=90) * Cylinder(8.0, 560.0 - (xi + 15.0), align=(Align.CENTER, Align.CENTER, Align.MIN)), 'running')
    add(f'tens_wsh_{side}', Pos(528.0, ym, zi) * Rot(Y=90) * wsh16, 'running')
    add(f'tens_nut_{side}', Pos(528.0 + wb16, ym, zi) * Rot(Y=90) * nut16, 'running')
# ---------------- UCFL M14 bolts (2 per UCFL), beam-flange M12 bolts ----------------
nut14 = HexNut(size='M14-2', fastener_type='iso4032'); wsh14 = PlainWasher(size='M14', fastener_type='iso7089'); wb14 = wsh14.bounding_box().size.Z
for side, (yh, dirn) in (('i', (FACE_IN_I - U['A1_flange_thk_mm'], 1)), ('o', (FACE_OUT_O + U['A1_flange_thk_mm'], -1))):
    for j, dz in enumerate((-U['J_bolt_spacing_mm'] / 2, U['J_bolt_spacing_mm'] / 2)):
        scr = HexHeadScrew(size='M14-2', length=40.0, fastener_type='iso4014')
        rx = 90 if dirn == 1 else -90
        add(f'ucflbolt_{side}{j}', Pos(xs, yh, zs + dz) * Rot(X=rx) * scr, 'drive')
        yface = FACE_IN_O if dirn == 1 else FACE_OUT_I           # nut sits on the between-plates face
        add(f'ucflwsh_{side}{j}', Pos(xs, yface, zs + dz) * Rot(X=-rx) * wsh14, 'drive')
        add(f'ucflnut_{side}{j}', Pos(xs, yface + dirn * wb14, zs + dz) * Rot(X=-rx) * nut14, 'drive')
nut12 = HexNut(size='M12-1.75', fastener_type='iso4032'); wsh12 = PlainWasher(size='M12', fastener_type='iso7089'); wb12 = wsh12.bounding_box().size.Z
for nm_, (bx, bz) in BEAM_POS.items():
    pad = box(bx - 35, bx + 35, FACE_IN_I - PAD_T, FACE_IN_I, bz - 35, bz + 35)
    for dx_, dz_ in BEAM_BOLTS[nm_]: pad = pad - cy(5.1, 0, FACE_IN_I - PAD_T - 1, FACE_IN_I + 1, bx + dx_, bz + dz_)
    add(f'{nm_}_pad', pad, 'structure')
    for k, (dx, dz) in enumerate(BEAM_BOLTS[nm_]):
        scr = HexHeadScrew(size='M12-1.75', length=25.0, fastener_type='iso4014')
        yf = FACE_IN_I - PAD_T - 6.0                         # flange inboard face
        add(f'{nm_}_wsh{k}', Pos(bx + dx, yf, bz + dz) * Rot(X=90) * wsh12, 'structure')
        add(f'{nm_}_bolt{k}', Pos(bx + dx, yf - wb12, bz + dz) * Rot(X=90) * scr, 'structure')   # tip ends ~2 mm past plate (tapped pad+plate)

# ---------------- cross beams ----------------
SHS, SW = CAT['shs40']['od_mm'], CAT['shs40']['wall_mm']
PAD_T = 8.0
BL = 2 * (FACE_IN_I - PAD_T - 6.0)      # tube length between the two flanges (flange inboard of the 8 mm pad)
def beam(x, z):
    t = Pos(x, 0, z) * (Box(SHS, BL, SHS) - Box(SHS - 2 * SW, BL + 2, SHS - 2 * SW))
    return t
BEAMS = [(n_, p_[0], p_[1]) for n_, p_ in BEAM_POS.items()]
BEAM_SOL = {}
for nm, x, z in BEAMS:
    BEAM_SOL[nm] = beam(x, z)

# ---------------- track envelope ----------------
def hull_poly(rs, ri_):
    pts = []
    for a in np.linspace(0, 2 * math.pi, 240, endpoint=False):
        pts.append((xs + rs * math.cos(a), zs + rs * math.sin(a)))
        pts.append((xi + ri_ * math.cos(a), zi + ri_ * math.sin(a)))
    pts = np.array(pts); h = ConvexHull(pts)
    return [tuple(pts[i]) for i in h.vertices]
def track(yc):
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):
            Polygon(*hull_poly(R_in_s + belt + lug, R_in_i + belt + lug), align=None)
            Polygon(*hull_poly(R_in_s, R_in_i), align=None, mode=Mode.SUBTRACT)
        extrude(amount=Wt)
    return Pos(0, yc + Wt / 2, 0) * p.part
add('track', track(YC), 'track', CAT['track_180x60x37']['mass_kg_each'])

# ---------------- mirror to left, assemble, gates ----------------
right = dict(parts)
asm = {}
for n, (s, c, m) in right.items():
    asm[n + '_R'] = (s, c, m)
    asm[n + '_L'] = (s.mirror(Plane.XZ), c, m)
for n, s in BEAM_SOL.items():
    asm[n] = (s, 'structure', None)
    # end flanges (6 mm) against the inner plate inner faces
for n, x, z in BEAMS:
    for sgn in (1, -1):
        y0f_, y1f_ = (FACE_IN_I - PAD_T - 6.0, FACE_IN_I - PAD_T) if sgn > 0 else (-(FACE_IN_I - PAD_T), -(FACE_IN_I - PAD_T - 6.0))
        fl = box(x - 35, x + 35, y0f_, y1f_, z - 35, z + 35)
        for dx_, dz_ in BEAM_BOLTS[n]:
            fl = fl - cy(6.5, 0, y0f_ - 1, y1f_ + 1, x + dx_, z + dz_)        # M12 clearance holes in the flange
        asm[f'{n}_flg{"R" if sgn > 0 else "L"}'] = (fl, 'structure', None)

def vol(s): return s.volume
mass = {}
for n, (s, c, m) in asm.items():
    mass[n] = (m if m is not None else vol(s) * RHO, c)
cat_tot = {}
for n, (m, c) in mass.items(): cat_tot[c] = cat_tot.get(c, 0.0) + m
# Items NOT yet modelled in CAD: carried as explicit, labelled allowances (estimates, not measurements)
ALLOW_KG = {'chain 428 62 links x2 (0.7 kg/m, retailer)': 1.1, 'chain guards x2 (1.5 mm sheet, estimate)': 3.0,
            'motor rails x4 (v2 value 1.11 kg each)': 4.44, 'deck mounts + lift lugs (deck not defined)': 0.0}
for k_, v_ in ALLOW_KG.items(): cat_tot['allowance'] = cat_tot.get('allowance', 0.0) + v_
total = sum(cat_tot.values())

allsolids = Compound([s for s, c, m in asm.values() if c != 'track'])
bb = allsolids.bounding_box()
gates = []
def gate(name, ok, val, lim): gates.append(dict(gate=name, ok=bool(ok), value=val, limit=lim))
tb = asm['track_R'][0].bounding_box()
gate('overall width <= 1190', bb.size.Y <= 1190.0, round(bb.size.Y, 1), 1190.0)
gate('overall height above ground (info)', True, round(bb.max.Z, 1), None)
def xz_gap(c1, r1, c2, r2): return math.hypot(c1[0] - c2[0], c1[1] - c2[1]) - r1 - r2
g_rs = xz_gap((xs, zs), Rtip, (ROLLERS[0], zr), RR)                       # true in-plane gap (not 3D across y)
g_ri = xz_gap((xi, zi), R_in_i, (ROLLERS[-1], zr), RR)
g_ri_ret = xz_gap((xi - 25.0, zi), R_in_i, (ROLLERS[-1], zr), RR)         # idler fully retracted (-25 mm slot travel)
gate('first roller to sprocket tip >=25 (XZ)', g_rs >= 25.0, round(g_rs, 1), 25.0)
gate('last roller to idler >=25 (XZ)', g_ri >= 25.0, round(g_ri, 1), 25.0)
gate('last roller to idler, idler retracted 25 mm >=5', g_ri_ret >= 5.0, round(g_ri_ret, 1), 5.0)
horn_tip_r = R_in_s - 25.0                                                # horn height C=25 above belt inner (PDF)
gate('hub/collar clear of horn tips (r hub+5)', horn_tip_r >= 38.0 + 5.0, round(horn_tip_r, 1), 43.0)
gate('drum gap vs horn base 62 (per side) in 1.5..5', 1.5 <= (70.0 - 62.0) / 2 <= 5.0, (70.0 - 62.0) / 2, '1.5..5')
lam = asm['spr_a_R'][0].bounding_box(); lam2 = asm['spr_b_R'][0].bounding_box()
play = (24.0 - (lam2.max.Y - lam.min.Y)) / 2                              # from actual laminate thickness
gate('sprocket gorge play vs IGB 24 (per side) in 1.5..5', 1.5 <= play <= 5.0, round(play, 2), '1.5..5')
# spool clamp: stack between the two plate faces must equal the sum of its measured parts
def zlen(n): b = asm[n][0].bounding_box(); return b.max.Y - b.min.Y
stack = zlen('rol0_spc_end_i_R') + zlen('rol0_brg_i_R') + zlen('rol0_spc_mid_R') + zlen('rol0_brg_o_R') + zlen('rol0_spc_end_o_R')
gate('spool stack closes to plate faces (194)', abs(stack - (FACE_OUT_I - FACE_IN_O)) < 0.01, round(stack, 3), round(FACE_OUT_I - FACE_IN_O, 3))
for tg in ('rol0', 'idl'):
    sh = asm[f'{tg}_shaft_R'][0].bounding_box(); nu = asm[f'{tg}_nut_i_R'][0].bounding_box(); wi = asm[f'{tg}_wsh_i_R'][0].bounding_box()
    seat_face = FACE_IN_I if tg != 'idl' else FACE_IN_I - 30.0      # idler washer bears on the tension block
    gate(f'{tg} nut seats on washer, washer on bearing face (no float)', abs(nu.max.Y - wi.min.Y) < 0.01 and abs(wi.max.Y - seat_face) < 0.01,
         [round(nu.max.Y, 2), round(wi.min.Y, 2), round(wi.max.Y, 2)], f'washer face {seat_face}')
axle = asm['axle_R'][0].bounding_box()
gate('axle engagement in inner UCFL >=90% of width', (FACE_IN_I - axle.min.Y) >= 0.9 * U['A0_total_mm'] and axle.max.Y >= FACE_IN_I, round(FACE_IN_I - axle.min.Y, 1), round(0.9 * U['A0_total_mm'], 1))
eng_out = axle.max.Y - FACE_OUT_O          # axle length inside the outer UCFL (width 51.2)
gate('axle engagement in outer UCFL >=90% of width', eng_out >= 0.9 * U['A0_total_mm'], round(eng_out, 1), round(0.9 * U['A0_total_mm'], 1))
gate('chain %d whole links at C=%.1f' % (CH_LINKS, CH_C), abs(chain_links(CH_C) - CH_LINKS) < 0.01, round(chain_links(CH_C), 3), CH_LINKS)
def mind(a, b): return asm[a][0].distance_to(asm[b][0])
bolt_names = [n for n in asm if n.startswith('beam_') and '_bolt' in n and n.endswith('_R')]
d_bolt_belt = min(mind(n, 'track_R') for n in bolt_names)
gate('beam bolt tips clear of belt >=4 (no nuts on track side)', d_bolt_belt >= 4.0, round(d_bolt_belt, 1), 4.0)
d_rod = mind('tens_rod_i_R', 'beam_front_flgR')
gate('tension rod clear of front beam flange >=5', d_rod >= 5.0, round(d_rod, 1), 5.0)
kb_ = asm['key0_R'][0].bounding_box(); bo_ = asm['cw_flange_R'][0].bounding_box(); bo2_ = asm['chainwheel_boss_R'][0].bounding_box()
eng_ = min(kb_.max.Y, bo2_.max.Y) - max(kb_.min.Y, bo_.min.Y)      # key length inside flange + boss
gate('chain-wheel key engages flange+boss >=30 mm', eng_ >= 30.0, round(eng_, 1), 30.0)
cwz_ = asm['chainwheel_R'][0].bounding_box().min.Z
gate('chain wheel bottom not below the plate bottom edge (z>=25; plates z=30)', cwz_ >= 25.0, round(cwz_, 1), 25.0)
gate('chain wheel clears the rear cross-beam (>=20 mm)', (BEAM_POS['beam_rear'][0] - 20.0) - (xs + _PDw / 2 + 4.0) >= 20.0, round((BEAM_POS['beam_rear'][0] - 20.0) - (xs + _PDw / 2 + 4.0), 1), 20.0)
gate('idler hub inside horn-tip radius (r32.5 < 84.5-10)', 32.5 < (R_in_i - 25.0) - 10.0, 32.5, round(R_in_i - 35.0, 1))
gate('track bottom at ground', abs(asm['track_R'][0].bounding_box().min.Z) < 0.5, round(asm['track_R'][0].bounding_box().min.Z, 2), 0.0)
# pairwise interference with allow-list (touching ok; overlap > 0.5 cm3 flagged)
names = [n for n in asm if not n.startswith('track')]
bbs = {n: asm[n][0].bounding_box() for n in names}
hits = []
for a, b_ in itertools.combinations(names, 2):
    A, B_ = bbs[a], bbs[b_]
    if A.max.X < B_.min.X or B_.max.X < A.min.X or A.max.Y < B_.min.Y or B_.max.Y < A.min.Y or A.max.Z < B_.min.Z or B_.max.Z < A.min.Z:
        continue
    try: v = (asm[a][0] & asm[b_][0]).volume
    except Exception as e: v = 1e9; print('boolean failed (treated as overlap):', a, b_)
    # allow-list: threaded shaft end inside its nut/washer bore (thread not modelled) is an intended fit
    fasten = lambda n: ('nut' in n or 'wsh' in n)
    thread = lambda n: ('shaft' in n or 'rod' in n or 'bolt' in n)
    if (fasten(a) and thread(b_)) or (fasten(b_) and thread(a)):
        continue      # threaded engagement, thread not modelled (intended)
    if v > 20.0:
        hits.append((a, b_, round(v / 1000.0, 2)))
gate('no solid interference (>20 mm3)', len(hits) == 0, len(hits), 0)

out = dict(drive=dict(pcd_mm=PCD_CW, pinion_T=PIN_N, wheel_T=CW_N, ratio=CW_N / PIN_N, chain_links=CH_LINKS, chain_C_mm=CH_C, motor_mass_kg=CAT['motor_bm1418zxf']['mass_kg_used']),
           allowances_kg=ALLOW_KG, layout=dict(Rp=Rp, C=C, xs=xs, xi=xi, zs=zs, zi=zi, zr=zr, rollers=ROLLERS, R_in_i=R_in_i, YC=YC,
                       plate_y=[FACE_IN_I, FACE_IN_O, FACE_OUT_I, FACE_OUT_O], overall_bbox=[round(v, 1) for v in (bb.size.X, bb.size.Y, bb.size.Z)]),
           mass_kg=dict(total=round(total, 2), by_category={k: round(v, 2) for k, v in cat_tot.items()}),
           gates=gates, interference=hits[:60],
           parts={n: dict(cat=c, mass_kg=round(m, 3)) for n, (m, c) in mass.items()})
json.dump(out, open(os.path.join(HERE, 'uc_v4.json'), 'w'), indent=1)
export_step(Compound([s for s, c, m in asm.values()]), os.path.join(HERE, 'uc_v4_assembly.step'))
print('total kg', out['mass_kg']); print('bbox', out['layout']['overall_bbox'])
for g in gates: print(('PASS' if g['ok'] else 'FAIL'), g['gate'], g['value'])
print('interference hits:', len(hits)); [print('  ', h) for h in hits[:25]]

# ---------------- laser DXF export (right-side copy of each plate part) ----------------
import csv
from collections import Counter
dxf_dir = os.path.join(HERE, 'dxf'); os.makedirs(dxf_dir, exist_ok=True)
LASER = ['plate_in_R', 'plate_out_R', 'spr_a_R', 'rol0_back_i_R', 'idl_back_i_R', 'rol0_seat_i_R', 'chainwheel_R', 'pinion_R',
         'beam_rear_flgR', 'cw_flange_R', 'tens_lug_i_R']
dxf_done = []
for n in LASER:
    shp = asm[n][0]
    ax_, pl_ = (Axis.X, Plane.YZ) if n.startswith('tens_lug') else (Axis.Y, Plane.XZ)
    fs = shp.faces().filter_by(ax_)
    f = max(fs, key=lambda q: q.area)
    exp = ExportDXF(unit=Unit.MM); exp.add_layer('CUT')
    for w in [f.outer_wire()] + list(f.inner_wires()):
        exp.add_shape(pl_.to_local_coords(w), layer='CUT')
    exp.write(os.path.join(dxf_dir, n.replace('_R', '') + '.dxf')); dxf_done.append(n)
print('DXF written:', len(dxf_done), 'files in', dxf_dir)

# ---------------- BOM (count by base name; mirror pairs and R/L counted separately) ----------------
base = Counter(); mass_by = {}
for n, (m, c) in mass.items():
    b = n.rsplit('_', 1)[0] if n.endswith(('_R', '_L')) else n
    base[b] += 1; mass_by[b] = (m, c)
with open(os.path.join(HERE, 'uc_v4_bom.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['item', 'category', 'qty_total', 'mass_each_kg', 'mass_total_kg'])
    for b in sorted(base): w.writerow([b, mass_by[b][1], base[b], round(mass_by[b][0], 3), round(mass_by[b][0] * base[b], 3)])
print('BOM lines:', len(base), '| total with allowances', round(total, 2), 'kg')

# ---------------- single-part STEP exports for FEM ----------------
pdir = os.path.join(HERE, 'parts'); os.makedirs(pdir, exist_ok=True)
for n in ('plate_in_R', 'plate_out_R', 'beam_rear', 'spc0_tube_R', 'axle_R'):
    export_step(asm[n][0], os.path.join(pdir, n + '.step'))
json.dump(dict(rollers=ROLLERS, zr=zr, xs=xs, zs=zs, xi=xi, zi=zi, ucfl_J=U['J_bolt_spacing_mm'], spc_x=list(SPC_X), spc_z=SPC_Z,
               beam_pos={k: list(v) for k, v in BEAM_POS.items()}), open(os.path.join(pdir, 'fem_inputs.json'), 'w'), indent=1)
print('FEM part STEPs written')

# ---------------- category STEPs for colour previews ----------------
pv = os.path.join(HERE, 'preview'); os.makedirs(pv, exist_ok=True)
for catg in ('structure', 'running', 'drive', 'track'):
    sols = [s for n, (s, c, m) in asm.items() if c == catg]
    export_step(Compound(sols), os.path.join(pv, f'cat_{catg}.step'))
print('preview STEPs written')

# ---------------- pads for FEM (restrain the 70x70 pad faces instead of tiny bores) ----------------
export_step(Compound([asm[f'{n}_pad_R'][0] for n in BEAM_POS]), os.path.join(pdir, 'pads_R.step'))
print('pads STEP written')
