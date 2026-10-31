"""Patch round 3c: beams bolt into 8 mm tapped pads welded on the plate's INBOARD face (no nuts on the track side)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'build_uc_v4.py')
s = open(p, encoding='utf-8').read()
assert 'ROUND3C' not in s

def rep(a, b):
    global s
    assert a in s, 'missing: ' + a[:80]
    s = s.replace(a, b, 1)

rep("                        with Locations((bx + dx, bz + dz)): Circle(6.5, mode=Mode.SUBTRACT)",
    "                        with Locations((bx + dx, bz + dz)): Circle(5.1, mode=Mode.SUBTRACT)   # M12 tap drill 10.2 (ROUND3C)")
rep("BL = 2 * FACE_IN_I - 2 * 6.0", "PAD_T = 8.0\nBL = 2 * (FACE_IN_I - PAD_T - 6.0)      # tube length between the two flanges (flange inboard of the 8 mm pad)")
rep("        y0f_, y1f_ = (321.0, 327.0) if sgn > 0 else (-327.0, -321.0)",
    "        y0f_, y1f_ = (FACE_IN_I - PAD_T - 6.0, FACE_IN_I - PAD_T) if sgn > 0 else (-(FACE_IN_I - PAD_T), -(FACE_IN_I - PAD_T - 6.0))")
old = """        scr = HexHeadScrew(size='M12-1.75', length=30.0, fastener_type='iso4014')
        add(f'{nm_}_bolt{k}', Pos(bx + dx, FACE_IN_I - 6.0, bz + dz) * Rot(X=90) * scr, 'structure')
        add(f'{nm_}_wsh{k}', Pos(bx + dx, FACE_IN_O, bz + dz) * Rot(X=-90) * wsh12, 'structure')
        add(f'{nm_}_nut{k}', Pos(bx + dx, FACE_IN_O + wb12, bz + dz) * Rot(X=-90) * nut12, 'structure')"""
new = """        scr = HexHeadScrew(size='M12-1.75', length=25.0, fastener_type='iso4014')
        yf = FACE_IN_I - PAD_T - 6.0                         # flange inboard face
        add(f'{nm_}_wsh{k}', Pos(bx + dx, yf, bz + dz) * Rot(X=90) * wsh12, 'structure')
        add(f'{nm_}_bolt{k}', Pos(bx + dx, yf - wb12, bz + dz) * Rot(X=90) * scr, 'structure')   # tip ends ~2 mm past plate (tapped pad+plate)"""
rep(old, new)
# pads: one per beam end, inserted before the beam-bolt loop header
rep("for nm_, (bx, bz) in BEAM_POS.items():\n    for k, (dx, dz) in enumerate(BEAM_BOLTS[nm_]):",
    "for nm_, (bx, bz) in BEAM_POS.items():\n"
    "    pad = box(bx - 35, bx + 35, FACE_IN_I - PAD_T, FACE_IN_I, bz - 35, bz + 35)\n"
    "    for dx_, dz_ in BEAM_BOLTS[nm_]: pad = pad - cy(5.1, 0, FACE_IN_I - PAD_T - 1, FACE_IN_I + 1, bx + dx_, bz + dz_)\n"
    "    add(f'{nm_}_pad', pad, 'structure')\n"
    "    for k, (dx, dz) in enumerate(BEAM_BOLTS[nm_]):")
# PAD_T must exist before the r2 block; it is defined at the BL line which comes later -> define early
rep("BEAM_BOLTS = {", "PAD_T = 8.0\nBEAM_BOLTS = {")
# gate replacement (no beam nuts any more)
rep("nut_names = [n for n in asm if n.startswith('beam_') and '_nut' in n and n.endswith('_R')]\nd_nut_belt = min(mind(n, 'track_R') for n in nut_names)\ngate('beam nuts clear of belt >=25', d_nut_belt >= 25.0, round(d_nut_belt, 1), 25.0)",
    "bolt_names = [n for n in asm if n.startswith('beam_') and '_bolt' in n and n.endswith('_R')]\nd_bolt_belt = min(mind(n, 'track_R') for n in bolt_names)\n"
    "gate('beam bolt tips clear of belt >=4 (no nuts on track side)', d_bolt_belt >= 4.0, round(d_bolt_belt, 1), 4.0)")
open(p, 'w', encoding='utf-8').write(s)
print('patched round 3c')
