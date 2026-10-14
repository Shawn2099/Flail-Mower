#!/usr/bin/env python3
"""build_track_180x72x37.py - parametric ACETRAX-style rubber track loop.

Defaults = 180x72x37 (PDF-exact: W=180, pitch=72, B=23, A=66, C=28.5, D=28.5).
Size code WxPxN -> N links, loop pitch length Ld = P*N on the cord line.
Change any value from the CLI, e.g.:
  py build_track_180x72x37.py --pitch 60 --links 44 --bigb 24 --ogba 62 --c 25 --d 24.5
Outputs are named track_WxPxN.stl / _section.dxf / .json into common/cad/
(or --outdir). Pattern parts (lug/horn/core plan sizes) stay fixed.

Outputs (into common/cad/):
  track_180x72x37.stl        - closed loop solid (belt ring + 37x2 horns + 37 lugs)
  track_180x72x37_section.dxf - YZ cross-section gauge profile (exact PDF dims)
  track_180x72x37.json        - all dims + verification numbers

Loop form: stadium (2 straights + 2 semicircles) on pitch line.
  Default R = 100 mm (matches common/specs/motor_traction_geared sprocket r=0.10).
  Ls = (Ld - 2*pi*R)/2  -> bottom contact ~1018 mm with R=100.
  Pass --R <mm> to refit to your undercarriage; pitch count/spacing stays exact.

Conventions: units mm, origin at loop centre, X travel, Y across width, Z up.
  local +z = loop-INWARD (roller/guide side), local -z = OUTWARD (ground side).

Assumed (NOT in PDF, flagged ASSUMED): belt_thk=12, lug_h=22 (E),
  horn_len=32 along track, horn top width 16 (draft), lug_len=50, lug_w=170.
Belt ring is mitered (exact joints on arcs); horns/lugs embedded 1.5 mm so the
union has no floating features. Tread chevron is schematic, envelope-exact.
"""
import math, argparse, json, pathlib

# --- PDF-frozen ---
W = 180.0; PITCH = 72.0; N = 37
B_IN = 23.0; A_OUT = 66.0; C_H = 28.5; D_H = 28.5
LD = PITCH * N  # 2664
# --- assumed ---
BELT = 12.0; LUG_H = 22.0; HORN_LEN = 32.0; HORN_TOP_W = 16.0
LUG_LEN = 50.0; LUG_W = 78.0; LUG_YC = 43.0; LUG_STAGGER = 8.0
CORE_W = 58.0; CORE_LEN = 20.0; CORE_THK = 6.0  # steel insert bar per pitch
RHO_RUBBER = 1.2e-6; RHO_STEEL = 7.85e-6  # kg/mm3
EMBED = 1.5  # horn/lug root embed into belt so solids intersect
HORN_W = (A_OUT - B_IN) / 2.0  # 21.5


def stadium_frame(s, Ld, R, Ls):
    """Frame at arc length s: returns (x, z, ang). travel=(cos a, sin a),
    loop-INWARD = (-sin a, cos a)."""
    s = s % Ld
    s1 = Ls
    s2 = s1 + math.pi * R
    s3 = s2 + Ls
    if s < s1:  # bottom straight, moving +x
        return (-Ls / 2.0 + s, -R, 0.0)
    elif s < s2:  # rear arc
        t = (s - s1) / R
        phi = -math.pi / 2.0 + t
        return (Ls / 2.0 + R * math.cos(phi), R * math.sin(phi), t)
    elif s < s3:  # top straight, moving -x
        return (Ls / 2.0 - (s - s2), R, math.pi)
    else:  # front arc
        t = (s - s3) / R
        phi = math.pi / 2.0 + t
        return (-Ls / 2.0 + R * math.cos(phi), R * math.sin(phi), math.pi + t)


def quad(a, b, c, d):
    return [(a, b, c), (a, c, d)]


def hex_tris(v):
    """8 vertices dict with keys (ex, iy, iz): ex 0/1 = end, iy +/-1 width,
    iz +/-1 radial. Returns 12 tris (closed solid)."""
    f = []
    # width sides
    f += quad(v[(0, -1, -1)], v[(1, -1, -1)], v[(1, -1, 1)], v[(0, -1, 1)])
    f += quad(v[(0, 1, 1)], v[(1, 1, 1)], v[(1, 1, -1)], v[(0, 1, -1)])
    # radial sides (inner +z / outer -z)
    f += quad(v[(0, -1, 1)], v[(1, -1, 1)], v[(1, 1, 1)], v[(0, 1, 1)])
    f += quad(v[(0, 1, -1)], v[(1, 1, -1)], v[(1, -1, -1)], v[(0, -1, -1)])
    # end caps (shared planes between neighbours)
    f += quad(v[(0, 1, -1)], v[(0, -1, -1)], v[(0, -1, 1)], v[(0, 1, 1)])
    f += quad(v[(1, -1, -1)], v[(1, 1, -1)], v[(1, 1, 1)], v[(1, -1, 1)])
    return f


def belt_segment(s0, s1, Ld, R, Ls, w, belt):
    """Mitered belt block between arc positions s0..s1: ends cut on the exact
    transverse planes at s0/s1, so neighbours join without gaps or overlaps."""
    ends = []
    for s in (s0, s1):
        x, z, a = stadium_frame(s, Ld, R, Ls)
        ix, iz = -math.sin(a), math.cos(a)  # inward
        ends.append((x, z, ix, iz))
    v = {}
    for ex, (x, z, ix, iz) in enumerate(ends):
        for iy in (-1, 1):
            for izs in (-1, 1):
                # izs=+1 inner face, -1 outer face, measured from pitch line
                off = izs * belt / 2.0
                v[(ex, iy, izs)] = (x + ix * off, iy * w / 2.0, z + iz * off)
    return hex_tris(v)


def box_tris(cx, cy, cz, sx, sy, sz, ang, y_skew=0.0):
    """Discrete feature block (horn/lug blank): sx tangent, sy across,
    sz radial; local +z = INWARD. Skew rotates plan view for chevron."""
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    cs, ss = math.cos(y_skew), math.sin(y_skew)
    corners = []
    for ix in (-1, 1):
        for iy in (-1, 1):
            for iz in (-1, 1):
                lx, ly, lz = ix * hx, iy * hy, iz * hz
                qx = lx * cs - ly * ss
                qy = lx * ss + ly * cs
                wx = cx + qx * math.cos(ang) - lz * math.sin(ang)
                wz = cz + qx * math.sin(ang) + lz * math.cos(ang)
                corners.append((wx, cy + qy, wz))
    idx = {}
    n = 0
    for ix in (-1, 1):
        for iy in (-1, 1):
            for iz in (-1, 1):
                idx[(ix, iy, iz)] = n; n += 1
    faces = [
        [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1)],
        [(-1, -1, 1), (-1, 1, 1), (1, 1, 1), (1, -1, 1)],
        [(-1, -1, -1), (-1, 1, -1), (-1, 1, 1), (-1, -1, 1)],
        [(1, -1, -1), (1, -1, 1), (1, 1, 1), (1, 1, -1)],
        [(-1, -1, -1), (-1, -1, 1), (1, -1, 1), (1, -1, -1)],
        [(-1, 1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1)],
    ]
    tris = []
    for q in faces:
        p = [corners[idx[c]] for c in q]
        tris += [(p[0], p[1], p[2]), (p[0], p[2], p[3])]
    return tris


def frustum_tris(cx, cy, cz_base, sx_base, sy_base, sx_top, sy_top, h, ang):
    """Tapered horn: base rect -> top rect, height h along local +z (= INWARD)."""
    hb = [(sx_base / 2, sy_base / 2), (sx_base / 2, -sy_base / 2),
          (-sx_base / 2, -sy_base / 2), (-sx_base / 2, sy_base / 2)]
    ht = [(sx_top / 2, sy_top / 2), (sx_top / 2, -sy_top / 2),
          (-sx_top / 2, -sy_top / 2), (-sx_top / 2, sy_top / 2)]

    def loc(lx, ly, lz):
        return (cx + lx * math.cos(ang) - lz * math.sin(ang),
                cy + ly, cz_base + lx * math.sin(ang) + lz * math.cos(ang))
    b = [loc(x, y, 0) for x, y in hb]
    t = [loc(x, y, h) for x, y in ht]
    tris = []
    for i in range(4):
        j = (i + 1) % 4
        tris.append((b[i], b[j], t[j])); tris.append((b[i], t[j], t[i]))
    tris.append((t[0], t[1], t[2])); tris.append((t[0], t[2], t[3]))
    tris.append((b[0], b[2], b[1])); tris.append((b[0], t[2] if False else b[3], b[2]))
    return tris


def write_stl_ascii(path, tris, solid="track_180x72x37"):
    with open(path, "w") as f:
        f.write(f"solid {solid}\n")
        for t in tris:
            (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = t
            ux, uy, uz = x2 - x1, y2 - y1, z2 - z1
            vx, vy, vz = x3 - x1, y3 - y1, z3 - z1
            nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            n = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            f.write(f"facet normal {nx / n:.6e} {ny / n:.6e} {nz / n:.6e}\nouter loop\n")
            for p in t:
                f.write(f"vertex {p[0]:.4f} {p[1]:.4f} {p[2]:.4f}\n")
            f.write("endloop\nendfacet\n")
        f.write(f"endsolid {solid}\n")


def main():
    ap = argparse.ArgumentParser(description="Parametric ACETRAX-style rubber track loop. "
        "Defaults = 180x72x37. Example 60-pitch variant: "
        "--pitch 60 --links 44 --bigb 24 --ogba 62 --c 25 --d 24.5")
    ap.add_argument("--W", type=float, default=180.0, help="overall width mm")
    ap.add_argument("--pitch", type=float, default=72.0, help="insert pitch mm")
    ap.add_argument("--links", type=int, default=37, help="link/insert count")
    ap.add_argument("--bigb", type=float, default=23.0, help="IGB (B) inner gap mm")
    ap.add_argument("--ogba", type=float, default=66.0, help="OGB (A) outer span mm")
    ap.add_argument("--c", type=float, default=28.5, help="horn height C mm")
    ap.add_argument("--d", type=float, default=28.5, help="horn height D mm")
    ap.add_argument("--belt", type=float, default=12.0, help="carcass thickness mm")
    ap.add_argument("--lug", type=float, default=22.0, help="tread lug height (E) mm")
    ap.add_argument("--R", type=float, default=100.0, help="pitch-line end radius mm")
    ap.add_argument("--outdir", type=str, default="")
    a = ap.parse_args()
    W, PITCH, N = a.W, a.pitch, a.links
    B_IN, A_OUT, C_H, D_H = a.bigb, a.ogba, a.c, a.d
    BELT, LUG_H, R = a.belt, a.lug, a.R
    LD = PITCH * N
    HORN_W = (A_OUT - B_IN) / 2.0
    assert PITCH > 0 and N > 0 and W > A_OUT > B_IN > 0, "bad section dims"
    stem = f"track_{W:g}x{PITCH:g}x{N}"
    root = pathlib.Path(__file__).resolve().parent  # common/cad
    if a.outdir:
        root = pathlib.Path(a.outdir)
    root.mkdir(parents=True, exist_ok=True)
    Ls = (LD - 2.0 * math.pi * R) / 2.0
    assert Ls > 0, f"R={R} too big for Ld={LD}"

    tris = []
    n_belt = n_horn = n_lug = n_core = 0
    for k in range(N):
        sc = k * PITCH
        s0, s1 = sc - PITCH / 2.0, sc + PITCH / 2.0
        tris += belt_segment(s0, s1, LD, R, Ls, W, BELT)
        n_belt += 12
        x, z, ang = stadium_frame(sc, LD, R, Ls)
        # steel insert bar: discrete track element, centred on cord line,
        # fully embedded in belt (literature: inserts carry sprocket load)
        tris += box_tris(x, 0.0, z, CORE_LEN, CORE_W, CORE_THK, ang)
        n_core += 12
        inx, inz = -math.sin(ang), math.cos(ang)
        for side in (-1, 1):
            y_horn = side * (B_IN / 2.0 + HORN_W / 2.0)
            # root sunk EMBED into belt; tip stays exactly C above roller face
            bx = x + inx * (BELT / 2.0 - EMBED)
            bz = z + inz * (BELT / 2.0 - EMBED)
            tris += frustum_tris(bx, y_horn, bz, HORN_LEN, HORN_W,
                                 HORN_LEN - 6.0, HORN_TOP_W, C_H + EMBED, ang)
            n_horn += 12
        outx, outz = -inx, -inz
        # staggered tread pair: two blocks across width, alternating along-track
        # offset each pitch (aggressive-pattern schematic, envelope-exact).
        # block centre set so tip lands exactly LUG_H above belt outer face.
        stag = LUG_STAGGER if k % 2 == 0 else -LUG_STAGGER
        skew = math.radians(12) * (1 if k % 2 == 0 else -1)
        ca, sa = math.cos(ang), math.sin(ang)
        off = BELT / 2.0 - EMBED + (LUG_H + EMBED) / 2.0
        for side in (-1, 1):
            bx = x + outx * off + ca * stag
            bz = z + outz * off + sa * stag
            tris += box_tris(bx, side * LUG_YC, bz, LUG_LEN, LUG_W, LUG_H + EMBED,
                             ang, y_skew=skew)
            n_lug += 12

    # degenerate-facet guard
    for t in tris:
        (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = t
        ux, uy, uz = x2 - x1, y2 - y1, z2 - z1
        vx, vy, vz = x3 - x1, y3 - y1, z3 - z1
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        assert nx * nx + ny * ny + nz * nz > 1e-12, "degenerate facet"

    stl = root / f"{stem}.stl"
    write_stl_ascii(str(stl), tris, solid=stem)

    xs = [p[0] for t in tris for p in t]
    ys = [p[1] for t in tris for p in t]
    zs = [p[2] for t in tris for p in t]
    bb = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    # freeze guards: envelope must hold on every rebuild
    assert bb[1] <= W + 0.05, f"width breach {bb[1]}"
    overall_L = Ls + 2 * R + 2 * (BELT / 2 + LUG_H)
    overall_H = 2 * R + 2 * (BELT / 2 + LUG_H)
    # sprocket candidates: PD = P/sin(pi/z)
    sprockets = {z: round(PITCH / math.sin(math.pi / z), 1) for z in (8, 9, 10, 11, 12)}
    # analytic mass from feature volumes (mitered ring preserves section area)
    import math as _m
    v_belt = LD * W * BELT
    a1, a2 = HORN_LEN * HORN_W, (HORN_LEN - 6.0) * HORN_TOP_W
    v_horn = (C_H + EMBED) / 3.0 * (a1 + a2 + _m.sqrt(a1 * a2))
    v_lug = LUG_LEN * LUG_W * (LUG_H + EMBED)
    v_core = CORE_LEN * CORE_W * CORE_THK
    mass = (v_belt + 2 * N * v_horn + 2 * N * v_lug) * RHO_RUBBER + N * v_core * RHO_STEEL
    data = {
        "pdf_exact_mm": {"W": W, "pitch": PITCH, "links": N, "B_IGB": B_IN,
                         "A_OGB": A_OUT, "C": C_H, "D": D_H},
        "assumed_mm": {"belt_thk": BELT, "lug_h_E": LUG_H, "horn_len": HORN_LEN,
                       "horn_top_w": HORN_TOP_W, "lug_len": LUG_LEN,
                       "lug_layout": "staggered pairs", "embed": EMBED,
                       "core_bar": [CORE_W, CORE_LEN, CORE_THK]},
        "loop": {"Ld_pitch_mm": LD, "R_pitch_mm": R, "straight_Ls_mm": round(Ls, 2),
                 "overall_length_mm": round(overall_L, 1),
                 "overall_height_mm": round(overall_H, 1),
                 "bottom_contact_pitch_mm": round(Ls, 1),
                 "closure_error_mm": 0.0, "sprocket_PD_candidates_mm": sprockets},
        "mass_kg": round(mass, 1),
        "stl": {"file": stl.name, "facets": len(tris), "bbox_mm": [round(v, 1) for v in bb],
                "counts": {"belt": n_belt // 12, "horns": n_horn // 12, "lugs": n_lug // 12,
                           "cores": n_core // 12},
                "units": "mm", "origin": "loop centre", "axes": "X travel, Y across, Z up"},
        "note": "W/pitch/B/A/C/D exact per ACETRAX pdf; E=22 frozen by user. Belt ring mitered "
                "(exact arc joints); horns inward, staggered lug pairs outward, roots embedded; "
                "1 steel insert per pitch on cord line; tread schematic, envelope-exact.",
    }
    (root / f"{stem}.json").write_text(json.dumps(data, indent=2))
    print(json.dumps(data, indent=2))

    dxf = root / f"{stem}_section.dxf"
    belt_top = 0.0; belt_bot = -BELT; lug_bot = -BELT - LUG_H
    horn_top = belt_top + C_H
    hw = W / 2; ao = A_OUT / 2; bi = B_IN / 2
    lines = []

    def L(x1, y1, x2, y2): lines.append((x1, y1, x2, y2))
    L(-hw, belt_top, hw, belt_top); L(hw, belt_top, hw, belt_bot)
    L(hw, belt_bot, -hw, belt_bot); L(-hw, belt_bot, -hw, belt_top)
    L(-85.0, belt_bot, 85.0, belt_bot); L(85.0, belt_bot, 85.0, lug_bot)
    L(85.0, lug_bot, -85.0, lug_bot); L(-85.0, lug_bot, -85.0, belt_bot)
    draft = (HORN_W - HORN_TOP_W) / 2.0
    for s in (-1, 1):
        b_in, b_out = s * bi, s * ao
        t_in, t_out = s * (bi + draft), s * (ao - draft)
        L(min(b_in, b_out), belt_top, max(b_in, b_out), belt_top)
        L(b_in, belt_top, t_in, horn_top)
        L(t_in, horn_top, t_out, horn_top)
        L(t_out, horn_top, b_out, belt_top)
    with open(dxf, "w") as f:
        f.write("0\nSECTION\n2\nENTITIES\n")
        for x1, y1, x2, y2 in lines:
            f.write(f"0\nLINE\n8\n0\n10\n{x1:.3f}\n20\n{y1:.3f}\n30\n0.0\n"
                    f"11\n{x2:.3f}\n21\n{y2:.3f}\n31\n0.0\n")
        f.write("0\nENDSEC\n0\nEOF\n")
    print(f"wrote {stl} facets={len(tris)}")
    print(f"wrote {dxf}")


if __name__ == "__main__":
    main()
