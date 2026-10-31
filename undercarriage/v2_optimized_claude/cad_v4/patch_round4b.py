"""Patch round 4b (value-guided weight reduction): upper-band plate windows (3 per plate) + 4 mm drum backplates (recessed 2 mm)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'build_uc_v4.py')
s = open(p, encoding='utf-8').read()
assert 'ROUND4B' not in s

def rep(a, b):
    global s
    assert a in s, 'missing: ' + a[:80]
    s = s.replace(a, b, 1)

# windows: z 210..250 (chord to plate top >=20 mm; >=15 mm above beam-pad bolt holes at z<=192 and UCFL hole top 205 is >88 mm away in x)
rep("            for sx in SPC_X:\n                with Locations((sx, SPC_Z)): Circle(8.5, mode=Mode.SUBTRACT)\n            if inner:",
    "            for wx0, wx1 in ((-300.0, -110.0), (-80.0, 110.0), (140.0, 280.0)):      # ROUND4B windows, webs >= 30 mm\n"
    "                with Locations(((wx0 + wx1) / 2, 230.0)): RectangleRounded(wx1 - wx0, 40.0, 10.0, mode=Mode.SUBTRACT)\n"
    "            for sx in SPC_X:\n                with Locations((sx, SPC_Z)): Circle(8.5, mode=Mode.SUBTRACT)\n            if inner:")
# 4 mm backplates recessed: y 357..361 instead of 355..361
rep("lo, hi = span(355.0, 361.0);   add(f'{tag}_back_{side}', cy(Ri, 32.5 if onepiece else 23.0, lo, hi, xc, zc), 'running')",
    "lo, hi = span(357.0, 361.0);   add(f'{tag}_back_{side}', cy(Ri, 32.5 if onepiece else 23.0, lo, hi, xc, zc), 'running')   # 4 mm, recessed 2 mm (ROUND4B)")
open(p, 'w', encoding='utf-8').write(s)
print('patched round 4b')
