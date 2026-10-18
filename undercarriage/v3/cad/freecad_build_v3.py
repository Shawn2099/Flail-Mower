#!/usr/bin/env python3
"""freecad_build_v3.py - V3 S1 concept model with telescopic idler.
Datum copied EXACTLY from v2: ground lug-tip 0, X travel, Y across, Z up.
Track centres y=+-260. Rollers x=-300/0/300 z=91.2, idler x=500.6 z=133.3,
axle x=-500.6 z=133.3. Spine SHS80x5 centre z=112 (covers 91+133).
Run inside FreeCAD: exec(open('C:/Users/malliath/Desktop/matlab/undercarriage/v3/cad/freecad_build_v3.py').read())
"""
import Part, FreeCAD, math
from FreeCAD import Vector
V2 = 'C:/Users/malliath/Desktop/matlab/undercarriage/v2/cad/'
try:
    doc = FreeCAD.getDocument('UndercarriageV3')
    for o in list(doc.Objects):
        doc.removeObject(o.Name)
except Exception:
    doc = FreeCAD.newDocument('UndercarriageV3')

M = {}
for k, f in [('drum','roller_drum.step'),('ring','idler_ring.step'),
              ('shaft','shaft_D25_L260.step'),('axle','side_axle.step'),
              ('lam','sprocket_72z9.step'),('hub76','hub76_OD76.step'),
              ('brg','brg6205_ref.step'),('ucfl','ucfl208_ref.step'),
              ('w48','chainwheel_48Tref.step'),('col','collar_D25.step'),
              ('flgf','flange_front_50x70x8.step'),
              ('washer','washer_D25_OD50.step'),('pin','pin_D6_L40.step')]:
    M[k] = Part.read(V2 + f)

def shs(B, t, L):
    b = B - 2*t
    outer = Part.makeBox(L, B, B, Vector(0, -B/2, -B/2))
    inner = Part.makeBox(L-0.001, b, b, Vector(0.0005, -b/2, -b/2))
    return outer.cut(inner).removeSplitter()

M['spine'] = shs(80, 5, 1000)     # x 0..1000 local, centred section
M['slider'] = shs(60, 5, 260)     # telescopic inner
M['beam40'] = shs(40, 3.2, 440)   # cross beams between spines
M['boss'] = Part.makeCylinder(19, 8, Vector(0,0,0)).cut(
    Part.makeCylinder(13, 10, Vector(0,0,-1))).removeSplitter()
M['endplate'] = Part.makeBox(8, 96, 96, Vector(0, -48, -48))
M['screw'] = Part.makeCylinder(6, 200, Vector(0,0,0))
M['nut'] = Part.makeBox(19, 19, 16, Vector(-9.5, -9.5, 0))

PL = []  # (key,label,bx,by,bz,rx,ry,rz)
for y, t in ((260,'R'), (-260,'L')):
    # spine x -560..440 (local 0..1000 -> base -560), centre z=112
    PL.append(('spine','Spine%s'%t, -560, y, 112, 0, 0, 0))
    # boss rings both walls at 3 roller stations (walls y+-40 rel centre)
    for rx in (-300, 0, 300):
        PL.append(('boss','Boss%s%d_a'%(t,rx), rx, y+40, 91.2, 90, 0, 0))
        PL.append(('boss','Boss%s%d_b'%(t,rx), rx, y-40, 91.2, 90, 0, 0))
    # running gear — same numbers as v2
    for rx in (-300, 0, 300):
        for doff, inn in ((-62,'in'),(62,'out')):
            Yc = y + doff
            PL.append(('drum','Dru%s%d%s'%(t,rx,inn), rx, Yc+20, 91.2, 90, 0, 0))
            PL.append(('brg','Brg%s%d%s'%(t,rx,inn), rx, Yc+7.5, 91.2, 90, 0, 0))
        PL.append(('shaft','Shaft%s%d'%(t,rx), rx, y, 91.2, 90, 0, 0))
        PL.append(('col','Col%s%do'%(t,rx), rx, y+103 if y>0 else y-115, 91.2, 90, 0, 0))
        PL.append(('washer','Wsh%s%d'%(t,rx), rx, y+119 if y>0 else y-115, 91.2, 0, 0, 0))
        PL.append(('pin','Pin%s%d'%(t,rx), rx, y+121 if y>0 else y-121, 91.2, 0, 0, 0))
    # telescopic idler: slider x 380..640, idler shaft at 500.6 rides in slider
    PL.append(('slider','Slider%s'%t, 380, y, 133.3, 0, 0, 0))
    PL.append(('endplate',' alberta%s'%t, 440, y, 133.3, 0, 0, 0))
    PL.append(('screw','Screw%s'%t, 440, y, 133.3, 0, -90, 0))
    PL.append(('nut','Nut%s'%t, 448, y, 133.3, 0, 0, 0))
    for doff, inn in ((-62,'in'),(62,'out')):
        Yc = y + doff
        for k in range(5):
            PL.append(('ring','Idl%s%s%d'%(t,inn,k), 500.6, Yc+20-k*8, 133.3, 90, 0, 0))
        PL.append(('brg','IdlBrg%s%s'%(t,inn), 500.6, Yc+7.5, 133.3, 90, 0, 0))
    PL.append(('shaft','IdlShaft%s'%t, 500.6, y, 133.3, 90, 0, 0))
    # rear axle + sprocket (v2 numbers) + end plate on spine rear mouth
    PL.append(('endplate','AxPlate%s'%t, -568, y, 133.3, 0, 0, 0))
    PL.append(('axle','Axle%s'%t, -500.6, y, 133.3, 90, 0, 0))
    PL.append(('lam','Spr%sa'%t, -500.6, y+8, 133.3, 90, 0, 0))
    PL.append(('lam','Spr%sb'%t, -500.6, y, 133.3, 90, 0, 0))
    PL.append(('hub76','Hub%s'%t, -500.6, y+22, 133.3, 90, 0, 0))
    PL.append(('w48','Whl%s'%t, -500.6, 142 if y>0 else -142, 133.3, 90, 0, 0))
    PL.append(('ucfl','Ucf%s'%t, -500.6, y+103 if y>0 else y-103, 133.3, -90 if y>0 else 90, 0, 0))
# cross beams + flanges (middle like v2, bolted to spine inner walls)
for bx in (-150, 150):
    PL.append(('beam40','Beam%d'%bx, bx, 0, 135, 0, 0, 90))
    PL.append(('flgf','FlgR%d'%bx, bx, 212, 135, 0, 0, 0))
    PL.append(('flgf','FlgL%d'%bx, bx, -228, 135, 0, 0, 0))
PL.append(('beam40','TieRear', -366, 0, 190, 0, 0, 90))
PL.append(('flgf','FlgRr', -366, 212, 190, 0, 0, 0))
PL.append(('flgf','FlgLr', -366, -228, 190, 0, 0, 0))

for (key, label, bx, by, bz, rx, ry, rz) in PL:
    o = doc.addObject('Part::Feature', label)
    o.Shape = M[key]
    m = FreeCAD.Matrix()
    if rx: m.rotateX(math.radians(rx))
    if ry: m.rotateY(math.radians(ry))
    if rz: m.rotateZ(math.radians(rz))
    m.move(Vector(bx, by, bz))
    o.Placement = FreeCAD.Placement(m)

doc.recompute()
bb = doc.Objects[0].Shape.BoundBox
for o in doc.Objects[1:]:
    try: bb.add(o.Shape.BoundBox.transformed(o.Placement.Matrix))
    except Exception: pass
print('placed: %d' % len(PL))
print('envelope L%.0f W%.0f H%.0f' % (bb.XLength, bb.YLength, bb.ZLength))
print('saved')
FreeCAD.getDocument('UndercarriageV3').saveAs(
  'C:/Users/malliath/Desktop/matlab/undercarriage/v3/cad/UndercarriageV3.FCStd')
