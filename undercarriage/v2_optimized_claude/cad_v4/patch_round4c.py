"""Patch round 4c: swappable chain wheel. Hub flange (OD120 x 8, 6x tapped M8 on PCD100) + bolt-on chain-wheel plate; tooth counts via env UC_WHEEL_T / UC_PINION_T;
chain length auto (nearest even link count) unless UC_LINKS is set."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'build_uc_v4.py')
s = open(p, encoding='utf-8').read()
assert 'ROUND4C' not in s

def rep(a, b):
    global s
    assert a in s, 'missing: ' + a[:90]
    s = s.replace(a, b, 1)

rep("CW_T, CW_N, PIN_N = 48, 48, 14      # ROUND4A: R15-type 48T rear sprocket on the axle, 14T pinion on the motor (ratio 3.43)\nCH_LINKS = 62",
    "CW_N = int(os.environ.get('UC_WHEEL_T', 48)); PIN_N = int(os.environ.get('UC_PINION_T', 14))   # ROUND4C swappable: wheel (axle) and pinion (motor) teeth\n"
    "PCD_CW = 100.0                                                       # bolt circle of the swappable chain-wheel plate (6 x M8)\n"
    "_PDw, _PDp = 12.7 / math.sin(math.pi / CW_N), 12.7 / math.sin(math.pi / PIN_N)\n"
    "_cd0 = (_PDw + _PDp) / 2 + 70.0                                       # target centre distance: wheel R + pinion R + 70 mm\n"
    "_lk0 = 2 * _cd0 / 12.7 + (PIN_N + CW_N) / 2 + ((CW_N - PIN_N) / (2 * math.pi)) ** 2 * 12.7 / _cd0\n"
    "CH_LINKS = int(os.environ.get('UC_LINKS', 2 * round(_lk0 / 2)))     # even link count (no offset link)")
rep("def chain_links(Cc, z1=14, z2=48, p=12.7)", "def chain_links(Cc, z1=PIN_N, z2=CW_N, p=12.7)")
old_start = s.index("cw = Sprocket(num_teeth=CW_N")
old_end = s.index("def chain_links")
new = ("cw = Sprocket(num_teeth=CW_N, chain_pitch=12.7, roller_diameter=8.51, thickness=6.0, bolt_circle_diameter=PCD_CW, num_mount_bolts=6, mount_bolt_diameter=9.0, bore_diameter=64.0)\n"
       "add('chainwheel', Pos(xs, 231.0, zs) * Rot(X=90) * cw, 'drive')          # swappable plate y 228..234, bolted to the hub flange\n"
       "cwf = cy(60.0, 20.0, 234.0, 242.0, xs, zs) - hubway(234.0, 242.0)\n"
       "for k_ in range(6):\n"
       "    a_ = math.radians(60 * k_); cwf = cwf - cy(3.4, 0, 233.0, 243.0, xs + PCD_CW / 2 * math.cos(a_), zs + PCD_CW / 2 * math.sin(a_))   # M8 tap drill\n"
       "add('cw_flange', cwf, 'drive')\n"
       "add('chainwheel_boss', cy(30.0, 20.0, 242.0, FACE_IN_I - U['A0_total_mm'] - 2.0, xs, zs) - hubway(242.0, 275.0), 'drive')\n"
       "_m8 = HexHeadScrew(size='M8-1.25', length=16.0, fastener_type='iso4017')\n"
       "for k_ in range(6):\n"
       "    a_ = math.radians(60 * k_); add(f'cw_bolt{k_}', Pos(xs + PCD_CW / 2 * math.cos(a_), 228.0, zs + PCD_CW / 2 * math.sin(a_)) * Rot(X=90) * _m8, 'drive')\n"
       "pin = Sprocket(num_teeth=PIN_N, chain_pitch=12.7, roller_diameter=8.51, thickness=6.0)\n"
       "# pinion plane y=231 = chain-wheel plane (motor shaft y 218..246)\n")
# keep everything between the old Sprocket line and chain_links? the original block between them holds only cw lines; replace whole span
s = s[:old_start] + new + s[old_end:]
rep("add('pinion', Pos(xs, 237.0, zs + CH_C) * Rot(X=90) * (pin - Cylinder(10, 10)), 'drive')",
    "add('pinion', Pos(xs, 231.0, zs + CH_C) * Rot(X=90) * (pin - Cylinder(10, 10)), 'drive')")
rep("pin = Sprocket(num_teeth=PIN_N, chain_pitch=12.7, roller_diameter=8.51, thickness=6.0)\nadd('pinion'",
    "add('pinion'") if "pin = Sprocket(num_teeth=PIN_N, chain_pitch=12.7, roller_diameter=8.51, thickness=6.0)\nadd('pinion'" in s else None
rep("kb_ = asm['key0_R'][0].bounding_box(); bo_ = asm['chainwheel_boss_R'][0].bounding_box()",
    "kb_ = asm['key0_R'][0].bounding_box(); bo_ = asm['cw_flange_R'][0].bounding_box(); bo2_ = asm['chainwheel_boss_R'][0].bounding_box()")
rep("eng_ = min(kb_.max.Y, bo_.max.Y) - max(kb_.min.Y, bo_.min.Y)", "eng_ = min(kb_.max.Y, bo2_.max.Y) - max(kb_.min.Y, bo_.min.Y)      # key length inside flange + boss")
rep("gate('chain-wheel key engages the welded boss >=30 mm'", "gate('chain-wheel key engages flange+boss >=30 mm'")
rep("'chain wheel bottom not below the plate bottom edge (z>=25; plates z=30)', cwz_ >= 25.0, round(cwz_, 1), 25.0)",
    "'chain wheel bottom not below the plate bottom edge (z>=25; plates z=30)', cwz_ >= 25.0, round(cwz_, 1), 25.0)\n"
    "gate('chain wheel clears the rear cross-beam (>=20 mm)', (BEAM_POS['beam_rear'][0] - 20.0) - (xs + _PDw / 2 + 4.0) >= 20.0, round((BEAM_POS['beam_rear'][0] - 20.0) - (xs + _PDw / 2 + 4.0), 1), 20.0)")
rep("'beam_rear_flgR', 'tens_lug_i_R']", "'beam_rear_flgR', 'cw_flange_R', 'tens_lug_i_R']") if "'beam_rear_flgR', 'tens_lug_i_R']" in s else None
rep("drive=dict(pinion_T=PIN_N, wheel_T=CW_N,", "drive=dict(pcd_mm=PCD_CW, pinion_T=PIN_N, wheel_T=CW_N,")
open(p, 'w', encoding='utf-8').write(s)
print('patched round 4c')
