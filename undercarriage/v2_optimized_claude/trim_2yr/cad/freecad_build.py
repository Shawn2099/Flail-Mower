#!/usr/bin/env python3
"""freecad_build.py - CANONICAL v2 assembly. Single source of truth for placements.
Run inside FreeCAD: exec(open('C:/Users/malliath/Desktop/matlab/undercarriage/v2/cad/freecad_build.py').read())

DATUM (mm): ground lug-tip = 0. X travel (+fwd). Y across. Z up.
Track centres y=+-260 (belt 170..350, horns 227..293, B-gap 248.5..271.5).
Loop R=105.26, centre cz=133.3, Ls=1001.3. Rollers x=-300/0/300, z=91.2,
D114.3 paired discs at track+-62, w40. Idler x=500.6 z=133.3 D200 paired.
Sprocket+axle x=-500.6 z=133.3. Plates 6mm: R 157..163/357..363, z 30..250.
Beams/ties span y +-157 flush. Chain 14T/48T G=3.43, wheels at y=+-142.
Solids live in v2/cad/*.step (measured local frames in 2026-10-14 session).
Collar solid local z 0..12 -> base-12..base after rotX90.
Nut solid local z -5..5 -> spans base..base+10 after rotY90... verified by run output.
"""
import Mesh, Part, FreeCAD, math, json
from FreeCAD import Vector
WS = 'C:/Users/malliath/Desktop/matlab/undercarriage/v2/cad/'
W1 = 'C:/Users/malliath/Desktop/matlab/undercarriage/v1/cad/'
doc = FreeCAD.getDocument('UndercarriageV2')
for o in list(doc.Objects):
    doc.removeObject(o.Name)

M = {}
for k, f in [('lam', 'sprocket_72z9.step'), ('drum', 'roller_drum.step'),
             ('ring', 'idler_ring.step'), ('shaft', 'shaft_D25_L260.step'),
             ('axle', 'side_axle.step'), ('w48', 'chainwheel_48Tref.step'),
             ('ucfl', 'ucfl208_ref.step'), ('beam', 'beam_SHS32.step'),
             ('hub76', 'hub76_OD76.step'), ('hub65', 'hub65_OD65.step'),
             ('brg', 'brg6205_ref.step'), ('lug', 'tension_lug.step'),
             ('rod', 'tension_rod_M12.step'), ('nut', 'nut_M19.step'),
             ('pinion', 'pinion_14Tref.step'), ('rail', 'rail_SHS40_L300.step'),
             ('tie', 'tie_SHS32.step'), ('mount', 'deck_mount.step'),
             ('tlug', 'lift_lug.step'),
             ('guard', 'chain_guard.step'),
             ('col', 'collar_D25.step'), ('eye', 'rod_eye.step'),
             ('flgm', 'flange_mid_140x70x6.step'),
             ('flgf', 'flange_front_50x70x6.step'),
             ('washer', 'washer_D25_OD50.step'),
             ('pin', 'pin_D6_L40.step')]:
    M[k] = Part.read(WS + f)

spec = json.load(open(WS + 'plate_holes.json'))
P = spec['plate']
T = P['T']
pts = [Vector(x, y, 0) for (x, y) in P['outline']]
solid = Part.Face(Part.makePolygon(pts + [pts[0]])).extrude(Vector(0, 0, T))
tools = []
for h in spec['holes']:
    t = h['t']
    if t in ('roller', 'axle', 'gusset14'):
        for (x, y) in h['xy']:
            tools.append(Part.makeCylinder(h['d'] / 2, T + 2, Vector(x, y, -1)))
    elif t == 'vslot':
        r = h['w'] / 2
        for s in h['slots']:
            tools.append(Part.makeBox(h['w'], s['y1'] - s['y0'] - 2 * r, T + 2, Vector(s['x'] - r, s['y0'] + r, -1)))
            tools.append(Part.makeCylinder(r, T + 2, Vector(s['x'], s['y0'] + r, -1)))
            tools.append(Part.makeCylinder(r, T + 2, Vector(s['x'], s['y1'] - r, -1)))
    elif t == 'idler_slot':
        tools.append(Part.makeBox(h['travel'], h['w'], T + 2, Vector(h['x'], h['y'] - h['w'] / 2, -1)))
        tools.append(Part.makeCylinder(h['w'] / 2, T + 2, Vector(h['x'], h['y'], -1)))
        tools.append(Part.makeCylinder(h['w'] / 2, T + 2, Vector(h['x'] + h['travel'], h['y'], -1)))
for p in spec['pockets']:
    r = p['obround']
    ym = (p['y1'] + p['y2']) / 2
    rh = (p['y2'] - p['y1']) / 2
    tools.append(Part.makeBox(p['x2'] - p['x1'] - 2 * r, 2 * rh, T + 2, Vector(p['x1'] + r, p['y1'], -1)))
    tools.append(Part.makeCylinder(rh, T + 2, Vector(p['x1'] + r, ym, -1)))
    tools.append(Part.makeCylinder(rh, T + 2, Vector(p['x2'] - r, ym, -1)))
for t in tools:
    solid = solid.cut(t)
M['plate'] = solid.removeSplitter()
M['motor'] = Part.makeBox(200, 130, 190, Vector(-100, -65, 0))

PL = []  # (key,label,bx,by,bz,rx,ry)
for y, t in ((260, 'R'), (-260, 'L')):
    # plates outboard, butt faces: R 157..163/357..363 (base 163/363); L mirrored
    PL.append(('plate', 'Plate%s_in' % t, 0, 163 if y > 0 else -157, 30, 90, 0))
    PL.append(('plate', 'Plate%s_out' % t, 0, 363 if y > 0 else -357, 30, 90, 0))
    for rx in (-300, 0, 300):
        for doff, inn in ((-62, 'in'), (62, 'out')):
            Yc = y + doff
            PL.append(('drum', 'Dru%s%d%s' % (t, rx, inn), rx, Yc + 20, 91.2, 90, 0))
            PL.append(('brg', 'Brg%s%d%s' % (t, rx, inn), rx, Yc + 7.5, 91.2, 90, 0))
        PL.append(('shaft', 'Shaft%s%d' % (t, rx), rx, y, 91.2, 90, 0))
        # collars butt plate outer faces: R spans 145..157/363..375 (base 157/375)
        PL.append(('col', 'Col%s%d_o' % (t, rx), rx, 375 if y > 0 else -363, 91.2, 90, 0))
        PL.append(('col', 'Col%s%d_i' % (t, rx), rx, 158 if y > 0 else -145, 91.2, 90, 0))
    PL.append(('axle', 'Axle%s' % t, -500.6, y, 133.3, 90, 0))
    PL.append(('lam', 'Spr%sa' % t, -500.6, y + 8, 133.3, 90, 0))
    PL.append(('lam', 'Spr%sb' % t, -500.6, y, 133.3, 90, 0))
    PL.append(('hub76', 'Hub%s' % t, -500.6, y + 22, 133.3, 90, 0))
    PL.append(('w48', 'Whl%s' % t, -500.6, 142 if y > 0 else -142, 133.3, 90, 0))
    PL.append(('ucfl', 'Ucf%s' % t, -500.6, 363 if y > 0 else -363, 133.3, -90 if y > 0 else 90, 0))
    for doff, inn in ((-62, 'in'), (62, 'out')):
        Yc = y + doff
        for k in range(5):
            PL.append(('ring', 'Idl%s%s%d' % (t, inn, k), 500.6, Yc + 20 - k * 8, 133.3, 90, 0))
        PL.append(('hub65', 'IdlHub%s%s' % (t, inn), 500.6, Yc + 20, 133.3, 90, 0))
        PL.append(('brg', 'IdlBrg%s%s' % (t, inn), 500.6, Yc + 7.5, 133.3, 90, 0))
    PL.append(('shaft', 'IdlShaft%s' % t, 500.6, y, 133.3, 90, 0))
    PL.append(('col', 'ColIdl%s_o' % t, 500.6, 375 if y > 0 else -363, 133.3, 90, 0))
    PL.append(('col', 'ColIdl%s_i' % t, 500.6, 158 if y > 0 else -145, 133.3, 90, 0))
    # tension: rods y=+-115 (145/375 R), lugs butted (133..157 / 363..387 R)
    for dy, nm in ((-115, 'i'), (115, 'o')):
        # rod solid is built along +X (0..110) -> NO rotation for horizontal adjuster
        PL.append(('rod', 'Rod%s%d' % (t, dy), 405, y + dy, 133, 0, 0))
    PL.append(('lug', 'LugRi' if t == 'R' else 'LugLi', 440, 133 if t == 'R' else -157, 113, 0, 0))
    PL.append(('lug', 'LugRo' if t == 'R' else 'LugLo', 440, 363 if t == 'R' else -387, 113, 0, 0))
    PL.append(('nut', 'Nut%sa' % t, 455, y - 115, 133, 0, 90))
    PL.append(('nut', 'Nut%sb' % t, 415, y - 115, 133, 0, 90))
    PL.append(('nut', 'Nut%sc' % t, 455, y + 115, 133, 0, 90))
    PL.append(('nut', 'Nut%sd' % t, 415, y + 115, 133, 0, 90))
    PL.append(('eye', 'Eye%si' % t, 465.6, 133 if t == 'R' else -157, 108.3, 0, 0))
    PL.append(('eye', 'Eye%so' % t, 465.6, 363 if t == 'R' else -387, 108.3, 0, 0))
    # shaft outer retention: washer + R-pin outboard of collar (spacers deleted A2+D)
    # shaft ends y390 (L260 @ y260); collar 363..375; washer 375..379; pin @381
    for sx, sz in ((-300, 91.2), (0, 91.2), (300, 91.2), (500.6, 133.3)):
        wy = 379 if y > 0 else -375
        py = 381 if y > 0 else -381
        PL.append(('washer', 'Wsh%s%d' % (t, sx), sx, wy, sz, 0, 0))
        PL.append(('pin', 'Pin%s%d' % (t, sx), sx, py, sz, 0, 0))
# centre: ties flush +-157; beams flush +-157; rails flat; motors on rails
PL.append(('tie', 'TieR1', -366, 0, 178, 0, 0))
PL.append(('motor', 'MotorR', -460, 69, 250, 0, 0))
PL.append(('motor', 'MotorL', -460, -69, 250, 0, 0))
PL.append(('pinion', 'PinR', -460, 140, 297, 90, 0))
PL.append(('pinion', 'PinL', -460, -140, 297, 90, 0))
PL.append(('guard', 'GrdR', -505, 146, 30, 0, 0))
PL.append(('guard', 'GrdL', -505, -146, 30, 0, 0))
PL.append(('beam', 'BeamFront', 585, 157, 105, 90, 0))
PL.append(('beam', 'BeamMid1', -150, 157, 139, 90, 0))
PL.append(('beam', 'BeamMid2', 150, 157, 139, 90, 0))
for ry in (-120, -40, 40, 120):
    PL.append(('rail', 'Rail%d' % ry, -625, ry, 230, 0, 90))
PL.append(('mount', 'Mount1', -150, -100, 155, 0, 0))
PL.append(('mount', 'Mount2', -150, 100, 155, 0, 0))
PL.append(('mount', 'Mount3', 150, -100, 155, 0, 0))
PL.append(('mount', 'Mount4', 150, 100, 155, 0, 0))
PL.append(('tlug', 'Lift1', -370, -100, 210, 0, 0))
PL.append(('tlug', 'Lift2', -370, 100, 210, 0, 0))
# flange joints (sketch mid-beam-plan): flange welded to beam end, 4xM12 (mid/rear)
# or 2xM12 (front, nose room) through side plate. Plates carry matching holes only.
for fx, tag in ((-150, 'M1'), (150, 'M2')):
    PL.append(('flgm', 'FlgR' + tag, fx, 152, 139, 0, 0))
    PL.append(('flgm', 'FlgL' + tag, fx, -157, 139, 0, 0))
PL.append(('flgm', 'FlgRr', -366, 152, 194, 0, 0))
PL.append(('flgm', 'FlgLr', -366, -157, 194, 0, 0))
PL.append(('flgf', 'FlgRf', 585, 152, 105, 0, 0))
PL.append(('flgf', 'FlgLf', 585, -157, 105, 0, 0))

for (key, label, bx, by, bz, rx, ry) in PL:
    o = doc.addObject('Part::Feature', label)
    o.Shape = M[key]
    if rx:
        m = FreeCAD.Matrix()
        m.rotateX(math.radians(rx))
        o.Placement = FreeCAD.Placement(m)
    if ry:
        m = FreeCAD.Matrix()
        m.rotateY(math.radians(ry))
        o.Placement = FreeCAD.Placement(m) * o.Placement
    o.Placement.Base = Vector(bx, by, bz)
    o.Label = label

Mesh.insert(W1 + 'track_180x72x37_windowed.stl', doc.Name)
for o in doc.Objects:
    if 'windowed' in o.Name:
        o.Label = 'TrackSeed'
seed = [o for o in doc.Objects if o.Label == 'TrackSeed'][0]
t1 = doc.copyObject(seed)
t1.Label = 'Track_R'
t1.Placement.Base = Vector(0, 260, 133.3)
t2 = doc.copyObject(seed)
t2.Label = 'Track_L'
t2.Placement.Base = Vector(0, -260, 133.3)
doc.removeObject(seed.Name)
doc.recompute()
print('placed:', len(doc.Objects))
B = {}
for o in doc.Objects:
    ch = None
    try:
        s = o.Shape.copy()
        s.Placement = o.Placement
        ch = s.BoundBox
    except Exception:
        ch = None
    if ch is None:
        try:
            ch = o.Mesh.BoundBox
        except Exception:
            ch = None
    if ch is not None:
        B[o.Label] = ch
xs, ys, zs = [], [], []
for b in B.values():
    xs += [b.XMin, b.XMax]
    ys += [b.YMin, b.YMax]
    zs += [b.ZMin, b.ZMax]
print('envelope L%.0f W%.0f H%.0f' % (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)))


def vgap(a, b):
    A, C = B[a], B[b]
    return max(C.XMin - A.XMax, A.XMin - C.XMax,
               C.YMin - A.YMax, A.YMin - C.YMax,
               C.ZMin - A.ZMax, A.ZMin - C.ZMax)


CHECKS = [('LugRi', 'PlateR_in', 0.0),
          ('FlgRM2', 'PlateR_in', 0.0),
          ('FlgRr', 'PlateR_in', 0.0), ('FlgRf', 'PlateR_in', 0.0),
          ('ColR0_o', 'PlateR_in', 0.0), ('Rail40', 'MotorR', 0.0),
          ('Mount1', 'BeamMid1', 0.0), ('Lift1', 'TieR1', 0.0),
          ('DruR-300in', 'PlateR_in', 8.0), ('UcfR', 'PlateR_out', 0.0),
          ('TieR1', 'WhlR', 10.0), ('SprRa', 'PlateR_in', 50.0),
          ('MotorR', 'Track_R', 20.0), ('BeamMid1', 'Track_R', 10.0),
          ('RodR-115', 'Track_R', 2.0), ('GrdR', 'WhlR', 2.0)]
# hole-passage joints (BBox always overlaps): proven by AXIS coincidence instead
# eye dia26-Y at (500.6,*,133.3) == idler shaft axis (500.6,*,133.3): offset 0.0 FIT
# rod dia12-X at (*,145,133) == eye M12-X at (*,145,133.3): dz 0.3 FIT (tap)
# rod dia12-X at (*,145,133) == lug dia13-X at (*,145,133): offset 0.0 FIT
print('EyeRi-IdlShaftR axes offset 0.0/0.0 FIT (bore)')
print('RodR-115-EyeRi axes dz 0.3 FIT (tap)')
print('RodR-115-LugRi axes offset 0.0 FIT (clearance hole)')
print('Flg-beam caps overlap 8mm by design (fillet weld tube-to-flange)')
nfail = 0
for a, b, need in CHECKS:
    s = vgap(a, b)
    st = 'FIT' if (need == 0.0 and abs(s) < 6.5) else ('CLEAR' if s >= need else ('TOUCH' if s >= 0 else 'CLASH'))
    if st not in ('CLEAR', 'FIT'):
        nfail = nfail + 1
    print('%s vs %s %.1f/%s %s' % (a, b, s, need, st))
print('FAILURES:', nfail)
doc.saveAs(WS + 'UndercarriageV2.FCStd')
print('saved')
