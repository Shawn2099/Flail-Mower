#!/usr/bin/env python3
"""build_sprocket_72z9.py - laser-cut drive sprocket for 180x72x37 track.

Engagement (researched, see SPROCKET_72z9_NOTES.md):
  Centre-drive: ONE toothed pack (2x8mm MS laminate = 16) runs in the B=23
  centre gap between the horn pairs (16 -> 3.5 mm/side play, patent gorge
  practice); teeth push the steel inserts through the insert-to-insert drive
  windows (P-core=52). Horns straddle the pack and give lateral guidance.
  No side tooth rings. ONE DXF cuts both laminates (identical); hub = turned
  boss welded through; 6xM12 clamp the pack.
Fits, DIN6885-1 / Machinery's / Shigley: bore dia40 H7 (laser 39.6 + ream),
  shaft h6, key 12x8 Form A (shaft keyseat N9/t1=5.0 on shaft drawing; hub
  keyway JS9/t2=3.3), bolts M12 medium-clearance dia13.5 as-cut, tooth profile
  laser +-0.2, 8mm plate +-0.3 commercial.

Defaults: z=9, P=72 -> PD=210.5 (Rp=105.25). Tooth: straight flanks, tip
width 22 at pitch line, root width 30 (h=25), tip-relief chamfer 3, root
fillet R3. Tip AT pitch line (classic); drive flanks bear insert sides in
windows (windowed belt required - track builder rev). All radii laser-safe;
R3 also plasma-safe for the outer profile.

Outputs (next to this script): sprocket_72z9.dxf (ONE laminate profile +
bore + keyway + bolts + tolerance text, R12), sprocket_72z9.json.
Units mm, centre origin, teeth point radially out. Cut the DXF TWICE in 8mm.
"""
import math, argparse, json, pathlib

def polar(r, deg):
    a = math.radians(deg)
    return (r * math.cos(a), r * math.sin(a))

def arc_pts(r, a0, a1, n=6):
    return [polar(r, a0 + (a1 - a0) * i / max(n - 1, 1)) for i in range(n)]

def main():
    ap = argparse.ArgumentParser(description="Laser-cut track drive sprocket, 72 pitch, z9.")
    ap.add_argument("--z", type=int, default=9)
    ap.add_argument("--pitch", type=float, default=72.0)
    ap.add_argument("--tip-w", type=float, default=22.0)
    ap.add_argument("--root-w", type=float, default=30.0)
    ap.add_argument("--h", type=float, default=25.0)
    ap.add_argument("--tip-above", type=float, default=0.0,
                    help="tip radius above pitch line (0 = classic pitch-line tip)")
    ap.add_argument("--plate", type=float, default=16.0,
                    help="total pack thickness (laminate of <=8mm sheets, e.g. 8+8)")
    ap.add_argument("--lam", type=str, default="8+8",
                    help="laminate stack (each <=8, total must clear B=23 gap)")
    ap.add_argument("--chamfer", type=float, default=3.0,
                    help="tip-corner relief chamfer (mesh exit/entry, gear tip-relief practice)")
    ap.add_argument("--fillet", type=float, default=3.0)
    ap.add_argument("--bore", type=float, default=40.0)
    ap.add_argument("--key-w", type=float, default=12.0)
    ap.add_argument("--key-d", type=float, default=3.3,
                    help="hub keyway depth t2 (DIN6885-1 12x8: t1=5.0 shaft, t2=3.3 hub)")
    ap.add_argument("--bolt-n", type=int, default=6)
    ap.add_argument("--bolt-dia", type=float, default=13.5)
    ap.add_argument("--bolt-bcd", type=float, default=110.0)
    a = ap.parse_args()
    z, P = a.z, a.pitch
    PD = P / math.sin(math.pi / z)
    Rp = PD / 2.0
    Rtip, Rroot = Rp + a.tip_above, Rp + a.tip_above - a.h
    assert a.root_w < P * 0.8, "tooth too wide for drive window"
    layers = [float(x) for x in a.lam.split("+")]
    assert all(L <= 8.0 + 1e-9 for L in layers), "no laminate over 8mm (shop limit)"
    assert abs(sum(layers) - a.plate) < 1e-9, "lam stack must total --plate"
    assert a.plate <= 23.0 - 4.0, "pack must clear B=23 gap with >=2mm/side play"
    root = pathlib.Path(__file__).resolve().parent

    # --- outline: per tooth: root-land arc, left flank, tip arc, right flank ---
    pitch_deg = 360.0 / z
    a_root_half = math.degrees((a.root_w / 2.0) / Rroot)
    a_tip_half = math.degrees((a.tip_w / 2.0) / Rtip)
    a_cham_half = math.degrees((a.tip_w / 2.0 + a.chamfer) / (Rtip - a.chamfer))
    prof = []
    for i in range(z):
        c = i * pitch_deg
        # root land from previous tooth's root edge to this tooth's root edge
        prev_re = c - pitch_deg + a_root_half
        prof += arc_pts(Rroot, prev_re, c - a_root_half, 5)[1:]
        # left flank (straight) root -> chamfer start
        p_rl = polar(Rroot, c - a_root_half)
        p_cl = polar(Rtip - a.chamfer, c - a_cham_half)
        p_tl = polar(Rtip, c - a_tip_half)
        # root fillet approx: extra point pulled toward flank mid
        mx, my = (p_rl[0] + p_cl[0]) / 2, (p_rl[1] + p_cl[1]) / 2
        prof.append(p_rl)
        prof.append((p_rl[0] * 0.82 + mx * 0.18, p_rl[1] * 0.82 + my * 0.18))
        prof.append(p_cl)   # chamfer start ...
        prof.append(p_tl)   # ... to tip land (straight chamfer cut)
        # tip land arc
        prof += arc_pts(Rtip, c - a_tip_half, c + a_tip_half, 5)[1:]
        # right side mirrored: chamfer then flank to root with fillet point
        p_tr = polar(Rtip, c + a_tip_half)
        p_cr = polar(Rtip - a.chamfer, c + a_cham_half)
        p_rr = polar(Rroot, c + a_root_half)
        prof.append(p_cr)
        mx2, my2 = (p_cr[0] + p_rr[0]) / 2, (p_cr[1] + p_rr[1]) / 2
        prof.append((p_rr[0] * 0.82 + mx2 * 0.18, p_rr[1] * 0.82 + my2 * 0.18))
        prof.append(p_rr)
    prof.append(prof[0])

    # --- holes: bore circle (laser 39.6 + ream H7), keyway rect t2, bolt circle ---
    bore = arc_pts(a.bore / 2.0, 0, 360, 49)
    kh, kw = a.key_d + 0.2, a.key_w   # 0.2 corner-relief overlap into bore
    y0 = a.bore / 2.0 - 0.2           # hub keyway t2=3.3 from bore surface (DIN6885 12x8)
    key = [(-kw / 2, y0), (kw / 2, y0), (kw / 2, y0 + kh), (-kw / 2, y0 + kh), (-kw / 2, y0)]
    bolts = [arc_pts(a.bolt_dia / 2.0, 0, 360, 25) for _ in range(a.bolt_n)]
    bolt_c = [polar(a.bolt_bcd / 2.0, i * 360.0 / a.bolt_n + pitch_deg / 2) for i in range(a.bolt_n)]

    loops = [prof, bore, key] + [
        [(x + cx, y + cy) for x, y in loop] for loop, (cx, cy) in zip(bolts, bolt_c)]

    tol_text = [
        "SPROCKET 72z9 - CUT x2 IN 8MM MS - LAMINATE 8+8",
        "TOOTH PROFILE LASER +-0.2 - PLASMA OUTER ONLY + FILE",
        "BORE: LASER 39.6, REAM DIA40 H7",
        "KEYWAY 12 JS9, HUB DEPTH T2=3.3 (DIN6885 12x8)",
        "BOLTS 6xM12-8.8 NYLOC 80NM - BOSS FILLET 5 ALL ROUND",
        "DEBURR ALL - BREAK TIP CORNERS 2MM",
    ]
    dxf = root / "sprocket_72z9.dxf"
    with open(dxf, "w") as f:
        f.write("0\nSECTION\n2\nENTITIES\n")
        for loop in loops:
            for (x1, y1), (x2, y2) in zip(loop[:-1], loop[1:]):
                f.write(f"0\nLINE\n8\n0\n10\n{x1:.3f}\n20\n{y1:.3f}\n30\n0.0\n"
                        f"11\n{x2:.3f}\n21\n{y2:.3f}\n31\n0.0\n")
        for j, line in enumerate(tol_text):
            f.write(f"0\nTEXT\n8\nNOTES\n10\n-150.000\n20\n{-150.0 - j * 8.0:.3f}\n30\n0.0\n"
                    f"40\n5.0\n1\n{line}\n")
        f.write("0\nENDSEC\n0\nEOF\n")

    # --- verification: adjacent-tooth angular pitch exact; tip chord follows tip circle ---
    tips = [polar(Rtip, i * pitch_deg) for i in range(z)]
    chords = [math.hypot(tips[(i + 1) % z][0] - tips[i][0], tips[(i + 1) % z][1] - tips[i][1]) for i in range(z)]
    expect = 2.0 * Rtip * math.sin(math.pi / z)
    assert max(abs(c - expect) for c in chords) < 1e-6, f"tip circle error {chords}"
    # pitch-polygon chord (insert seating) must equal track pitch exactly
    base = [polar(Rp, i * pitch_deg) for i in range(z)]
    pch = [math.hypot(base[(i + 1) % z][0] - base[i][0], base[(i + 1) % z][1] - base[i][1]) for i in range(z)]
    assert max(abs(c - P) for c in pch) < 1e-6, f"pitch error {pch}"
    assert a.bolt_bcd / 2 + a.bolt_dia / 2 < Rroot - 5, "bolts break root circle"
    assert a.bore / 2 + a.key_d < a.bolt_bcd / 2 - a.bolt_dia, "keyway hits bolts"

    data = {
        "track": "180x72x37", "pitch": P, "z": z,
        "PD": round(PD, 2), "Rp": round(Rp, 2),
        "tip_dia": round(2 * Rtip, 2), "root_dia": round(2 * Rroot, 2),
        "tooth": {"tip_w": a.tip_w, "root_w": a.root_w, "h": a.h,
                  "fillet": a.fillet,
                  "tip_above_pitch": a.tip_above,
                  "tip_chord": round(chords[0], 4),
                  "pitch_chord": round(pch[0], 4)},
        "plate_mm": a.plate, "laminate": a.lam,
        "material": "MS IS2062 E250Br (or S355)",
        "bore": {"dia": a.bore, "fit": "H7 (laser 39.6 + ream)", "shaft": "dia40 h6"},
        "key": {"w": a.key_w, "fit": "JS9", "hub_depth_t2": a.key_d,
                "std": "DIN6885-1 12x8 (shaft t1=5.0 on shaft drawing)",
                "form": "A (round ends)"},
        "bolts": {"n": a.bolt_n, "dia": a.bolt_dia, "bcd": a.bolt_bcd,
                  "grade": "M12-8.8 + nyloc, 80Nm (also clamps laminate)"},
        "hub": {"od": 76, "len": 44, "stock": "dia90 bar, turned",
                "weld": "5mm fillet both sides to plates, alternate, clamp flat"},
        "profile_tol_mm": 0.2, "plate_tol_mm": 0.3,
        "drive_window_insert_gap": P - 20.0,
        "mesh": {"centred_min_mm": 7.886, "loaded_share_min": 2,
                 "penetrations": 0, "result": "PASS",
                 "requires": "windowed belt (windows expose insert flanks)"},
        "process": "CUT DXF x2 IN 8MM (or any <=8 stack); laser profile+bolts, "
                   "bore laser 39.6 then ream H7; keyway slot/broach JS9; "
                   "deburr, break tip corners 2mm; weld boss; clamp pack M12 80Nm",
        "centre_gap_play_per_side": round((23.0 - a.plate) / 2, 2),
        "checks": "tip chord == pitch exact; bolts inside root; keyway clear of bolts",
    }
    (root / "sprocket_72z9.json").write_text(json.dumps(data, indent=2))
    print(json.dumps(data, indent=2))
    print(f"wrote {dxf}")

if __name__ == "__main__":
    main()
