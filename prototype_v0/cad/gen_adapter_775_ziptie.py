"""gen_adapter_775_ziptie.py
Adapter for 775 motor, 5 mm round shaft, 15 mm engagement (12+3 stack),
50 mm dia head with 2 opposed top-loading slots for 4.8 mm zip ties.
Slot channel 5.0 wide, head pocket 8.6 wide, floor 2 mm. M4 grub + 2x M3 clamp.
Exports STEP + STL via build123d. All units mm.
"""
from build123d import (
    Solid, Cylinder, Box, Plane, Align,
    Axis, Locations, Pos, Rot,
    export_step, export_stl,
)
import os

OUT = r"C:\Users\malliath\Desktop\matlab\prototype_v0\cad"
os.makedirs(OUT, exist_ok=True)

D_HEAD = 50.0
R_HEAD = D_HEAD / 2
H_HUB = 12.0
H_PLATE = 3.0
D_BORE = 5.05          # 5 mm shaft + clearance
R_BORE = D_BORE / 2
# Zip tie 4.8 mm wide x ~1.3 thick; slot 5.0 wide, open-top notches
W_CHAN = 5.0           # narrow channel tangential width
W_POCKET = 8.6         # tie-head pocket width (head ~7.5)
R_IN = 11.0            # notch inner radius
FLOOR = 2.0            # notch floor thickness from hub bottom
NOTCH_TOP = H_HUB      # open to top
NOTCH_H = NOTCH_TOP - FLOOR   # 10
R_POCKET_OUT = 17.0    # pocket radial extent R_IN..17

def notch_boxes():
    """Return list of (channel, pocket) solids for angle 0 deg (along +X)."""
    # narrow channel: x from R_IN..R_HEAD+0.5 (break through OD), y +-W_CHAN/2, z FLOOR..H_HUB
    chan_len = (R_HEAD + 0.5) - R_IN
    chan = Pos((R_IN + R_HEAD + 0.5) / 2, 0, FLOOR + NOTCH_H / 2) * Box(chan_len, W_CHAN, NOTCH_H)
    # head pocket: x from R_IN..R_POCKET_OUT, wider
    pok_len = R_POCKET_OUT - R_IN
    pok = Pos((R_IN + R_POCKET_OUT) / 2, 0, FLOOR + NOTCH_H / 2) * Box(pok_len, W_POCKET, NOTCH_H)
    return chan, pok

# ---------- HUB ----------
hub = Cylinder(radius=R_HEAD, height=H_HUB, align=(Align.CENTER, Align.CENTER, Align.MIN))
# centre bore (through, +0.5 extra to guarantee cut)
bore = Cylinder(radius=R_BORE, height=H_HUB + 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
hub = hub - bore
# 2 opposed notch sets (0 and 180 deg)
for ang in (0, 180):
    c, p = notch_boxes()
    c = Rot(0, 0, ang) * c
    p = Rot(0, 0, ang) * p
    hub = hub - c - p
# M4 grub tap hole, radial along +Y (90 deg from notches), mid-height z=6
# tap drill 3.3 -> r 1.65, from OD (y=25) to bore; length 24 centred y~13
grub = Pos(0, 13.0, 6.0) * Rot(90, 0, 0) * Cylinder(radius=1.65, height=24.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
hub = hub - grub
# 2x M3 tap holes (drill 2.5 -> r 1.25), depth 8 from top, at (0, +/-18)
for sy in (18.0, -18.0):
    t = Pos(0, sy, H_HUB - 4.0) * Cylinder(radius=1.25, height=8.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    hub = hub - t

# ---------- TOP PLATE ----------
plate = Pos(0, 0, H_HUB) * Cylinder(radius=R_HEAD, height=H_PLATE, align=(Align.CENTER, Align.CENTER, Align.MIN))
plate = plate - Cylinder(radius=R_BORE, height=H_PLATE + 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Pos(0,0,H_HUB-0.5))
for sy in (18.0, -18.0):
    c = Pos(0, sy, H_HUB + H_PLATE / 2) * Cylinder(radius=1.6, height=H_PLATE + 1.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    plate = plate - c

export_step(hub, os.path.join(OUT, "adapter_775_ziptie_hub.step"))
export_step(plate, os.path.join(OUT, "adapter_775_ziptie_plate.step"))
export_stl(hub, os.path.join(OUT, "adapter_775_ziptie_hub.stl"))
export_stl(plate, os.path.join(OUT, "adapter_775_ziptie_plate.stl"))

print("hub  volume mm3:", round(hub.volume, 1), " bbox:", [round(v,2) for v in hub.bounding_box().size])
print("plate volume mm3:", round(plate.volume, 1), " bbox:", [round(v,2) for v in plate.bounding_box().size])
print("saved to", OUT)
print("DIMS: head D50 x hub12 + plate3 = 15 stack; bore 5.05 thru; notches 2x 180deg")
print("  channel W5.0 (tie 4.8 +0.2), pocket W8.6 x radial 6 (11..17), floor 2, open top")
print("  M4 grub radial @90deg mid-height; 2x M3 taps PCD36 (plate clr 3.2)")
print("USE: drop 2 zip ties tail-OUT (70mm), heads in pockets, clamp plate with 2x M3x12, grub M4 on shaft flat")
