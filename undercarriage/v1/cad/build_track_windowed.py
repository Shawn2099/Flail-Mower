#!/usr/bin/env python3
"""build_track_windowed.py - 180x72x37 with drive windows (rev A).
Copies common/cad/build_track_180x72x37.py geometry, changes:
  R default 100 -> 105.26 (= Rp z9, v1 refit), belt centre band has one
  52x20x12-through window per pitch between inserts (teeth pass-through).
  Side bands full length; centre rungs 20 long carry the inserts.
Outputs: track_180x72x37_windowed.stl/.json (into undercarriage/cad/).
"""
import math, json, pathlib

W, PITCH, N = 180.0, 72.0, 37
B_IN, A_OUT, C_H, D_H = 23.0, 66.0, 28.5, 28.5
BELT, LUG_H = 12.0, 22.0
HORN_LEN, HORN_TOP_W = 32.0, 16.0
LUG_LEN, LUG_W, LUG_YC, LUG_STAGGER = 50.0, 78.0, 43.0, 8.0
CORE_W, CORE_LEN, CORE_THK = 58.0, 20.0, 6.0
EMBED = 1.5
HORN_W = (A_OUT - B_IN) / 2.0
R = 72.0 / math.sin(math.pi / 9) / 2.0   # Rp 105.26
LD = PITCH * N
WIN_LEN, WIN_W = 52.0, 20.0              # frozen realistic (INPUTS.md)
RUNG = PITCH - WIN_LEN                   # 20
RHO_R, RHO_S = 1.2e-6, 7.85e-6

def stadium_frame(s, Ld, R, Ls):
    s = s % Ld
    s1 = Ls; s2 = s1 + math.pi * R; s3 = s2 + Ls
    if s < s1: return (-Ls/2 + s, -R, 0.0)
    elif s < s2:
        t = (s - s1)/R; phi = -math.pi/2 + t
        return (Ls/2 + R*math.cos(phi), R*math.sin(phi), t)
    elif s < s3: return (Ls/2 - (s - s2), R, math.pi)
    else:
        t = (s - s3)/R; phi = math.pi/2 + t
        return (-Ls/2 + R*math.cos(phi), R*math.sin(phi), math.pi + t)

def quad(a,b,c,d): return [(a,b,c),(a,c,d)]
def hex_tris(v):
    f = []
    f += quad(v[(0,-1,-1)],v[(1,-1,-1)],v[(1,-1,1)],v[(0,-1,1)])
    f += quad(v[(0,1,1)],v[(1,1,1)],v[(1,1,-1)],v[(0,1,-1)])
    f += quad(v[(0,-1,1)],v[(1,-1,1)],v[(1,1,1)],v[(0,1,1)])
    f += quad(v[(0,1,-1)],v[(1,1,-1)],v[(1,-1,-1)],v[(0,-1,-1)])
    f += quad(v[(0,1,-1)],v[(0,-1,-1)],v[(0,-1,1)],v[(0,1,1)])
    f += quad(v[(1,-1,-1)],v[(1,1,-1)],v[(1,1,1)],v[(1,-1,1)])
    return f

def belt_span(s0, s1, Ld, R, Ls, y0, y1, belt):
    ends = []
    for s in (s0, s1):
        x, z, a = stadium_frame(s, Ld, R, Ls)
        ends.append((x, z, -math.sin(a), math.cos(a)))
    v = {}
    for ex, (x, z, ix, iz) in enumerate(ends):
        for iy, y in ((-1, y0), (1, y1)):
            for izs in (-1, 1):
                off = izs * belt / 2.0
                v[(ex, iy, izs)] = (x + ix*off, y, z + iz*off)
    return hex_tris(v)

def box_tris(cx, cy, cz, sx, sy, sz, ang, y_skew=0.0):
    hx, hy, hz = sx/2, sy/2, sz/2
    cs, ss = math.cos(y_skew), math.sin(y_skew)
    corners = []
    for ix in (-1,1):
        for iy in (-1,1):
            for iz in (-1,1):
                lx, ly, lz = ix*hx, iy*hy, iz*hz
                qx = lx*cs - ly*ss; qy = lx*ss + ly*cs
                corners.append((cx + qx*math.cos(ang) - lz*math.sin(ang), cy + qy,
                                cz + qx*math.sin(ang) + lz*math.cos(ang)))
    idx = {}
    n = 0
    for ix in (-1,1):
        for iy in (-1,1):
            for iz in (-1,1): idx[(ix,iy,iz)] = n; n += 1
    faces = [[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1)],
             [(-1,-1,1),(-1,1,1),(1,1,1),(1,-1,1)],
             [(-1,-1,-1),(-1,1,-1),(-1,1,1),(-1,-1,1)],
             [(1,-1,-1),(1,-1,1),(1,1,1),(1,1,-1)],
             [(-1,-1,-1),(-1,-1,1),(1,-1,1),(1,-1,-1)],
             [(-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1)]]
    tris = []
    for q in faces:
        p = [corners[idx[c]] for c in q]
        tris += [(p[0],p[1],p[2]),(p[0],p[2],p[3])]
    return tris

def frustum_tris(cx, cy, czb, sxb, syb, sxt, syt, h, ang):
    hb = [(sxb/2,syb/2),(sxb/2,-syb/2),(-sxb/2,-syb/2),(-sxb/2,syb/2)]
    ht = [(sxt/2,syt/2),(sxt/2,-syt/2),(-sxt/2,-syt/2),(-sxt/2,syt/2)]
    def loc(lx,ly,lz): return (cx+lx*math.cos(ang)-lz*math.sin(ang), cy+ly, czb+lx*math.sin(ang)+lz*math.cos(ang))
    b=[loc(x,y,0) for x,y in hb]; t=[loc(x,y,h) for x,y in ht]
    tris=[]
    for i in range(4):
        j=(i+1)%4; tris.append((b[i],b[j],t[j])); tris.append((b[i],t[j],t[i]))
    tris.append((t[0],t[1],t[2])); tris.append((t[0],t[2],t[3]))
    tris.append((b[0],b[2],b[1])); tris.append((b[0],b[3],b[2]))
    return tris

def write_stl(path, tris, solid):
    with open(path,"w") as f:
        f.write(f"solid {solid}\n")
        for t in tris:
            (x1,y1,z1),(x2,y2,z2),(x3,y3,z3)=t
            ux,uy,uz=x2-x1,y2-y1,z2-z1; vx,vy,vz=x3-x1,y3-y1,z3-z1
            nx,ny,nz=uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx
            n=math.sqrt(nx*nx+ny*ny+nz*nz) or 1.0
            f.write(f"facet normal {nx/n:.6e} {ny/n:.6e} {nz/n:.6e}\nouter loop\n")
            for p in t: f.write(f"vertex {p[0]:.4f} {p[1]:.4f} {p[2]:.4f}\n")
            f.write("endloop\nendfacet\n")
        f.write(f"endsolid {solid}\n")

root = pathlib.Path(__file__).resolve().parent
Ls = (LD - 2*math.pi*R)/2
tris=[]; n_band=n_rung=n_horn=n_lug=n_core=0
for k in range(N):
    sc = k*PITCH; s0, s1 = sc-PITCH/2, sc+PITCH/2
    tris += belt_span(s0,s1,LD,R,Ls,-W/2,-WIN_W/2,BELT); n_band+=12
    tris += belt_span(s0,s1,LD,R,Ls,WIN_W/2,W/2,BELT); n_band+=12
    tris += belt_span(sc-RUNG/2,sc+RUNG/2,LD,R,Ls,-WIN_W/2,WIN_W/2,BELT); n_rung+=12
    x,z,ang = stadium_frame(sc,LD,R,Ls)
    tris += box_tris(x,0.0,z,CORE_LEN,CORE_W,CORE_THK,ang); n_core+=12
    inx,inz = -math.sin(ang), math.cos(ang)
    for side in (-1,1):
        yh = side*(B_IN/2+HORN_W/2)
        bx = x+inx*(BELT/2-EMBED); bz = z+inz*(BELT/2-EMBED)
        tris += frustum_tris(bx,yh,bz,HORN_LEN,HORN_W,HORN_LEN-6.0,HORN_TOP_W,C_H+EMBED,ang); n_horn+=12
    outx,outz = -inx,-inz
    stag = LUG_STAGGER if k%2==0 else -LUG_STAGGER
    skew = math.radians(12)*(1 if k%2==0 else -1)
    ca,sa = math.cos(ang), math.sin(ang)
    off = BELT/2-EMBED+(LUG_H+EMBED)/2
    for side in (-1,1):
        bx = x+outx*off+ca*stag; bz = z+outz*off+sa*stag
        tris += box_tris(bx,side*LUG_YC,bz,LUG_LEN,LUG_W,LUG_H+EMBED,ang,y_skew=skew); n_lug+=12

stl = root/"track_180x72x37_windowed.stl"
write_stl(str(stl),tris,"track_180x72x37_windowed")
xs=[p[0] for t in tris for p in t]; ys=[p[1] for t in tris for p in t]; zs=[p[2] for t in tris for p in t]
bb=(max(xs)-min(xs),max(ys)-min(ys),max(zs)-min(zs))
assert bb[1] <= W+0.05
v_belt = (LD*W-(N*WIN_LEN*WIN_W))*BELT
v_horn=(C_H+EMBED)/3*((HORN_LEN*HORN_W)+((HORN_LEN-6)*HORN_TOP_W)+math.sqrt(HORN_LEN*HORN_W*(HORN_LEN-6)*HORN_TOP_W))
v_lug=LUG_LEN*LUG_W*(LUG_H+EMBED); v_core=CORE_LEN*CORE_W*CORE_THK
mass=(v_belt+2*N*v_horn+2*N*v_lug)*RHO_R+N*v_core*RHO_S
data={"track":"180x72x37 revA windowed","W":W,"pitch":PITCH,"links":N,"B":B_IN,"A":A_OUT,"C":C_H,"D":D_H,
 "windows":{"n":N,"len":WIN_LEN,"width":WIN_W,"through":BELT,"corners":"R3 at cut (note for tooling)"},
 "loop":{"Ld":LD,"R":round(R,2),"Ls":round(Ls,1)},"mass_kg":round(mass,1),
 "stl":{"file":stl.name,"facets":len(tris),"bbox":[round(v,1) for v in bb],
 "counts":{"bands":n_band//12,"rungs":n_rung//12,"horns":n_horn//12,"lugs":n_lug//12,"cores":n_core//12}}}
(root/"track_180x72x37_windowed.json").write_text(json.dumps(data,indent=2))
print(json.dumps(data,indent=2))
