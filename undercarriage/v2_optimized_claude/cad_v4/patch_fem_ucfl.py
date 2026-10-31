"""Add CASE='ucfl' (inner-bearing reaction on the plate's two UCFL bolt holes) to fem_plate.py."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'fem_plate.py')
s = open(p, encoding='utf-8').read()
assert "CASE == 'ucfl'" not in s

def rep(a, b):
    global s
    assert a in s, 'missing: ' + a[:80]
    s = s.replace(a, b, 1)

rep("        if CASE == 'vertical' and abs(abs(d.z) - 1.0) < 1e-6 and e.Length > 100: zedge = i; break",
    "        if CASE in ('vertical', 'ucfl') and abs(abs(d.z) - 1.0) < 1e-6 and e.Length > 100: zedge = i; break")
i0 = s.index("roll = [i for i, r, c, a in cyls")
i1 = s.index("for c in forces:\n    print(c.Name")
block = s[i0:i1]
ind = ''.join('    ' + ln if ln.strip() else ln for ln in block.splitlines(True))
new = ("forces = []\n"
       "if CASE == 'ucfl':\n"
       "    xedge = next(i for i, e in enumerate(shape.Edges, 1) if e.Curve.TypeId == 'Part::GeomLine' and abs(abs(e.Curve.Direction.x) - 1.0) < 1e-6 and e.Length > 100)\n"
       "    uc = [i for i, r, c, a in cyls if abs(r - 8.0) < 0.05 and abs(c.x - inp['xs']) < 1.0]\n"
       "    print('ucfl bolt faces', uc)\n"
       "    forces.append(add_force(uc, 1289.0, 'UCFLz'))      # chain-pull reaction on the inner bearing (axle beam model)\n"
       "    c2 = ObjectsFem.makeConstraintForce(doc, 'UCFLx'); c2.References = [(obj, 'Face%d' % i) for i in uc]\n"
       "    c2.Force = '515 N'; c2.Direction = (obj, ['Edge%d' % xedge]); c2.Reversed = False; analysis.addObject(c2); doc.recompute(); forces.append(c2)\n"
       "else:\n" + ind.replace("    forces = []\n", "", 1))
s = s[:i0] + new + s[i1:]
rep("if CASE == 'vertical' and c.DirectionVector.z < 0: c.Reversed = True", "if CASE in ('vertical', 'ucfl') and c.Name != 'UCFLx' and c.DirectionVector.z < 0: c.Reversed = True")
rep("out = dict(case=('inner plate ground reaction 3x1.7 kN + idler 2.0 kN' if CASE == 'vertical' else 'inner plate lateral 1.0 kN per roller hole + idler')",
    "out = dict(case=('inner plate ground reaction 3x1.7 kN + idler 2.0 kN' if CASE == 'vertical' else ('inner plate inner-bearing reaction 1289 N vertical + 515 N horizontal on the 2 UCFL bolt holes' if CASE == 'ucfl' else 'inner plate lateral 1.0 kN per roller hole + idler'))")
rep("('fem_plate_result.json' if CASE == 'vertical' else 'fem_plate_result_lateral.json')", "{'vertical': 'fem_plate_result.json', 'lateral': 'fem_plate_result_lateral.json', 'ucfl': 'fem_plate_result_ucfl.json'}[CASE]")
open(p, 'w', encoding='utf-8').write(s)
print('fem script: ucfl case added')
