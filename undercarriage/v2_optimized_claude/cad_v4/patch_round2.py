"""One-off patch: round-1 build_uc_v4.py -> round 2 (tensioner, M14/M12 bolts, keys, chain-wheel hub, idler shaft ext).
Kept in the repo for traceability; the patched build_uc_v4.py is the source of truth afterwards."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'build_uc_v4.py')
s = open(p, encoding='utf-8').read()

def rep(a, b):
    global s
    assert a in s, 'missing: ' + a[:70]
    s = s.replace(a, b, 1)

rep("def plate(yc):",
    "BEAM_BOLTS = {'beam_rear': [(-27, -27), (27, -27), (-27, 27), (27, 27)], 'beam_mid1': [(27, 27), (-27, -27)],\n"
    "              'beam_mid2': [(27, 27), (-27, -27)], 'beam_front': [(27, 27), (-27, -27)]}\n"
    "BEAM_POS = {'beam_rear': (-230.0, 175.0), 'beam_mid1': (-100.0, 175.0), 'beam_mid2': (100.0, 175.0), 'beam_front': (470.0, 110.0)}\n"
    "def plate(yc, inner=False):")
rep("            for sx in SPC_X:\n                with Locations((sx, SPC_Z)): Circle(8.5, mode=Mode.SUBTRACT)\n",
    "            for sx in SPC_X:\n                with Locations((sx, SPC_Z)): Circle(8.5, mode=Mode.SUBTRACT)\n"
    "            if inner:\n                for nm_, (bx, bz) in BEAM_POS.items():\n                    for dx, dz in BEAM_BOLTS[nm_]:\n"
    "                        with Locations((bx + dx, bz + dz)): Circle(6.5, mode=Mode.SUBTRACT)\n")
rep("add('plate_in', plate(Y_PIN), 'structure'); add('plate_out', plate(Y_POUT), 'structure')",
    "add('plate_in', plate(Y_PIN, True), 'structure'); add('plate_out', plate(Y_POUT, False), 'structure')")
rep("BEAMS = [('beam_rear', -230.0, 175.0), ('beam_mid1', -100.0, 175.0), ('beam_mid2', 100.0, 175.0), ('beam_front', 495.0, 110.0)]",
    "BEAMS = [(n_, p_[0], p_[1]) for n_, p_ in BEAM_POS.items()]")
rep("add('axle', cy(20.0, 0, 245.0, FACE_OUT_O + U['A0_total_mm'] - 1.0, xs, zs), 'drive')   # ends 1 mm inside outer UCFL face",
    "KEYS = [(236.0, 272.0), (410.0, 450.0)]       # chain-wheel key 12x8x36, sprocket-hub key 12x8x40 (DIN 6885-A, t1=5.0 t2=3.3 UNVERIFIED)\n"
    "def seat(y0, y1): return box(xs - 6, xs + 6, y0, y1, zs + 15.0, zs + 21.0)\n"
    "def hubway(y0, y1): return box(xs - 6, xs + 6, y0, y1, zs + 19.5, zs + 23.3)\n"
    "ax = cy(20.0, 0, 225.0, FACE_OUT_O + U['A0_total_mm'] - 1.0, xs, zs)\n"
    "for k0, k1 in KEYS: ax = ax - seat(k0, k1)\n"
    "add('axle', ax, 'drive')   # ends 1 mm inside outer UCFL face\n"
    "for i_, (k0, k1) in enumerate(KEYS): add(f'key{i_}', box(xs - 6, xs + 6, k0, k1, zs + 15.0, zs + 23.0), 'drive')")
rep("add('hub', cy(38.0, 20.0, 408.0, 452.0, xs, zs), 'drive')",
    "add('hub', cy(38.0, 20.0, 408.0, 452.0, xs, zs) - hubway(*KEYS[1]), 'drive')")
rep("cw = cw - Cylinder(20, 10)\nadd('chainwheel', Pos(xs, 253.0, zs) * Rot(X=90) * cw, 'drive')\n"
    "add('chainwheel_boss', cy(30.0, 20.0, 256.0, FACE_IN_I - U['A0_total_mm'] - 2.0, xs, zs), 'drive')",
    "cw = cw - Cylinder(20, 10)\nadd('chainwheel', Pos(xs, 237.0, zs) * Rot(X=90) * cw - hubway(234.0, 240.0), 'drive')\n"
    "add('chainwheel_boss', cy(30.0, 20.0, 240.0, FACE_IN_I - U['A0_total_mm'] - 2.0, xs, zs) - hubway(240.0, 275.0), 'drive')")
rep("add('motor_ph', cy(50.0, 0, 90.0, 235.0, xs, zs + CH_C), 'drive', CAT['motor_placeholder']['mass_kg'])\n"
    "add('motor_shaft_ph', cy(10.0, 0, 235.0, 262.0, xs, zs + CH_C), 'drive')",
    "add('motor_ph', cy(50.0, 0, 80.0, 218.0, xs, zs + CH_C), 'drive', CAT['motor_placeholder']['mass_kg'])\n"
    "add('motor_shaft_ph', cy(10.0, 0, 218.0, 246.0, xs, zs + CH_C), 'drive')")
rep("add('pinion', Pos(xs, 253.0, zs + CH_C) * Rot(X=90) * (pin - Cylinder(10, 10)), 'drive')",
    "add('pinion', Pos(xs, 237.0, zs + CH_C) * Rot(X=90) * (pin - Cylinder(10, 10)), 'drive')")
rep("def spool_set(tag, xc, zc, Ro, wall, with_shaft_ends=True):", "def spool_set(tag, xc, zc, Ro, wall, ext=0.0):")
rep("    add(f'{tag}_shaft', cy(12.5, 0, 329.0, 531.0, xc, zc) + cy(12.0, 0, 296.0, 329.0, xc, zc) + cy(12.0, 0, 531.0, 564.0, xc, zc), 'running')",
    "    add(f'{tag}_shaft', cy(12.5, 0, 329.0 - ext, 531.0 + ext, xc, zc) + cy(12.0, 0, 296.0 - ext, 329.0 - ext, xc, zc) + cy(12.0, 0, 531.0 + ext, 564.0 + ext, xc, zc), 'running')")
rep("(('i', (FACE_IN_I, FACE_IN_I - wb, 90)), ('o', (FACE_OUT_O, FACE_OUT_O + wb, -90)))",
    "(('i', (FACE_IN_I - ext, FACE_IN_I - ext - wb, 90)), ('o', (FACE_OUT_O + ext, FACE_OUT_O + ext + wb, -90)))")
rep("spool_set('idl', xi, zi, R_in_i, T_ID)   # idler shaft shares the same stack (shaft ends/tensioner added round 2)",
    "spool_set('idl', xi, zi, R_in_i, T_ID, ext=30.0)   # ext: shaft passes through the tension blocks (y 297..327 / 533..563)")

r2 = '''# ---------------- tensioner: block on idler shaft, M16 rod, anchor lug ----------------
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
    for k, (dx, dz) in enumerate(BEAM_BOLTS[nm_]):
        scr = HexHeadScrew(size='M12-1.75', length=30.0, fastener_type='iso4014')
        add(f'{nm_}_bolt{k}', Pos(bx + dx, FACE_IN_I - 6.0, bz + dz) * Rot(X=90) * scr, 'structure')
        add(f'{nm_}_wsh{k}', Pos(bx + dx, FACE_IN_O, bz + dz) * Rot(X=-90) * wsh12, 'structure')
        add(f'{nm_}_nut{k}', Pos(bx + dx, FACE_IN_O + wb12, bz + dz) * Rot(X=-90) * nut12, 'structure')

'''
rep("# ---------------- cross beams ----------------", r2 + "# ---------------- cross beams ----------------")
rep("from bd_warehouse.fastener import HexNut, PlainWasher", "from bd_warehouse.fastener import HexNut, PlainWasher, HexHeadScrew")
rep("    if (('_nut_' in a or '_nut_' in b_ or '_wsh_' in a or '_wsh_' in b_) and ('shaft' in a or 'shaft' in b_ or 'rod' in a or 'rod' in b_)):\n        continue",
    "    fasten = lambda n: ('nut' in n or 'wsh' in n)\n    thread = lambda n: ('shaft' in n or 'rod' in n or 'bolt' in n)\n"
    "    if (fasten(a) and thread(b_)) or (fasten(b_) and thread(a)):\n        continue      # threaded engagement, thread not modelled (intended)")
open(p, 'w', encoding='utf-8').write(s)
print('patched')
