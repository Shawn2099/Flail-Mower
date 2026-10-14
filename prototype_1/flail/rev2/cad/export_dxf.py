"""export_dxf.py - plasma-cut flat patterns for the box-5 enclosure. Units mm.
One DXF per part in cad/dxf/. Convention:
  CUT layer   = finished outline (plasma kerf outside this line)
  PILOT layer = hole-centre crosshairs: plasma-pilot dia-8, then DRILL to size
                (plasma holes come out tapered; bores must be drilled/reamed)
  NOTE layer  = human text (sizes, bends, drill callouts)
Bend lines on the development are on BEND layer (mark, do not cut).
Drill table: M10 clearance = 11 | UCF rotor bore = 52 H8 (bore after drill: hole-saw 50 + ream)
             roller seat = 42 | motor plate holes TO SUIT MOTOR (confirm pattern)
"""
import math, os
import ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "dxf")
os.makedirs(OUT, exist_ok=True)

ZC = 218.0
YROLLC = -210.0 - 45.0 * math.sin(math.radians(50)) - 10.0 - 70.0   # -324.5

def new_doc(name):
    doc = ezdxf.new("R2010")
    doc.layers.add("CUT", color=7)
    doc.layers.add("PILOT", color=1)
    doc.layers.add("BEND", color=3, linetype="DASHED")
    doc.layers.add("NOTE", color=4)
    msp = doc.modelspace()
    return doc, msp

def poly(msp, pts, layer="CUT", close=True):
    msp.add_lwpolyline(pts, dxfattribs={"layer": layer}, close=close)

def pilot(msp, x, y, drill_note=""):
    s = 6.0
    msp.add_line((x - s, y), (x + s, y), dxfattribs={"layer": "PILOT"})
    msp.add_line((x, y - s), (x, y + s), dxfattribs={"layer": "PILOT"})
    msp.add_circle((x, y), 4.0, dxfattribs={"layer": "PILOT"})
    if drill_note:
        msp.add_text(drill_note, dxfattribs={"layer": "NOTE", "height": 5}).set_placement((x + 8, y + 8))

def note(msp, txt, x, y, h=6):
    msp.add_text(txt, dxfattribs={"layer": "NOTE", "height": h}).set_placement((x, y))

def save(doc, name):
    p = os.path.join(OUT, name)
    doc.saveas(p)
    print("WROTE", p)

# ---------------- 1. shell development 867x550 (front 308 + top 330 + rear 229) ----------------
doc, msp = new_doc("shell")
x = 0.0
lengths = [308.3, 330.0, 228.5]
names = ["FRONT (lip at left)", "TOP", "REAR"]
for i, L in enumerate(lengths):
    poly(msp, [(x, 0), (x + L, 0), (x + L, 550), (x, 550)])
    note(msp, names[i], x + 10, 525)
    if i < 2:
        for yy in (0, 550):
            msp.add_line((x + L, yy - 12), (x + L, yy + 12), dxfattribs={"layer": "BEND"})
        note(msp, "BEND ~80deg r>=8", x + L - 60, 260, h=8)
    x += L
note(msp, "4mm MS 867x550. Bend lines 1-2 MARK ONLY. Grain along 550.", 10, -25)
note(msp, "Lip edge (left) deburr; lip bar bolts on later.", 10, -45)
save(doc, "01_shell_development.dxf")

# ---------------- 2. cheek (common L/R, flip) ----------------
doc, msp = new_doc("cheek")
ymin, ymax, zmin, ztop, ch = -406.5, 217.0, 15.0, 413.0, 70.0
poly(msp, [(ymin, zmin), (ymax, zmin), (ymax, ztop - ch), (ymax - ch, ztop),
           (ymin + ch, ztop), (ymin, ztop - ch)])
pilot(msp, 0.0, ZC, "ream 52 H8 (rotor)")
pilot(msp, YROLLC, 70.0, "drill 42 (roller brg)")
for zb in (40.0, 200.0, 340.0):
    for yb in (ymin + 30.0, ymax - 30.0):
        pilot(msp, yb, zb, "")
note(msp, "4mm MS + 4mm doubler at UCF. 12x M10 clr 11 after pilot. SAME P/N both sides (flip).", ymin + 10, -25)
note(msp, "Rotor bore: hole-saw 50 then ream 52. Flatness 0.5.", ymin + 10, -45)
save(doc, "02_cheek.dxf")

# ---------------- 3. counter-knife comb ----------------
doc, msp = new_doc("comb")
poly(msp, [(-250, 0), (250, 0), (250, 40), (-250, 40)])
for k in range(10):
    x0 = -250.0 + k * 50.0 + 5.0
    poly(msp, [(x0, 40), (x0 + 40, 40), (x0 + 40, 70), (x0, 70)])
for xb in (-200, -100, 0, 100, 200):
    pilot(msp, xb, 20, "")
note(msp, "8mm MS comb 500 wide. Teeth up. 5x M10 clr 11 (slots +/-2 at fit-up).", -240, -25)
note(msp, "Grind tooth edges after plasma; tips must clear blade circle by 12.", -240, -45)
save(doc, "03_comb.dxf")

# ---------------- 4. deflector ----------------
doc, msp = new_doc("deflector")
poly(msp, [(-275, 0), (275, 0), (275, 86), (-275, 86)])
for xb in (-200, -100, 100, 200):
    msp.add_lwpolyline([(xb - 4, 20), (xb + 4, 20), (xb + 4, 66), (xb - 4, 66)],
                       dxfattribs={"layer": "PILOT"}, close=True)
note(msp, "MS 4mm 550x86. Slots 8x46 for M10 (adjust +/-4).", -265, -25)
save(doc, "04_deflector.dxf")

# ---------------- 5. skids (2x same) ----------------
doc, msp = new_doc("skid")
poly(msp, [(-140, 0), (140, 0), (140, 90), (-140, 90)])
for yb in (-90, 0, 90):
    msp.add_lwpolyline([(yb - 5.5, 20), (yb + 5.5, 20), (yb + 5.5, 70), (yb - 5.5, 70)],
                       dxfattribs={"layer": "PILOT"}, close=True)
note(msp, "Hardox 6mm 280x90. Vertical slots 11x50 = cut 40-80.", -130, -25)
save(doc, "05_skid.dxf")

# ---------------- 6. motor plate ----------------
doc, msp = new_doc("motorplate")
poly(msp, [(-50, -130), (250, -130), (250, 160), (-50, 160)])
for (xb, yb) in ((30, -80), (170, -80), (30, -40), (170, -40)):
    msp.add_lwpolyline([(xb - 6, yb - 20), (xb + 6, yb - 20), (xb + 6, yb + 20), (xb - 6, yb + 20)],
                       dxfattribs={"layer": "PILOT"}, close=True)
note(msp, "8->6mm MS 300x290. Slots 12x40 for M? motor feet (pattern TO SUIT MOTOR-confirm).", -40, -170)
note(msp, "Slots along Y give +/-15 ratio-change travel.", -40, -190)
save(doc, "06_motorplate.dxf")

# ---------------- 7. guard (cover + 2 sides) ----------------
doc, msp = new_doc("guard")
poly(msp, [(-180, 150), (100, 150), (100, 600), (-180, 600)])
note(msp, "Guard cover 2mm 280x450. Sides: 2x 67x450 same sheet (bend 90).", -170, 120)
save(doc, "07_guard.dxf")

# ---------------- 2b. UCF doubler (2x same) ----------------
doc, msp = new_doc("doubler")
poly(msp, [(-75, -75), (75, -75), (75, 75), (-75, 75)])
pilot(msp, 0.0, 0.0, "52 clear (rotor)")
for (xb, yb) in ((-47.5, -47.5), (47.5, -47.5), (-47.5, 47.5), (47.5, 47.5)):
    pilot(msp, xb, yb, "")
note(msp, "4mm MS 150x150. Centre hole to suit UCF205 spigot; 4 holes to suit flange.", -70, -105)
save(doc, "02b_doubler.dxf")

# ---------------- 8. bend templates (cut from offcut, any thickness) ----------------
doc, msp = new_doc("templates")
import math as _m
for i, ang in enumerate((82, 80)):
    ox = i * 220
    poly(msp, [(ox, 0), (ox + 150, 0)])
    poly(msp, [(ox, 0), (ox + 150 * _m.cos(_m.radians(180 - ang)), 150 * _m.sin(_m.radians(180 - ang)))])
    note(msp, f"TEMPLATE {ang}deg turn (bend {i+1})", ox + 10, -25)
note(msp, "Cut 2x. Bend sheet until panel matches template.", 10, -60)
save(doc, "08_bend_templates.dxf")

print("ALL DXF DONE in", OUT)
