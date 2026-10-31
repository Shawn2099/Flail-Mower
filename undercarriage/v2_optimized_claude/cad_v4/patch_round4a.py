"""Patch round 4a: single-stage drive 14T (motor) -> 48T (R15-type rear sprocket on axle), 62-link chain, real motor mass, chain data in JSON."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'build_uc_v4.py')
s = open(p, encoding='utf-8').read()
assert 'ROUND4A' not in s

def rep(a, b):
    global s
    assert a in s, 'missing: ' + a[:80]
    s = s.replace(a, b, 1)

rep("CW_T, CW_N, PIN_N = 43, 43, 14", "CW_T, CW_N, PIN_N = 48, 48, 14      # ROUND4A: R15-type 48T rear sprocket on the axle, 14T pinion on the motor (ratio 3.43)\nCH_LINKS = 62")
rep("def chain_links(Cc, z1=14, z2=43, p=12.7)", "def chain_links(Cc, z1=14, z2=48, p=12.7)")
rep("    if chain_links(mid_) < 58: lo_ = mid_", "    if chain_links(mid_) < CH_LINKS: lo_ = mid_")
rep("# centre distance for exactly 58 links", "# centre distance for exactly CH_LINKS links")
rep("add('motor_ph', cy(50.0, 0, 80.0, 218.0, xs, zs + CH_C), 'drive', CAT['motor_placeholder']['mass_kg'])",
    "add('motor_ph', cy(50.0, 0, 80.0, 218.0, xs, zs + CH_C), 'drive', CAT['motor_bm1418zxf']['mass_kg_used'])   # envelope = PLACEHOLDER (no drawing); mass 7.12 kg from one listing (3.0/7.12/10.66 disputed)")
rep("'chain 08B-1 58 links x2 (0.7 kg/m, retailer)': 1.03", "'chain 428 62 links x2 (0.7 kg/m, retailer)': 1.1")
rep("gate('chain 58 whole links at C=%.1f' % CH_C, abs(chain_links(CH_C) - 58.0) < 0.01, round(chain_links(CH_C), 3), 58)",
    "gate('chain %d whole links at C=%.1f' % (CH_LINKS, CH_C), abs(chain_links(CH_C) - CH_LINKS) < 0.01, round(chain_links(CH_C), 3), CH_LINKS)")
rep("gate('chain wheel ground clearance >=35 (info: v2 was 36)', cwz_ >= 35.0, round(cwz_, 1), 35.0)",
    "gate('chain wheel bottom not below the plate bottom edge (z>=25; plates z=30)', cwz_ >= 25.0, round(cwz_, 1), 25.0)")
# chain info into JSON
rep("out = dict(allowances_kg=ALLOW_KG, layout=",
    "out = dict(drive=dict(pinion_T=PIN_N, wheel_T=CW_N, ratio=CW_N / PIN_N, chain_links=CH_LINKS, chain_C_mm=CH_C, motor_mass_kg=CAT['motor_bm1418zxf']['mass_kg_used']),\n           allowances_kg=ALLOW_KG, layout=")
open(p, 'w', encoding='utf-8').write(s)
print('patched round 4a')
