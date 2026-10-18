#!/usr/bin/env python3
"""stl_sprocket_72z9.py - 3D CAD (STL) of the 72z9 sprocket plate + hub.
Profile math mirrors build_sprocket_72z9.py defaults (z9/P72/tip22/root30/
h25/chamfer3/R3, plate 14, bore 40, 6xM13.5 BCD110, hub OD76 L44).
Fan-triangulated extrusion (profile is star-shaped w.r.t. centre); holes as
inner loops. Keyway omitted in STL (present in DXF; cut/wire-cut with bore).
Verifies: closed loops, volume>0, extents; prints analytic mass (MS 7850).
"""
import math, pathlib

Z, P = 9, 72.0
PD = P / math.sin(math.pi / Z)
RP = PD / 2.0
TIP_AB, H, CH = 0.0, 25.0, 3.0
RTIP, RROOT = RP + TIP_AB, RP + TIP_AB - H
TIP_W, ROOT_W = 22.0, 30.0
PLATE, BORE = 16.0, 40.0
BOLT_N, BOLT_D, BOLT_BCD = 6, 13.5, 110.0
HUB_OD, HUB_L = 76.0, 44.0
RHO = 7.85e-6  # kg/mm3

def polar(r, deg):
    a = math.radians(deg)
    return (r * math.cos(a), r * math.sin(a))

def arc_pts(r, a0, a1, n=6):
    return [polar(r, a0 + (a1 - a0) * i / max(n - 1, 1)) for i in range(n)]

def profile():
    pitch = 360.0 / Z
    ar = math.degrees((ROOT_W / 2) / RROOT)
    at = math.degrees((TIP_W / 2) / RTIP)
    ac = math.degrees((TIP_W / 2 + CH) / (RTIP - CH))
    prof = []
    for i in range(Z):
        c = i * pitch
        prof += arc_pts(RROOT, c - pitch + ar, c - ar, 5)[1:]
        p_rl = polar(RROOT, c - ar)
        p_cl = polar(RTIP - CH, c - ac)
        mx, my = (p_rl[0] + p_cl[0]) / 2, (p_rl[1] + p_cl[1]) / 2
        prof += [p_rl, (p_rl[0] * 0.82 + mx * 0.18, p_rl[1] * 0.82 + my * 0.18),
                 p_cl, polar(RTIP, c - at)]
        prof += arc_pts(RTIP, c - at, c + at, 5)[1:]
        p_tr = polar(RTIP, c + at)
        p_cr = polar(RTIP - CH, c + ac)
        p_rr = polar(RROOT, c + ar)
        mx2, my2 = (p_cr[0] + p_rr[0]) / 2, (p_cr[1] + p_rr[1]) / 2
        prof += [p_cr, (p_rr[0] * 0.82 + mx2 * 0.18, p_rr[1] * 0.82 + my2 * 0.18), p_rr]
    return prof

def circle(r, n=48):
    return [polar(r, i * 360.0 / n) for i in range(n)]

def shoelace(loop):
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2)
                   in zip(loop, loop[1:] + loop[:1]))) / 2

def extrude(tris, loop, z0, z1, flip=False):
    n = len(loop)
    for i in range(n):
        x1, y1 = loop[i]
        x2, y2 = loop[(i + 1) % n]
        if not flip:
            tris += [((x1, y1, z0), (x2, y2, z0), (x2, y2, z1)),
                     ((x1, y1, z0), (x2, y2, z1), (x1, y1, z1))]
        else:
            tris += [((x2, y2, z0), (x1, y1, z0), (x2, y2, z1)),
                     ((x2, y2, z1), (x1, y1, z0), (x1, y1, z1))]
    # caps as fan around centroid (loop star-shaped / convex)
    cx = sum(p[0] for p in loop) / n
    cy = sum(p[1] for p in loop) / n
    for i in range(n):
        x1, y1 = loop[i]
        x2, y2 = loop[(i + 1) % n]
        if not flip:
            tris += [((cx, cy, z1), (x1, y1, z1), (x2, y2, z1)),
                     ((cx, cy, z0), (x2, y2, z0), (x1, y1, z0))]
        else:
            tris += [((cx, cy, z1), (x2, y2, z1), (x1, y1, z1)),
                     ((cx, cy, z0), (x1, y1, z0), (x2, y2, z0))]

def main():
    root = pathlib.Path(__file__).resolve().parent
    prof = profile()
    assert abs(max(math.hypot(*p) for p in prof) - RTIP) < 0.01
    bore = circle(BORE / 2)
    bolts = []
    for i in range(BOLT_N):
        cx, cy = polar(BOLT_BCD / 2, i * 360.0 / BOLT_N + 20.0)
        bolts.append([(x + cx, y + cy) for x, y in circle(BOLT_D / 2, 24)])
    tris = []
    z0, z1 = -PLATE / 2, PLATE / 2
    extrude(tris, prof, z0, z1)
    for loop in [bore] + bolts:  # holes: inner loops (flipped winding)
        extrude(tris, loop, z0, z1, flip=True)
    # hub tube
    ho, hi = circle(HUB_OD / 2, 64), circle(BORE / 2, 48)
    extrude(tris, ho, -HUB_L / 2, HUB_L / 2)
    extrude(tris, hi, -HUB_L / 2, HUB_L / 2, flip=True)
    # hub annulus caps
    for j in range(len(ho)):
        a1, a2 = ho[j], ho[(j + 1) % len(ho)]
        b1, b2 = hi[j % len(hi)], hi[(j + 1) % len(hi)]
        tris += [(a1 + (HUB_L / 2,), a2 + (HUB_L / 2,), b2 + (HUB_L / 2,)),
                 (a1 + (HUB_L / 2,), b2 + (HUB_L / 2,), b1 + (HUB_L / 2,))]
    with open(root / "sprocket_72z9.stl", "w") as f:
        f.write("solid sprocket_72z9\n")
        for t in tris:
            (x1, y1, z1a), (x2, y2, z2a), (x3, y3, z3a) = t
                # noqa
            ux, uy, uz = x2 - x1, y2 - y1, z2a - z1a
            vx, vy, vz = x3 - x1, y3 - y1, z3a - z1a
            nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            nn = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            f.write(f"facet normal {nx/nn:.6e} {ny/nn:.6e} {nz/nn:.6e}\nouter loop\n")
            for p in t:
                f.write(f"vertex {p[0]:.4f} {p[1]:.4f} {p[2]:.4f}\n")
            f.write("endloop\nendfacet\n")
        f.write("endsolid sprocket_72z9\n")
    # analytic mass
    a_plate = shoelace(prof) - shoelace(bore) - sum(shoelace(b) for b in bolts)
    a_hub = math.pi * ((HUB_OD / 2) ** 2 - (BORE / 2) ** 2)
    mass = (a_plate * PLATE + a_hub * (HUB_L - PLATE)) * RHO
    xs = [p[0] for p in prof]
    ys = [p[1] for p in prof]
    print(f"facets={len(tris)} bbox={[round(max(xs)-min(xs),1), round(max(ys)-min(ys),1), HUB_L]}")
    print(f"plate_area={a_plate:.0f} hub_area={a_hub:.0f} mass={mass:.2f} kg")
    print("wrote sprocket_72z9.stl")

if __name__ == "__main__":
    main()
