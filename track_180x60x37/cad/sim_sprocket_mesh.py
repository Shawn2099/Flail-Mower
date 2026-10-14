#!/usr/bin/env python3
"""sim_sprocket_mesh.py - kinematic mesh check: 72z9 sprocket vs 180x72x37 inserts.

Rigid 2D side-view sweep over one full pitch (40 deg): track pins travel the
tangent-in -> wrap arc (Rp) -> tangent-out path while the sprocket rotates.
ASSUMES windowed belt (windows expose insert flanks; belt rubber absent in the
window zone - required track-builder rev, see SPROCKET_72z9_NOTES.md).
Checks per step: min coast-flank clearance tooth-vs-insert (must stay > 0),
drive-flank contact achieved (min over cycle ~= 0 proves engagement), tooth
count in mesh. Pure python, no dependencies. Exit nonzero on FAIL.
"""
import math, sys

# --- sprocket (must match build_sprocket_72z9.py defaults) ---
Z, P = 9, 72.0
PD = P / math.sin(math.pi / Z)
RP = PD / 2.0
TIP_ABOVE, H = 0.0, 25.0
RTIP, RROOT = RP + TIP_ABOVE, RP + TIP_ABOVE - H
TIP_W, ROOT_W = 22.0, 30.0
# --- track inserts ---
INS_W, INS_T = 20.0, 6.0   # along-track x radial, centred on cord line
SEAT = 1.5  # tension seating: belt pull beds inserts 1.5 into gaps (also covers
            # shop tolerance + thermal); drive flanks stay in contact, tip gap opens

def tooth_poly(tc):
    """Trapezoid with tip-relief chamfers: root-L, chamfer-L, tip-L, tip-R,
    chamfer-R, root-R at tooth centre angle tc (deg). Mirrors the DXF builder."""
    CH = 3.0
    ar = math.degrees((ROOT_W / 2) / RROOT)
    at = math.degrees((TIP_W / 2) / RTIP)
    ac = math.degrees((TIP_W / 2 + CH) / (RTIP - CH))
    def pol(r, d):
        a = math.radians(d)
        return (r * math.cos(a), r * math.sin(a))
    return [pol(RROOT, tc - ar), pol(RTIP - CH, tc - ac), pol(RTIP, tc - at),
            pol(RTIP, tc + at), pol(RTIP - CH, tc + ac), pol(RROOT, tc + ar)]

def seg_dist(p1, p2, p3, p4):
    """Min distance between segments p1p2 and p3p4."""
    def sub(a, b): return (a[0] - b[0], a[1] - b[1])
    def dot(a, b): return a[0] * b[0] + a[1] * b[1]
    d1, d2 = sub(p2, p1), sub(p4, p3)
    r = sub(p1, p3)
    a, e, f = dot(d1, d1), dot(d2, d2), dot(d2, r)
    if a <= 1e-12 and e <= 1e-12:
        return math.hypot(*r)
    if a <= 1e-12:
        s, t = 0.0, max(0.0, min(1.0, f / e))
    elif e <= 1e-12:
        s, t = max(0.0, min(1.0, -dot(d1, r) / a)), 0.0
    else:
        c, b = dot(d1, r), dot(d1, d2)
        den = a * e - b * b
        s = max(0.0, min(1.0, (b * f - c * e) / den)) if abs(den) > 1e-12 else 0.0
        t = (b * s + f) / e
        if t < 0: t, s = 0.0, max(0.0, min(1.0, -c / a))
        elif t > 1: t, s = 1.0, max(0.0, min(1.0, (b - c) / a))
    c1 = (p1[0] + d1[0] * s, p1[1] + d1[1] * s)
    c2 = (p3[0] + d2[0] * s * 0 + d2[0] * t, p3[1] + d2[1] * t)
    return math.hypot(c1[0] - c2[0], c1[1] - c2[1])

def poly_dist(a, b):
    ea = [(a[i], a[(i + 1) % len(a)]) for i in range(len(a))]
    eb = [(b[i], b[(i + 1) % len(b)]) for i in range(len(b))]
    return min(seg_dist(*x, *y) for x in ea for y in eb)

def pin_in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            inside = not inside
    return inside

def penetrates(t, ins):
    return any(pin_in_poly(p, t) for p in ins) or any(pin_in_poly(p, ins) for p in t)

def pin_pose(s):
    """Pin at arc-length s: returns (pos, tangent, outward-normal).
    Path: straight y=+RP (moving +x) -> clockwise half-wrap -> straight y=-RP."""
    if s < 0:
        return ((s, RP), (1.0, 0.0), (0.0, 1.0))
    arc = RP * math.pi
    if s <= arc:
        al = math.pi / 2 - s / RP
        c = (RP * math.cos(al), RP * math.sin(al))
        return (c, (math.sin(al), -math.cos(al)), (math.cos(al), math.sin(al)))
    d = s - arc
    return (((-d, -RP)), (-1.0, 0.0), (0.0, -1.0))

def insert_poly(center, tang, outw):
    hw, ht = INS_W / 2, INS_T / 2
    cx = center[0] - outw[0] * SEAT
    cy = center[1] - outw[1] * SEAT
    pts = []
    for st, sn in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
        pts.append((cx + tang[0] * st * hw + outw[0] * sn * ht,
                    cy + tang[1] * st * hw + outw[1] * sn * ht))
    return pts

def pins_at(phi_deg, delta):
    """All (insert poly) with track-shift delta (seating solve variable).
    Track advances one PITCH per tooth-pass (z*P*n), not Rp*phi."""
    pitch_ang = 360.0 / Z
    s_off = P * (phi_deg / pitch_ang) + delta
    out = []
    for k in range(-3, 8):
        c, tang, outw = pin_pose(k * P - 200.0 + s_off)
        if math.hypot(*c) > RP + 30:
            continue
        out.append(insert_poly(c, tang, outw))
    return out

def step_min(teeth, inss):
    ds = [poly_dist(t, ins) for ins in inss for t in teeth]
    ds.sort()
    return ds

def scan(phi, teeth, dlist):
    """(min_dist, n_pen, delta) scan over shift list; penetration-aware."""
    best = None
    for dd in dlist:
        inss = pins_at(phi, dd)
        ds = [poly_dist(t, ins) for ins in inss for t in teeth]
        pen = sum(1 for t in teeth for ins in inss if penetrates(t, ins))
        m = min(ds)
        key = (pen, -m)
        if best is None or key < best[0]:
            best = (key, dd, m, pen)
    return best[1], best[2], best[3]

def main():
    steps = 80
    pitch_ang = 360.0 / Z
    center_min, loaded_min, n_pen_tot, n_share = 1e9, 1e9, 0, 0
    d_prev = None
    for st in range(steps + 1):
        phi = pitch_ang * st / steps           # sprocket rotation this cycle
        teeth = [tooth_poly(i * pitch_ang + phi) for i in range(Z)]
        # (a) kinematic centering: coarse full-pitch + fine refine (independent per phase)
        coarse = [i * 1.0 for i in range(-36, 37)]
        cc, _, _ = scan(phi, teeth, coarse)
        dl = [cc + i * 0.25 for i in range(-4, 5)]
        dc, mc, _ = scan(phi, teeth, dl)
        # (b) loaded: smallest shift from centred that brings drive flanks to touch
        dl2 = [dc + i * 0.25 for i in range(-80, 81)]
        cands = []
        for dd in dl2:
            inss = pins_at(phi, dd)
            ds = [poly_dist(t, ins) for ins in inss for t in teeth]
            if min(ds) <= 0.5:
                cands.append((abs(dd - dc), dd))
        if cands:
            dl = min(cands)[1]
            touched = True
        else:
            dl, touched = dc, False
        d_prev = dl if touched else dc
        # metrics at loaded timing (or centred if floating)
        inss = pins_at(phi, d_prev)
        pen = sum(1 for t in teeth for ins in inss if penetrates(t, ins))
        n_pen_tot += pen
        ds = step_min(teeth, inss)
        center_min = min(center_min, mc)
        if touched:
            loaded_min = min(loaded_min, min(x for x in ds if x >= 0.3) if any(x >= 0.3 for x in ds) else 0.0)
            n_share = max(n_share, sum(1 for x in ds if x < 1.0))
    print(f"centred clearance min       : {center_min:.3f} mm (kinematic, want > 2)")
    print(f"loaded 2nd-contact min      : {loaded_min:.3f} mm (near-touch = load sharing, expected)")
    print(f"teeth sharing (<=1mm) max   : {n_share} (want >= 2)")
    print(f"true penetrations           : {n_pen_tot} (require 0)")
    ok = n_pen_tot == 0 and center_min > 2.0 and n_share >= 2
    print("MESH " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
