"""Patch round 4d - fixes from the round-4 Opus review.
B1 idler hub bearing seats open OUTWARD (bearing inserted from each end, shoulder inboard, DIN 472 groove at the end);
B2 sprocket-hub keyway through; G1 honest wheel-clearance gate (>= plate bottom 30) and default 13T/44T (Apache RTR 160 pair);
G2 gates tagged 'measured' vs 'by-construction'; G3 UCFL nuts vs belt gate; R2 axle end washer + M10 bolt (axial retention of the chain-wheel hub);
R3 chain wheel / pinion are BOUGHT parts -> removed from the laser DXF list; JSON gets cw_plane_y."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'build_uc_v4.py')
s = open(p, encoding='utf-8').read()
assert 'ROUND4D' not in s

def rep(a, b):
    global s
    assert a in s, 'missing: ' + a[:90]
    s = s.replace(a, b, 1)

# defaults 13T/44T
rep("CW_N = int(os.environ.get('UC_WHEEL_T', 48)); PIN_N = int(os.environ.get('UC_PINION_T', 14))",
    "CW_N = int(os.environ.get('UC_WHEEL_T', 44)); PIN_N = int(os.environ.get('UC_PINION_T', 13))   # ROUND4D default: Apache RTR 160 pair 13T/44T")
# B1 hub seats open outward
rep("        for (a0, a1, g0, g1) in ((361.0, 378.15, 376.0, 378.15), (481.85, 499.0, 481.85, 484.0)):",
    "        for (a0, a1, g0, g1) in ((354.0, 376.0, 358.85, 361.0), (484.0, 506.0, 499.0, 501.15)):   # ROUND4D: seats open outward, shoulder inboard at y=376/484")
rep("        lo, hi = span(376.075, 378.075); add(f'{tag}_clip_{side}', cy(27.5, 23.0, lo, hi, xc, zc), 'running')",
    "        lo, hi = span(358.925, 360.925) if onepiece else span(376.075, 378.075); add(f'{tag}_clip_{side}', cy(27.5, 23.0, lo, hi, xc, zc), 'running')")
# B2 through keyway in the sprocket hub
rep("add('hub', cy(38.0, 20.0, 408.0, 452.0, xs, zs) - hubway(*KEYS[1]), 'drive')",
    "add('hub', cy(38.0, 20.0, 408.0, 452.0, xs, zs) - hubway(407.0, 453.0), 'drive')   # keyway through the full hub (broachable)")
# R2 axle starts flush with the flange inboard face; end washer + M10 bolt retain the chain-wheel hub
rep("ax = cy(20.0, 0, 225.0, FACE_OUT_O + U['A0_total_mm'] - 1.0, xs, zs)",
    "ax = cy(20.0, 0, 234.0, FACE_OUT_O + U['A0_total_mm'] - 1.0, xs, zs) - cy(4.25, 0, 233.0, 259.0, xs, zs)   # ends flush with the hub flange; M10 tapped centre hole")
rep("add('chainwheel_boss', cy(30.0, 20.0, 242.0,",
    "add('endwsh', cy(25.0, 5.5, 230.0, 234.0, xs, zs), 'drive')\n"
    "add('endbolt', Pos(xs, 230.0, zs) * Rot(X=90) * HexHeadScrew(size='M10-1.5', length=25.0, fastener_type='iso4017'), 'drive')   # retains the hub axially (loctite-free, spring washer optional)\n"
    "add('chainwheel_boss', cy(30.0, 20.0, 242.0,")
rep("    fasten = lambda n: ('nut' in n or 'wsh' in n)",
    "    if ('axle' in a and 'endbolt' in b_) or ('axle' in b_ and 'endbolt' in a):\n        continue      # M10 bolt in its tapped hole, thread not modelled\n    fasten = lambda n: ('nut' in n or 'wsh' in n)")
# G1 honest wheel clearance
rep("gate('chain wheel bottom not below the plate bottom edge (z>=25; plates z=30)', cwz_ >= 25.0, round(cwz_, 1), 25.0)",
    "gate('chain wheel bottom not below the plate bottom edge (z>=30)', cwz_ >= 30.0, round(cwz_, 1), 30.0)")
# G3 UCFL nuts vs belt
rep("def mind(a, b): return asm[a][0].distance_to(asm[b][0])",
    "def mind(a, b): return asm[a][0].distance_to(asm[b][0])\nd_un = min(mind(n, 'track_R') for n in asm if n.startswith('ucflnut_') and n.endswith('_R'))\n"
    "gate('UCFL M14 nuts clear of the belt >=5', d_un >= 5.0, round(d_un, 1), 5.0)")
# G2 tagging: gate() default kind, then post-process
rep("def gate(name, ok, val, lim): gates.append(dict(gate=name, ok=bool(ok), value=val, limit=lim))",
    "def gate(name, ok, val, lim): gates.append(dict(gate=name, ok=bool(ok), value=val, limit=lim, kind='measured'))")
rep("bb = allsolids.bounding_box()", "bb = allsolids.bounding_box()")
rep("out = dict(drive=dict(",
    "_CONSTR = ('spool stack', 'nut seats', 'track bottom', 'chain %d' % CH_LINKS, 'drum gap', 'hub/collar', 'idler hub inside', 'first roller to sprocket', 'last roller to idler')\n"
    "for g_ in gates:\n"
    "    if any(k in g_['gate'] for k in _CONSTR): g_['kind'] = 'by-construction'\n"
    "out = dict(drive=dict(")
rep("layout=dict(Rp=Rp,", "layout=dict(cw_plane_y=231.0, Rp=Rp,")
# R3: bought sprockets are not laser parts
rep("'rol0_seat_i_R', 'chainwheel_R', 'pinion_R',", "'rol0_seat_i_R',")
open(p, 'w', encoding='utf-8').write(s)
print('patched round 4d')
