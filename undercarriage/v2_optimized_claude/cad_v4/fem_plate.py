# KNOWN ISSUE (2026-10-31): CASE="ucfl" produced NO node loads on the two R8 bolt-hole faces (solver input had empty *CLOAD sets) -> its result was discarded. Use the analytic axle-beam reaction in sim_uc_v4.m instead.
"""fem_plate.py - run INSIDE FreeCAD (exec(open(...).read())). CalculiX + Gmsh bundled with FreeCAD 1.1.
Inner side plate 6 mm IS2062 E250. Load case 'ground reaction up': 1.7 kN on each roller hole, 2.0 kN on the idler slot top face
(v2 worst-case station loads incl. shock, applied in full to the inner plate = conservative; spacer tubes/outer plate not credited).
Restraint: the 10 beam-bolt holes (M12) fixed. Allowable = 250/1.5 = 167 MPa nominal. ASSUMPTIONS flagged in the JSON output.
"""
import FreeCAD, Part, ObjectsFem, json, math, os
from femtools import ccxtools
from femmesh import gmshtools

CASE = globals().get('CASE', 'vertical')      # 'vertical' (ground reaction up) or 'lateral' (skid side load, 1.0 kN per hole)
P = 'C:/Users/malliath/Desktop/matlab/undercarriage/v2_optimized_claude/cad_v4/parts/'
inp = json.load(open(P + 'fem_inputs.json'))
BEAM_BOLTS = {'beam_rear': [(-27, -27), (27, -27), (-27, 27), (27, 27)], 'beam_mid1': [(27, 27), (-27, -27)],
              'beam_mid2': [(27, 27), (-27, -27)], 'beam_front': [(-27, -27), (27, -27)]}
for n in list(FreeCAD.listDocuments()):
    if n.startswith('FEM_plate'): FreeCAD.closeDocument(n)
doc = FreeCAD.newDocument('FEM_plate')
obj = doc.addObject('Part::Feature', 'Plate')
_plate = Part.read(P + 'plate_in_R.step'); _pads = Part.read(P + 'pads_R.step')
obj.Shape = _plate.fuse(_pads).removeSplitter(); doc.recompute()      # plate + four 8 mm tapped pads (beam joints)
shape = obj.Shape

analysis = ObjectsFem.makeAnalysis(doc, 'Analysis')
solver = ObjectsFem.makeSolverCalculiXCcxTools(doc, 'Solver'); solver.AnalysisType = 'static'; solver.GeometricalNonlinearity = 'linear'
solver.ThermoMechSteadyState = False; solver.MatrixSolverType = 'default'; analysis.addObject(solver)
mat = ObjectsFem.makeMaterialSolid(doc, 'Steel')
m = mat.Material; m['Name'] = 'IS2062_E250'; m['YoungsModulus'] = '210000 MPa'; m['PoissonRatio'] = '0.30'; m['Density'] = '7850 kg/m^3'
mat.Material = m; analysis.addObject(mat)

def cyl_faces():
    out = []
    for i, f in enumerate(shape.Faces, 1):
        sf = f.Surface
        if sf.TypeId == 'Part::GeomCylinder':
            out.append((i, sf.Radius, f.CenterOfMass, f.Area))
    return out
cyls = cyl_faces()

# vertical (Z) straight edge for force direction reference
zedge = None
for i, e in enumerate(shape.Edges, 1):
    if e.Curve.TypeId == 'Part::GeomLine':
        d = e.Curve.Direction
        if CASE in ('vertical', 'ucfl') and abs(abs(d.z) - 1.0) < 1e-6 and e.Length > 100: zedge = i; break
        if CASE == 'lateral' and abs(abs(d.y) - 1.0) < 1e-6: zedge = i; break
print('z-edge', zedge, 'cyl faces', len(cyls))

# fixed: inboard faces of the four pads (planar, normal -Y, y = 327-8 = 319): the beam flange bears on these
fixed = []
for i, f in enumerate(shape.Faces, 1):
    if f.Surface.TypeId == 'Part::GeomPlane' and abs(abs(f.normalAt(0, 0).y) - 1.0) < 1e-6 and abs(f.CenterOfMass.y - 319.0) < 0.2:
        fixed.append(i)
print('fixed pad faces', fixed)
cf = ObjectsFem.makeConstraintFixed(doc, 'Fixed'); cf.References = [(obj, 'Face%d' % i) for i in fixed]; analysis.addObject(cf)

def add_force(faces, newtons, name):
    c = ObjectsFem.makeConstraintForce(doc, name); c.References = [(obj, 'Face%d' % i) for i in faces]
    c.Force = '%d N' % newtons; c.Direction = (obj, ['Edge%d' % zedge]); c.Reversed = False
    analysis.addObject(c); doc.recompute()
    return c
forces = []
if CASE == 'ucfl':
    xedge = next(i for i, e in enumerate(shape.Edges, 1) if e.Curve.TypeId == 'Part::GeomLine' and abs(abs(e.Curve.Direction.x) - 1.0) < 1e-6 and e.Length > 100)
    uc = [i for i, r, c, a in cyls if abs(r - 8.0) < 0.05 and abs(c.x - inp['xs']) < 1.0]
    print('ucfl bolt faces', uc)
    forces.append(add_force(uc, 1289.0, 'UCFLz'))      # chain-pull reaction on the inner bearing (axle beam model)
    c2 = ObjectsFem.makeConstraintForce(doc, 'UCFLx'); c2.References = [(obj, 'Face%d' % i) for i in uc]
    c2.Force = '515 N'; c2.Direction = (obj, ['Edge%d' % xedge]); c2.Reversed = False; analysis.addObject(c2); doc.recompute(); forces.append(c2)
else:
    roll = [i for i, r, c, a in cyls if abs(r - 13.0) < 0.05 and any(abs(c.x - x) < 1.0 for x in inp['rollers']) and abs(c.z - inp['zr']) < 1.0]
    print('roller hole faces', roll)
    QR = 1700.0 if CASE == 'vertical' else 1000.0
    for k, i in enumerate(roll): forces.append(add_force([i], QR, 'Roller%d' % k))
    # idler slot top face: planar face with normal +-Z at z = zi + 12.75
    slot_top = None
    for i, f in enumerate(shape.Faces, 1):
        if f.Surface.TypeId == 'Part::GeomPlane' and abs(abs(f.normalAt(0, 0).z) - 1.0) < 1e-6 and abs(f.CenterOfMass.z - (inp['zi'] + 12.75)) < 0.5 and abs(f.CenterOfMass.x - (inp['xi'] + 5.0)) < 3.0:
            slot_top = i
    print('slot top face', slot_top)
    forces.append(add_force([slot_top], 2000.0 if CASE == 'vertical' else 1000.0, 'Idler'))
for c in forces:
    print(c.Name, 'dir vec', tuple(round(v, 2) for v in c.DirectionVector))
# make every force point +Z (ground reaction pushes shaft up into plate)
for c in forces:
    if CASE in ('vertical', 'ucfl') and c.Name != 'UCFLx' and c.DirectionVector.z < 0: c.Reversed = True      # lateral: sign irrelevant (all same direction)
doc.recompute()

mesh = ObjectsFem.makeMeshGmsh(doc, 'Mesh'); mesh.Shape = obj
_mx, _mn = globals().get('MESH', (11.0, 2.5)); mesh.CharacteristicLengthMax = '%s mm' % _mx; mesh.CharacteristicLengthMin = '%s mm' % _mn; mesh.ElementOrder = '2nd'; mesh.SecondOrderLinear = True
analysis.addObject(mesh); doc.recompute()
g = gmshtools.GmshTools(mesh); err = g.create_mesh(); print('gmsh err', err, 'nodes', mesh.FemMesh.NodeCount, 'volumes', mesh.FemMesh.VolumeCount)
doc.recompute()

fea = ccxtools.FemToolsCcx(analysis, solver); fea.update_objects(); fea.setup_working_dir(); fea.setup_ccx()
msg = fea.check_prerequisites(); print('prereq:', msg)
fea.purge_results(); fea.write_inp_file()
print('working dir:', fea.working_dir, '| inp:', fea.inp_file_name)
fea.ccx_run()
print('ccx binary:', getattr(fea, 'ccx_binary', None), '| error:', getattr(fea, 'error', None), '| ccx_exit:', getattr(fea, 'ccx_process', None) and fea.ccx_process.exitCode())
try: print('ccx stdout tail:', str(fea.ccx_stdout)[-1500:])
except Exception as e: print('no stdout', e)
print('dir listing:', os.listdir(fea.working_dir))
fea.load_results(); doc.recompute()
res = [o for o in doc.Objects if o.isDerivedFrom('Fem::FemResultObject')]
print('result objects:', [o.Name for o in res])
r = res[-1]
vm = list(r.vonMises); disp = list(r.DisplacementLengths)
vm_sorted = sorted(vm)
p95 = vm_sorted[int(0.95 * len(vm_sorted))]; p99 = vm_sorted[int(0.99 * len(vm_sorted))]
out = dict(case=('inner plate ground reaction 3x1.7 kN + idler 2.0 kN' if CASE == 'vertical' else ('inner plate inner-bearing reaction 1289 N vertical + 515 N horizontal on the 2 UCFL bolt holes' if CASE == 'ucfl' else 'inner plate lateral 1.0 kN per roller hole + idler')) + ', 4 tapped-pad faces fixed (beam joints)', max_vm_MPa=max(vm), p99_MPa=p99, p95_MPa=p95,
           max_disp_mm=max(disp), nodes=mesh.FemMesh.NodeCount, allowable_MPa=167.0, yield_MPa=250.0,
           note='peak at constrained/loaded hole edges is partly a constraint singularity; judge by p95/p99 and the hole-edge max vs yield')
json.dump(out, open(P + {'vertical': 'fem_plate_result.json', 'lateral': 'fem_plate_result_lateral.json', 'ucfl': 'fem_plate_result_ucfl.json'}[CASE], 'w'), indent=1)
print(json.dumps(out, indent=1))
