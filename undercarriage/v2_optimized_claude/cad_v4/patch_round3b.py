"""Patch round 3b: one-piece centre-groove idler, beam heights, new computed gates. Idempotent guard via marker."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'build_uc_v4.py')
s = open(p, encoding='utf-8').read()
assert 'ROUND3B' not in s, 'already patched'

def rep(a, b):
    global s
    assert a in s, 'missing: ' + a[:80]
    s = s.replace(a, b, 1)

# beam heights: rear/mid up to z=160 (nuts clear of roller washers and belt), front down to z=90 (rod clearance)
rep("BEAM_POS = {'beam_rear': (-230.0, 175.0), 'beam_mid1': (-100.0, 175.0), 'beam_mid2': (100.0, 175.0), 'beam_front': (470.0, 110.0)}",
    "BEAM_POS = {'beam_rear': (-230.0, 160.0), 'beam_mid1': (-100.0, 160.0), 'beam_mid2': (100.0, 160.0), 'beam_front': (470.0, 90.0)}  # ROUND3B")

# spool_set: one-piece idler option
rep("def spool_set(tag, xc, zc, Ro, wall, ext=0.0):", "def spool_set(tag, xc, zc, Ro, wall, ext=0.0, onepiece=False):")
rep("        lo, hi = span(355.0, 361.0);   add(f'{tag}_back_{side}', cy(Ri, 23.0, lo, hi, xc, zc), 'running')\n"
    "        lo, hi = span(361.0, 379.0)\n"
    "        seat = cy(32.5, 26.0, lo, hi, xc, zc)\n"
    "        g0, g1 = span(376.0, 378.15); seat = seat - cy(27.5, 20.0, g0, g1, xc, zc)\n"
    "        add(f'{tag}_seat_{side}', seat, 'running')\n",
    "        lo, hi = span(355.0, 361.0);   add(f'{tag}_back_{side}', cy(Ri, 32.5 if onepiece else 23.0, lo, hi, xc, zc), 'running')\n"
    "        if not onepiece:\n"
    "            lo, hi = span(361.0, 379.0)\n"
    "            seat = cy(32.5, 26.0, lo, hi, xc, zc)\n"
    "            g0, g1 = span(376.0, 378.15); seat = seat - cy(27.5, 20.0, g0, g1, xc, zc)\n"
    "            add(f'{tag}_seat_{side}', seat, 'running')\n")
rep("    add(f'{tag}_spc_mid', cy(16.0, 12.75, 376.0, 484.0, xc, zc), 'running')",
    "    add(f'{tag}_spc_mid', cy(16.0, 12.75, 376.0, 484.0, xc, zc), 'running')\n"
    "    if onepiece:   # one rotating weldment: hub tube OD65 bored 46 with two 52 bearing seats + circlip grooves; 70 mm centre groove for the horns\n"
    "        hub = cy(32.5, 23.0, 355.0, 505.0, xc, zc)\n"
    "        for (a0, a1, g0, g1) in ((361.0, 378.15, 376.0, 378.15), (481.85, 499.0, 481.85, 484.0)):\n"
    "            hub = hub - cy(26.0, 0, a0, a1, xc, zc) - cy(27.5, 0, g0, g1, xc, zc)\n"
    "        add(f'{tag}_hubtube', hub, 'running')")
rep("spool_set('idl', xi, zi, R_in_i, T_ID, ext=30.0)", "spool_set('idl', xi, zi, R_in_i, T_ID, ext=30.0, onepiece=True)")

# new computed gates after the chain-links gate
anchor = "gate('chain 58 whole links at C=%.1f' % CH_C, abs(chain_links(CH_C) - 58.0) < 0.01, round(chain_links(CH_C), 3), 58)"
rep(anchor, anchor + """
def mind(a, b): return asm[a][0].distance_to(asm[b][0])
nut_names = [n for n in asm if n.startswith('beam_') and '_nut' in n and n.endswith('_R')]
d_nut_belt = min(mind(n, 'track_R') for n in nut_names)
gate('beam nuts clear of belt >=25', d_nut_belt >= 25.0, round(d_nut_belt, 1), 25.0)
d_rod = mind('tens_rod_i_R', 'beam_front_flgR')
gate('tension rod clear of front beam flange >=5', d_rod >= 5.0, round(d_rod, 1), 5.0)
kb_ = asm['key0_R'][0].bounding_box(); bo_ = asm['chainwheel_boss_R'][0].bounding_box()
eng_ = min(kb_.max.Y, bo_.max.Y) - max(kb_.min.Y, bo_.min.Y)
gate('chain-wheel key engages the welded boss >=30 mm', eng_ >= 30.0, round(eng_, 1), 30.0)
cwz_ = asm['chainwheel_R'][0].bounding_box().min.Z
gate('chain wheel ground clearance >=35 (info: v2 was 36)', cwz_ >= 35.0, round(cwz_, 1), 35.0)
gate('idler hub inside horn-tip radius (r32.5 < 84.5-10)', 32.5 < (R_in_i - 25.0) - 10.0, 32.5, round(R_in_i - 35.0, 1))""")
open(p, 'w', encoding='utf-8').write(s)
print('patched round 3b')
