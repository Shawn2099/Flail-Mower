#!/usr/bin/env python3
"""freecad_build_v3u.py - V3 folded-U concept: V2 plates as channel legs + roof.
Legs reuse side_plate.step (V2 holes/slots untouched). Roof plain 6mm box.
Idler: carrier block between legs + front gate + M12 screw (telescopic).
Run: exec(open('C:/Users/malliath/Desktop/matlab/undercarriage/v3/cad/freecad_build_v3u.py').read())
"""
import Part, FreeCAD, math
from FreeCAD import Vector
V2 = 'C:/Users/malliath/Desktop/matlab/undercarriage/v2/cad/'
try:
    doc = FreeCAD.getDocument('UndercarriageV3U')
    for o in list(doc.Objects):
        doc.removeObject(o.Name)
except Exception:
    doc = FreeCAD.newDocument('UndercarriageV3U')

M = {}
for k, f in [('leg','side_plate.step'),('drum','roller_drum.step'),
              ('ring','idler_ring.step'),('shaft','shaft_D25_L260.step'),
              ('axle','side_axle.step'),('lam','sprocket_72z9.step'),
              ('hub76','hub76_OD76.step'),('hub65','hub65_OD65.step'),
              ('brg','brg6205_ref.step'),('ucfl','ucfl208_ref.step'),
              ('w48','chainwheel_48Tref.step'),('col','collar_D25.step'),
              ('flgf','flange_front_50x70x8.step'),
              ('washer','washer_D25_OD50.step'),('pin','pin_D6_L40.step')]:
    M[k] = Part.read(V2 + f)

# roof: spans outer faces, full plate length x -620..620, 6 thick on z 250..256
M['roof'] = Part.makeBox(1240, 206, 6, Vector(-620, 0, 0))
# idler carrier: block between legs holding shaft, 80 long x 194 wide x 60 tall
M['carrier'] = Part.makeBox(80, 194, 60, Vector(0, -97, -30))
# front gate across mouth + screw + nut
M['gate'] = Part.makeBox(6, 206, 80, Vector(0, -103, -40))
M['screw'] = Part.makeCylinder(6, 120, Vector(0, 0, 0))
M['nut'] = Part.makeBox(19, 19, 16, Vector(-9.5, -9.5, 0))
M['beam40'] = Part.makeBox(40, 440, 40, Vector(-20, -220, -20))

PL = []
for y, t in ((260, 'R'), (-260, 'L')):
    yIn = 163 if y > 0 else -157   # leg inner base (V2 numbers)
    yOut = 363 if y > 0 else -357  # leg outer base
    yRoof = 157 if y > 0 else -363 # roof spans inner..outer faces
    PL.append(('leg', 'Leg%s_in' % t, 0, yIn, 30, 90, 0))
    PL.append(('leg', 'Leg%s_out' % t, 0, yOut, 30, 90, 0))
    PL.append(('roof', 'Roof%s' % t, 0, yRoof, 250, 0, 0))
    for rx in (-300, 0, 300):
        for doff, inn in ((-62, 'in'), (62, 'out')):
            Yc = y + doff
            PL.append(('drum', 'Dru%s%d%s' % (t, rx, inn), rx, Yc + 20, 91.2, 90, 0))
            PL.append(('brg', 'Brg%s%d%s' % (t, rx, inn), rx, Yc + 7.5, 91.2, 90, 0))
        PL.append(('shaft', 'Shaft%s%d' % (t, rx), rx, y, 91.2, 90, 0))
        PL.append(('col', 'Col%s%d_o' % (t, rx), rx, 375 if y > 0 else -363, 91.2, 90, 0))
        PL.append(('col', 'Col%s%d_i' % (t, rx), rx, 157 if y > 0 else -145, 91.2, 90, 0))
    # idler pair + shaft (rides in leg slots, carried by block)
    for doff, inn in ((-62, 'in'), (62, 'out')):
        Yc = y + doff
        for k in range(5):
            PL.append(('ring', 'Idl%s%s%d' % (t, inn, k), 500.6, Yc + 20 - k * 8, 133.3, 90, 0))
        PL.append(('hub65', 'IdlHub%s%s' % (t, inn), 500.6, Yc + 20, 133.3, 90, 0))
        PL.append(('brg', 'IdlBrg%s%s' % (t, inn), 500.6, Yc + 7.5, 133.3, 90, 0))
    PL.append(('shaft', 'IdlShaft%s' % t, 500.6, y, 133.3, 90, 0))
    PL.append(('carrier', 'Carrier%s' % t, 460, y, 133.3, 0, 0))
    PL.append(('gate', 'Gate%s' % t, 600, y, 133.3, 0, 0))
    PL.append(('screw', 'Screw%s' % t, 500, y, 133.3, 0, -90))
    PL.append(('nut', 'Nut%s' % t, 609, y, 133.3, 0, 0))
    # rear axle + sprocket + UCFL (V2 numbers)
    PL.append(('axle', 'Axle%s' % t, -500.6, y, 133.3, 90, 0))
    PL.append(('lam', 'Spr%sa' % t, -500.6, y + 8, 133.3, 90, 0))
    PL.append(('lam', 'Spr%sb' % t, -500.6, y, 133.3, 90, 0))
    PL.append(('hub76', 'Hub%s' % t, -500.6, y + 22, 133.3, 90, 0))
    PL.append(('w48', 'Whl%s' % t, -500.6, 142 if y > 0 else -142, 133.3, 90, 0))
    PL.append(('ucfl', 'Ucf%s' % t, -500.6, 363 if y > 0 else -363, 133.3, -90 if y > 0 else 90, 0))
    for sx, sz in ((-300, 91.2), (0, 91.2), (300, 91.2), (500.6, 133.3)):
        PL.append(('washer', 'Wsh%s%d' % (t, sx), sx, 379 if y > 0 else -375, sz, 0, 0))
        PL.append(('pin', 'Pin%s%d' % (t, sx), sx, 381 if y > 0 else -381, sz, 0, 0))
# cross beams between inner legs (span y -157..157 -> L314) with end flanges
M['tie314'] = Part.makeBox(40, 314, 40, Vector(-20, -157, -20))
for bx, bz in ((-150, 135), (150, 135), (-366, 190)):
    PL.append(('tie314', 'Beam%d' % bx, bx, 0, bz, 0, 0))
    PL.append(('flgf', 'FlgR%d' % bx, bx, 149, bz, 0, 0))
    PL.append(('flgf', 'FlgL%d' % bx, bx, -157, bz, 0, 0))

for (key, label, bx, by, bz, rx, ry) in PL:
    o = doc.addObject('Part::Feature', label)
    o.Shape = M[key]
    m = FreeCAD.Matrix()
    if rx:
        m.rotateX(math.radians(rx))
    if ry:
        m.rotateY(math.radians(ry))
    m.move(Vector(bx, by, bz))
    o.Placement = FreeCAD.Placement(m)

doc.recompute()
print('placed: %d' % len(PL))
print('saved')
doc.saveAs('C:/Users/malliath/Desktop/matlab/undercarriage/v3/cad/UndercarriageV3U.FCStd')
