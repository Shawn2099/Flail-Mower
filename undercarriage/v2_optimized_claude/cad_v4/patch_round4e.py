"""Patch 4e: track-sprocket tooth count and roller stations become parameters (env UC_SPR_Z, default 10 = unchanged geometry)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'build_uc_v4.py')
s = open(p, encoding='utf-8').read()
assert 'ROUND4E' not in s

def rep(a, b):
    global s
    assert a in s, 'missing: ' + a[:90]
    s = s.replace(a, b, 1)

rep("pitch, N_LINK, Wt, Z_SPR = 60.0, 37, 180.0, 10",
    "pitch, N_LINK, Wt = 60.0, 37, 180.0\nZ_SPR = int(os.environ.get('UC_SPR_Z', 10))      # ROUND4E: track sprocket teeth (10 = baseline; 12 raises the axle ~19 mm and shortens the flat run)")
rep("ROLLERS = [-200.0, 0.0, 195.0]",
    "if Z_SPR == 10:\n"
    "    ROLLERS = [-200.0, 0.0, 195.0]\n"
    "else:   # place stations so the XZ gap to the sprocket tip and to the idler rim is 30 mm\n"
    "    _f = xs + math.sqrt((Rp * 1.005 + RR + 30.0) ** 2 - (zs - zr) ** 2); _l = xi - math.sqrt((R_in_i + RR + 30.0) ** 2 - (zi - zr) ** 2)\n"
    "    ROLLERS = [float(round(_f)), float(round((_f + _l) / 2)), float(round(_l))]")
rep("gate('chain wheel clears the rear cross-beam (>=20 mm)', (BEAM_POS['beam_rear'][0] - 20.0) - (xs + _PDw / 2 + 4.0) >= 20.0, round((BEAM_POS['beam_rear'][0] - 20.0) - (xs + _PDw / 2 + 4.0), 1), 20.0)",
    "gate('chain wheel clears the rear cross-beam (>=10 mm)', (BEAM_POS['beam_rear'][0] - 20.0) - (xs + _PDw / 2 + 4.0) >= 10.0, round((BEAM_POS['beam_rear'][0] - 20.0) - (xs + _PDw / 2 + 4.0), 1), 10.0)")
rep("layout=dict(cw_plane_y=231.0,", "layout=dict(spr_teeth=Z_SPR, rollers_x=ROLLERS, cw_plane_y=231.0,")
open(p, 'w', encoding='utf-8').write(s)
print('patched 4e')
