"""SUPERSEDED by cad_v4/build_uc_v4.py + cad_v4/uc_v4.json (8NB idler, rollers -200/0/195, chain wheel y234-240). Kept for history.
layout_v4.py - layout numbers only (no solids) for 180x60x37 track, gauge 860.
Run: python -I layout_v4.py   -> prints table, writes layout_v4.json
Datum: ground lug tip z=0, X travel, Y across, right side y>0.
Inputs: ACETRAX PDF row 180/60 (IGB24 OGB62 C25 D24.5); 37 links = repo size code (NOT in PDF);
belt 12 + lug E=22 carried over (E frozen by user); idler R = belt-inner radius (Rp-6, as v2).
"""
import json, math
pitch, N, Wt, z = 60.0, 37, 180.0, 10
lug, belt = 22.0, 12.0
Rp = pitch / math.sin(math.pi / z) / 2           # sprocket pitch radius
Ld = pitch * N
C = (Ld - 2 * math.pi * Rp) / 2                   # flat run = centre distance (equal radii)
R_in = Rp - 6.0                                   # belt-inner radius (v2 rule)
zc = lug + belt + R_in                            # axle centre height
xs, xi = -C / 2, C / 2                            # sprocket (rear) / idler (front)
Rr, zr = 57.15, lug + belt + 57.15                # D114.3 roller
gap_min = 25.0
r_first = (Rp + Rr + gap_min)                     # min roller-to-sprocket centre distance
rollers = [-220.0, 0.0, 220.0]
gauge = 860.0; yc = gauge / 2                     # track centre
pl_in, pl_out = yc - 100, yc + 100                # plate centres (v2: track +-100)
plate_half = C / 2 + 120                          # v2: 620 = 500.6 + ~120
out = dict(Rp=Rp, Ld=Ld, C=C, R_in=R_in, zc=zc, xs=xs, xi=xi, zr=zr, rollers=rollers,
           gauge=gauge, plate_in_y=pl_in, plate_out_y=pl_out, plate_half_len=plate_half)
out['roller_sprocket_gap'] = [abs(r - xs) - Rp - Rr for r in rollers]
out['roller_idler_gap'] = [abs(xi - r) - R_in - Rr for r in rollers]
out['roller_spacing_links'] = [(rollers[i + 1] - rollers[i]) / pitch for i in range(2)]
out['v2_roller_x'] = [-300, 0, 300]; out['v2_C'] = 1001.3
# y-stack, right side (mm): UCFL208 housing ~50 wide, flange against plate face
y = {}
y['track_belt'] = (yc - Wt / 2, yc + Wt / 2)
y['plate_in'] = (pl_in - 3, pl_in + 3); y['plate_out'] = (pl_out - 3, pl_out + 3)
y['UCFL_in (inboard of inner plate)'] = (pl_in - 3 - 50, pl_in - 3)
y['UCFL_out (outboard of outer plate)'] = (pl_out + 3, pl_out + 3 + 50)
y['chain_wheel'] = (pl_in - 3 - 50 - 20, pl_in - 3 - 50 - 4)
y['sprocket_laminate'] = (yc - 8, yc + 8)
out['y_stack'] = y
out['overall_width'] = 2 * (pl_out + 3 + 50)
out['axle_len_min'] = (pl_out + 3 + 50) - y['chain_wheel'][0] + 6
v = 0.5; n_out = v / (Rp / 1000) * 60 / (2 * math.pi)
out['sprocket_rpm_at_0.5'] = n_out
out['total_ratio_at_3000rpm'] = 3000 / n_out
out['max_chain_wheel_teeth_08B'] = int(math.pi / math.asin(12.7 / (2 * (zc - 17.5))))  # 17.5 mm ground clearance
json.dump(out, open('layout_v4.json', 'w'), indent=1)
for k, vv in out.items():
    print(k, vv if not isinstance(vv, float) else round(vv, 2))
