"""Patch: add labelled mass allowances, laser DXF export and BOM CSV to build_uc_v4.py."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'build_uc_v4.py')
s = open(p, encoding='utf-8').read()

def rep(a, b):
    global s
    assert a in s, 'missing: ' + a[:70]
    s = s.replace(a, b, 1)

rep("total = sum(cat_tot.values())",
    "# Items NOT yet modelled in CAD: carried as explicit, labelled allowances (estimates, not measurements)\n"
    "ALLOW_KG = {'chain 08B-1 58 links x2 (0.7 kg/m, retailer)': 1.03, 'chain guards x2 (1.5 mm sheet, estimate)': 3.0,\n"
    "            'motor rails x4 (v2 value 1.11 kg each)': 4.44, 'deck mounts + lift lugs (deck not defined)': 0.0}\n"
    "for k_, v_ in ALLOW_KG.items(): cat_tot['allowance'] = cat_tot.get('allowance', 0.0) + v_\n"
    "total = sum(cat_tot.values())")
rep("out = dict(layout=", "out = dict(allowances_kg=ALLOW_KG, layout=")

tail = '''
# ---------------- laser DXF export (right-side copy of each plate part) ----------------
import csv
from collections import Counter
dxf_dir = os.path.join(HERE, 'dxf'); os.makedirs(dxf_dir, exist_ok=True)
LASER = ['plate_in_R', 'plate_out_R', 'spr_a_R', 'rol0_back_i_R', 'idl_back_i_R', 'rol0_seat_i_R', 'chainwheel_R', 'pinion_R',
         'tens_lug_i_R', 'beam_rear_flgR']
dxf_done = []
for n in LASER:
    shp = asm[n][0]
    fs = shp.faces().filter_by(Axis.Y)
    f = max(fs, key=lambda q: q.area)
    exp = ExportDXF(unit=Unit.MM); exp.add_layer('CUT', color=ColorIndex.RED)
    for w in [f.outer_wire()] + list(f.inner_wires()):
        exp.add_shape(w.to_local_coords(Plane.XZ), layer='CUT')
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
'''
s = s.rstrip('\n') + '\n' + tail
open(p, 'w', encoding='utf-8').write(s)
print('patched round 3')
