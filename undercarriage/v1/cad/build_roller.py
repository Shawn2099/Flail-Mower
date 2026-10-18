#!/usr/bin/env python3
"""build_roller.py - fab bottom roller D120 + top/idler variant.

Design (easy-fab, common stock): turned drum from 121OD pipe / C45 disc,
2x 6205-2RS (25x52x15, sealed, swappable) on fixed EN8 stub shaft dia25g6,
drum bore 52H7, circlip grooves, 3xM10 flange bolts to side plate.
Roller tread width 60 (< B-adjacent path, clears horns A66/B23, C28.5).
Idler variant D200: same bearings/shaft, wider drum + sliding blocks (built here as params).
Outputs: roller_D120.json + roller.dxf (profile) + idler_D200.json.
"""
import json, math, pathlib
root = pathlib.Path(__file__).resolve().parent

def roller(D, w, tag):
    bore, brg_od, brg_w = 25.0, 52.0, 15.0
    data = {"tag": tag, "drum_OD": D, "tread_w": w,
            "bearings": "2x 6205-2RS (25x52x15) sealed",
            "shaft": "dia25 g6 EN8 fixed stub, M10 flange x3",
            "fits": {"drum_bore": "dia52 H7 (ream)", "circlip": "52x1.5 DIN472",
                     "band_clear": "w40 disc on side bands (170-227/293-350), clears horns A66 + plates ~10"},
            "process": "turn drum OD+crown0.5+bore; ream; fit bearings; loctite+circlips; grease sealed-for-life",
            "mass_kg": round(math.pi/4*((D/1000)**2-0.052**2)*(w/1000)*7850 + 2*0.13 + 0.4, 2)}
    (root / f"{tag}.json").write_text(json.dumps(data, indent=2))
    # profile DXF: half-section (axis horizontal)
    with open(root / f"{tag}.dxf", "w") as f:
        f.write("0\nSECTION\n2\nENTITIES\n")
        R, hw = D/2, w/2
        for x1,y1,x2,y2 in [(-hw,R,hw,R),(hw,R,hw,-R),(hw,-R,-hw,-R),(-hw,-R,-hw,R),
                            (-hw-15,12.5,hw+15,12.5),(-hw-15,-12.5,hw+15,-12.5)]:
            f.write(f"0\nLINE\n8\n0\n10\n{x1:.2f}\n20\n{y1:.2f}\n30\n0.0\n11\n{x2:.2f}\n21\n{y2:.2f}\n31\n0.0\n")
        f.write("0\nTEXT\n8\nNOTES\n10\n-100.0\n20\n-80.0\n30\n0.0\n40\n5.0\n1\n"
                + tag.upper().replace('_',' ') + " - TURN+REAM - 6205-2RS x2 - DIA25 G6 STUB\n")
        f.write("0\nENDSEC\n0\nEOF\n")
    print(tag, json.dumps(data))
    return data

r = roller(120.0, 40.0, "roller_disc_D120")
i = roller(200.0, 40.0, "idler_disc_D200")
print("wrote roller_disc_D120.json/dxf + idler_disc_D200.json/dxf (paired, +-62, w40)")
