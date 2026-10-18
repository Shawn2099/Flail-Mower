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

def roller(D, w, tag, hollow=True, single_brg=True):
    bore, brg_od, brg_w = 25.0, 52.0, 15.0
    n_brg = 1 if single_brg else 2
    if 'idler' in tag:  # v2: laser RINGS D200/ID150 5x8mm + small turned hub (NO big lathe:
        # laser OD +-0.3 is fine on rubber; deburr + flap-disc only; hub dia65 fits any lathe)
        m = 5*(math.pi/4*((D/1000)**2-0.150**2)*0.008*7850) + 1.5 + n_brg*0.13 + 0.2
        proc = "5x 8mm laser rings D200/ID150 + ring-stack hub + Loctite 638, weld stack, NO skim (flap-disc max 1mm), NO ream, 1x6205 press + circlip"
    else:  # v2: pipe shell + laser cheeks + hub
        m_shell = math.pi/4*((D/1000)**2-((D-9)/1000)**2)*(w/1000)*7850
        m = m_shell + 2*(math.pi/4*((D/1000)**2-0.052**2)*0.006*7850) + 0.3 + n_brg*0.13 + 0.2
        proc = "100NB-M shell + 2 laser cheeks + hollow-bar/hub rings + Loctite 638, weld, NO skim, NO ream (clamp shafts), 1x6205 press + circlip"
    data = {"tag": tag, "drum_OD": D, "tread_w": w, "hollow_v2": hollow,
            "bearings": f"{n_brg}x 6205-2RS (25x52x15) sealed",
            "shaft": "dia25 g6 EN8 through-shaft across plates",
            "fits": {"drum_bore": "dia52 H7 (ream)", "circlip": "52x1.5 DIN472",
                     "band_clear": "w40 disc on side bands (170-227/293-350), clears horns A66 + plates ~10"},
            "process": proc,
            "mass_kg": round(m, 2)}
    (root / f"{tag}.json").write_text(json.dumps(data, indent=2))
    # DXF held until CAD freeze (DO_DXF)
    print(tag, json.dumps(data))
    return data

r = roller(114.3, 40.0, "roller_disc_D114_v2")  # 100NB-M shell as-is
i = roller(200.0, 40.0, "idler_disc_D200_v2")
print("wrote v2 hollow single-brg disc JSONs (paired, +-62, w40; DXF after freeze)")
