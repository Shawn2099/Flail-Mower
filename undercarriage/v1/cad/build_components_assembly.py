#!/usr/bin/env python3
"""build_components_assembly.py - v1 component STLs + assembly.
Components: side plate, roller D120, idler D200(hollow note), sprocket env,
  axle, cross members, chain wheels, tension screws, plummer env.
Assembly: 2 track stations at y=+-260 + frame/gear positioned (envelope-exact).
Outputs into undercarriage/cad/: plate.stl roller_D120.stl idler_D200.stl
  axle.stl assembly.stl assembly.json
"""
import math, json, pathlib
root = pathlib.Path(__file__).resolve().parent

def box(cx,cy,cz,sx,sy,sz):
    x0,x1,y0,y1,z0,z1=cx-sx/2,cx+sx/2,cy-sy/2,cy+sy/2,cz-sz/2,cz+sz/2
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    q=[(0,1,2,3),(4,6,5,7),(0,4,5,1),(2,6,7,3),(0,3,7,4),(1,5,6,2)]
    return [(v[i],v[j],v[k]) for i,j,k,l in q]+[(v[i],v[k],v[l]) for i,j,k,l in q]

def cyly(cx,cy,cz,d,w,n=12):
    t=[]
    for i in range(n):
        a0,a1=2*math.pi*i/n,2*math.pi*(i+1)/n
        p0=(cx+d/2*math.cos(a0),cy-w/2,cz+d/2*math.sin(a0))
        p1=(cx+d/2*math.cos(a1),cy-w/2,cz+d/2*math.sin(a1))
        q0=(cx+d/2*math.cos(a0),cy+w/2,cz+d/2*math.sin(a0))
        q1=(cx+d/2*math.cos(a1),cy+w/2,cz+d/2*math.sin(a1))
        t+= [(p0,p1,q1),(p0,q1,q0)]
    return t

def cylx(cx,cy,cz,d,w,n=12):  # axis along X (standalone parts only)
    t=[]
    for i in range(n):
        a0,a1=2*math.pi*i/n,2*math.pi*(i+1)/n
        p0=(cx-w/2,cy+d/2*math.cos(a0),cz+d/2*math.sin(a0))
        p1=(cx-w/2,cy+d/2*math.cos(a1),cz+d/2*math.sin(a1))
        q0=(cx+w/2,p0[1],p0[2]); q1=(cx+w/2,p1[1],p1[2])
        t+= [(p0,p1,q1),(p0,q1,q0)]
    return t

def write(path,tris,solid):
    with open(path,"w") as f:
        f.write(f"solid {solid}\n")
        for t in tris:
            (x1,y1,z1),(x2,y2,z2),(x3,y3,z3)=t
            ux,uy,uz=x2-x1,y2-y1,z2-z1; vx,vy,vz=x3-x1,y3-y1,z3-z1
            nx,ny,nz=uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx
            n=math.hypot(nx,ny,nz) or 1.0
            f.write(f"facet normal {nx/n:.4e} {ny/n:.4e} {nz/n:.4e}\nouter loop\n")
            for p in t: f.write(f"vertex {p[0]:.1f} {p[1]:.1f} {p[2]:.1f}\n")
            f.write("endloop\nendfacet\n")
        f.write(f"endsolid {solid}\n")

# dims from frozen v1 (loop-driven datum, ground lug-tip = 0; paired discs + outboard plates)
PLATE_L, PLATE_H, PLATE_T = 1301.8, 190.0, 6.0
PLATE_CZ, PLATE_OFF = 155.0, 100.0
ROLLER_D, ROLLER_W, ROLLER_OFF = 120.0, 40.0, 62.0
IDLER_D, IDLER_W = 200.0, 40.0
SHAFT_D = 25.0
ROLLER_Z = 94.0
AXLE_DIA = 40.0
PD_SPR, RP = 210.51, 105.26
LOOP_CZ = 22.0+6.0+RP   # 133.3
TRACK_Y = 260.0
ROLLER_X = [-300.0, 0.0, 300.0]  # equal 300 spacing (MATLAB clearance 35.3/40.6)
FRONT_X, REAR_X = 500.6, -500.6   # arc centres

write(root/"plate.stl", box(0,0,0,PLATE_L,PLATE_T,PLATE_H), "plate")
write(root/"roller_disc.stl", cyly(0,0,0,ROLLER_D,ROLLER_W)+cyly(0,0,0,52,ROLLER_W+2,8), "rollerdisc")
write(root/"idler_disc.stl", cyly(0,0,0,IDLER_D,IDLER_W)+cyly(0,0,0,52,IDLER_W+2,8), "idlerdisc")
write(root/"shaft_D25.stl", cyly(0,0,0,SHAFT_D,2*PLATE_OFF+20,8), "shaft")
write(root/"sprocket_env.stl", cyly(0,0,0,PD_SPR,16), "sprocket")
write(root/"side_axle.stl", cyly(0,0,0,AXLE_DIA,2*PLATE_OFF+40,10), "sideaxle")

assy=[]
frameL=[]; frameR=[]; centre=[]
for s in (-1,1):
    yc=s*TRACK_Y
    tgt = frameR if s>0 else frameL
    for dy in (-PLATE_OFF,PLATE_OFF):  # plates outboard of track
        tgt+= box(0,yc+dy,PLATE_CZ,PLATE_L,PLATE_T,PLATE_H)
    for rx in ROLLER_X:                # paired discs + shaft per station
        for do in (-ROLLER_OFF,ROLLER_OFF):
            tgt+= cyly(rx,yc+do,ROLLER_Z,ROLLER_D,ROLLER_W)
        tgt+= cyly(rx,yc,ROLLER_Z,SHAFT_D,2*PLATE_OFF+20,8)
    for do in (-ROLLER_OFF,ROLLER_OFF):
        tgt+= cyly(FRONT_X,yc+do,LOOP_CZ,IDLER_D,IDLER_W)
    tgt+= cyly(FRONT_X,yc,LOOP_CZ,SHAFT_D,2*PLATE_OFF+20,8)
    tgt+= cyly(REAR_X,yc,LOOP_CZ,PD_SPR,16)
    tgt+= cyly(REAR_X,yc,LOOP_CZ,AXLE_DIA,2*PLATE_OFF+40,10)
    tgt+= cyly(REAR_X,yc-s*(PLATE_OFF+20),LOOP_CZ,169.9,12)  # 42T inboard
    tgt+= box(FRONT_X+30,yc-PLATE_OFF,LOOP_CZ,90,30,40)
    tgt+= box(FRONT_X+30,yc+PLATE_OFF,LOOP_CZ,90,30,40)
    tgt+= box(REAR_X,yc-PLATE_OFF-10,LOOP_CZ,90,30,60)
    tgt+= box(REAR_X,yc+PLATE_OFF+10,LOOP_CZ,90,30,60)
    for gx in (-150.0,150.0):
        tgt+= box(gx,s*(TRACK_Y-PLATE_OFF),PLATE_CZ,120,40,40)
    parts_note = None
ci = TRACK_Y-PLATE_OFF  # 160
centre+= box(REAR_X,0,200,120,2*ci,50)
centre+= box(FRONT_X,0,110,50,2*ci,40)
centre+= box(-150,0,PLATE_CZ,120,2*ci,40)+box(150,0,PLATE_CZ,120,2*ci,40)
for bs in (-1,1):
    centre+= box(-380,bs*80,330,220,130,220)    # motor per side
    centre+= box(REAR_X,bs*80,210,120,20,180)   # chain guard per side
assy = frameL+frameR+centre
write(root/"assembly.stl", assy, "assembly")
write(root/"frame_L.stl", frameL, "frameL")
write(root/"frame_R.stl", frameR, "frameR")
write(root/"frame_centre.stl", centre, "frame_centre")
info={"assembly":"v1 baseline, 3 sections (L/R/centre bolted, 8xM12 each interface)",
 "sections":{"L":"frame_L.stl (2 plates+spacers+sliders+gussets)","R":"frame_R.stl (mirror)",
  "centre":"frame_centre.stl (axle beam+tie+2 cross+axle+plummers+chain+motor)"},
 "stations":{"track_y":TRACK_Y,"loop_cz":round(LOOP_CZ,1),"roller_x":ROLLER_X,"front":FRONT_X,"rear":REAR_X},
 "components":["plate.stl(x4)+side_plate.dxf","roller_disc x12+shafts dia25","idler_disc x4+shafts",
  "72z9 sprockets x2 + side axles dia40 + UCFL208 x4","42T wheels x2 + 14T pinions + 428 chains x2",
  "motors 2x on centre","track_180x72x37_windowed.stl(x2)"],
 "note":"holes/threads/keys per DXF+JSON (plate 25H7, bore40H7, key12JS9, M10/M12/M16); STL is assembly envelope for clash+viewer"}
(root/"assembly.json").write_text(json.dumps(info,indent=2))
print(json.dumps(info,indent=2))
