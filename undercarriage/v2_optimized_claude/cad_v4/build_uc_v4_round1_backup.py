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
from bd_warehouse.fastener import HexNut, PlainWasher

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
def plate(yc):
    with BuildPart() as p:
        with BuildSketch(Plane.XZ):
            Polygon(*PTS, align=None)
            for x in ROLLERS:
                with Locations((x, zr)): Circle(13.0, mode=Mode.SUBTRACT)
            with Locations((xs, zs)): Circle(22.5, mode=Mode.SUBTRACT)
            for dz in (-U['J_bolt_spacing_mm'] / 2, U['J_bolt_spacing_mm'] / 2):
                with Locations((xs, zs + dz)): Circle(U['N_bolt_hole_mm'] / 2, mode=Mode.SUBTRACT)
            with Locations((xi + 5, zi)): SlotOverall(85.5, 25.5, mode=Mode.SUBTRACT)
            for sx in SPC_X:
                with Locations((sx, SPC_Z)): Circle(8.5, mode=Mode.SUBTRACT)
            with Locations((-100, zr + 10)): RectangleRounded(130, 65, 10, mode=Mode.SUBTRACT)  # between roller holes
            with Locations((100, zr + 10)): RectangleRounded(130, 65, 10, mode=Mode.SUBTRACT)
        extrude(amount=TPL)
    return Pos(0, yc + TPL / 2, 0) * p.part
add('plate_in', plate(Y_PIN), 'structure'); add('plate_out', plate(Y_POUT), 'structure')

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
add('axle', cy(20.0, 0, 245.0, FACE_OUT_O + U['A0_total_mm'] - 1.0, xs, zs), 'drive')   # ends 1 mm inside outer UCFL face
add('collar_a', cy(30.0, 20.0, 396.0, 408.0, xs, zs), 'drive'); add('collar_b', cy(30.0, 20.0, 452.0, 464.0, xs, zs), 'drive')
add('hub', cy(38.0, 20.0, 408.0, 452.0, xs, zs), 'drive')

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
CW_T, CW_N, PIN_N = 43, 43, 14
cw = Sprocket(num_teeth=CW_N, chain_pitch=12.7, roller_diameter=8.51, thickness=6.0)
cw = cw - Cylinder(20, 10)
add('chainwheel', Pos(xs, 253.0, zs) * Rot(X=90) * cw, 'drive')
add('chainwheel_boss', cy(30.0, 20.0, 256.0, FACE_IN_I - U['A0_total_mm'] - 2.0, xs, zs), 'drive')
def chain_links(Cc, z1=14, z2=43, p=12.7): return 2 * Cc / p + (z1 + z2) / 2 + ((z2 - z1) / (2 * math.pi)) ** 2 * p / Cc
lo_, hi_ = 120.0, 260.0
for _ in range(60):
    mid_ = (lo_ + hi_) / 2
    if chain_links(mid_) < 58: lo_ = mid_
    else: hi_ = mid_
CH_C = (lo_ + hi_) / 2                                  # centre distance for exactly 58 links
add('motor_ph', cy(50.0, 0, 90.0, 235.0, xs, zs + CH_C), 'drive', CAT['motor_placeholder']['mass_kg'])
add('motor_shaft_ph', cy(10.0, 0, 235.0, 262.0, xs, zs + CH_C), 'drive')
pin = Sprocket(num_teeth=PIN_N, chain_pitch=12.7, roller_diameter=8.51, thickness=6.0)
add('pinion', Pos(xs, 253.0, zs + CH_C) * Rot(X=90) * (pin - Cylinder(10, 10)), 'drive')

# ---------------- spools: roller drums (3 stations) and idler drums ----------------
def spool_set(tag, xc, zc, Ro, wall, with_shaft_ends=True):
    """one station: two drums (pipe+backplate+seat ring+6205), spacers, circlips. Right side."""
    Ri = Ro - wall
    for side, mirror in (('i', 1), ('o', -1)):
        def Y(y): return y if mirror == 1 else 2 * YC - y      # mirror about track centre
        def span(a, b):
            lo, hi = sorted((Y(a), Y(b))); return lo, hi
        lo, hi = span(355.0, 395.0);   add(f'{tag}_pipe_{side}', cy(Ro, Ri, lo, hi, xc, zc), 'running')
        lo, hi = span(355.0, 361.0);   add(f'{tag}_back_{side}', cy(Ri, 23.0, lo, hi, xc, zc), 'running')
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
    add(f'{tag}_shaft', cy(12.5, 0, 329.0, 531.0, xc, zc) + cy(12.0, 0, 296.0, 329.0, xc, zc) + cy(12.0, 0, 531.0, 564.0, xc, zc), 'running')
    for y_wash, y_nut, sgn in ((322.7, 301.2, 1), (533.0, 537.3, -1)):
        pass
    nut = HexNut(size='M24-3', fastener_type='iso4032'); wsh = PlainWasher(size='M24', fastener_type='iso7089')
    nb = nut.bounding_box().size.Z; wb = wsh.bounding_box().size.Z
    # bd_warehouse parts extend along +Z from the origin; Rot(X=+90) sends +Z to -Y, Rot(X=-90) to +Y.
    for side, (yw0, yn0, rx) in (('i', (FACE_IN_I, FACE_IN_I - wb, 90)), ('o', (FACE_OUT_O, FACE_OUT_O + wb, -90))):
        add(f'{tag}_wsh_{side}', Pos(xc, yw0, zc) * Rot(X=rx) * wsh, 'running')
        add(f'{tag}_nut_{side}', Pos(xc, yn0, zc) * Rot(X=rx) * nut, 'running')
for k, x in enumerate(ROLLERS): spool_set(f'rol{k}', x, zr, RR, CAT['pipe_4NB_roller']['wall_mm'])
spool_set('idl', xi, zi, R_in_i, T_ID)   # idler shaft shares the same stack (shaft ends/tensioner added round 2)

# ---------------- through-spacer tubes: tie inner and outer plate together (review defect 2) ----------------
nut16 = HexNut(size='M16-2', fastener_type='iso4032'); wsh16 = PlainWasher(size='M16', fastener_type='iso7089')
nb16, wb16 = nut16.bounding_box().size.Z, wsh16.bounding_box().size.Z
for k, sx in enumerate(SPC_X):
    add(f'spc{k}_tube', cy(21.2, 18.0, FACE_IN_O, FACE_OUT_I, sx, SPC_Z), 'structure')
    add(f'spc{k}_rod', cy(8.0, 0, 305.0, 555.0, sx, SPC_Z), 'structure')
    for side, (yw0, yn0, rx) in (('i', (FACE_IN_I, FACE_IN_I - wb16, 90)), ('o', (FACE_OUT_O, FACE_OUT_O + wb16, -90))):
        add(f'spc{k}_wsh_{side}', Pos(sx, yw0, SPC_Z) * Rot(X=rx) * wsh16, 'structure')
        add(f'spc{k}_nut_{side}', Pos(sx, yn0, SPC_Z) * Rot(X=rx) * nut16, 'structure')

# ---------------- cross beams ----------------
SHS, SW = CAT['shs40']['od_mm'], CAT['shs40']['wall_mm']
BL = 2 * FACE_IN_I - 2 * 6.0
def beam(x, z):
    t = Pos(x, 0, z) * (Box(SHS, BL, SHS) - Box(SHS - 2 * SW, BL + 2, SHS - 2 * SW))
    return t
BEAMS = [('beam_rear', -230.0, 175.0), ('beam_mid1', -100.0, 175.0), ('beam_mid2', 100.0, 175.0), ('beam_front', 495.0, 110.0)]
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
        fl = box(x - 35, x + 35, 321.0 * sgn if sgn > 0 else -327.0, 327.0 * sgn if sgn > 0 else -321.0, z - 35, z + 35)
        asm[f'{n}_flg{"R" if sgn > 0 else "L"}'] = (fl, 'structure', None)

def vol(s): return s.volume
mass = {}
for n, (s, c, m) in asm.items():
    mass[n] = (m if m is not None else vol(s) * RHO, c)
cat_tot = {}
for n, (m, c) in mass.items(): cat_tot[c] = cat_tot.get(c, 0.0) + m
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
    gate(f'{tg} nut seats on washer, washer on plate (no float)', abs(nu.max.Y - wi.min.Y) < 0.01 and abs(wi.max.Y - FACE_IN_I) < 0.01,
         [round(nu.max.Y, 2), round(wi.min.Y, 2)], 'equal')
axle = asm['axle_R'][0].bounding_box()
gate('axle engagement in inner UCFL >=90% of width', (FACE_IN_I - axle.min.Y) >= 0.9 * U['A0_total_mm'] and axle.max.Y >= FACE_IN_I, round(FACE_IN_I - axle.min.Y, 1), round(0.9 * U['A0_total_mm'], 1))
eng_out = axle.max.Y - FACE_OUT_O          # axle length inside the outer UCFL (width 51.2)
gate('axle engagement in outer UCFL >=90% of width', eng_out >= 0.9 * U['A0_total_mm'], round(eng_out, 1), round(0.9 * U['A0_total_mm'], 1))
gate('chain 58 whole links at C=%.1f' % CH_C, abs(chain_links(CH_C) - 58.0) < 0.01, round(chain_links(CH_C), 3), 58)
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
    if (('_nut_' in a or '_nut_' in b_ or '_wsh_' in a or '_wsh_' in b_) and ('shaft' in a or 'shaft' in b_ or 'rod' in a or 'rod' in b_)):
        continue
    if v > 500.0:
        hits.append((a, b_, round(v / 1000.0, 2)))
gate('no solid interference (>0.5 cm3)', len(hits) == 0, len(hits), 0)

out = dict(layout=dict(Rp=Rp, C=C, xs=xs, xi=xi, zs=zs, zi=zi, zr=zr, rollers=ROLLERS, R_in_i=R_in_i, YC=YC,
                       plate_y=[FACE_IN_I, FACE_IN_O, FACE_OUT_I, FACE_OUT_O], overall_bbox=[round(v, 1) for v in (bb.size.X, bb.size.Y, bb.size.Z)]),
           mass_kg=dict(total=round(total, 2), by_category={k: round(v, 2) for k, v in cat_tot.items()}),
           gates=gates, interference=hits[:60],
           parts={n: dict(cat=c, mass_kg=round(m, 3)) for n, (m, c) in mass.items()})
json.dump(out, open(os.path.join(HERE, 'uc_v4.json'), 'w'), indent=1)
export_step(Compound([s for s, c, m in asm.values()]), os.path.join(HERE, 'uc_v4_assembly.step'))
print('total kg', out['mass_kg']); print('bbox', out['layout']['overall_bbox'])
for g in gates: print(('PASS' if g['ok'] else 'FAIL'), g['gate'], g['value'])
print('interference hits:', len(hits)); [print('  ', h) for h in hits[:25]]
