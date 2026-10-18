#!/usr/bin/env python3
"""
build_v0_frame.py - prototype v0 chassis (build123d, mm).

Parametric source of truth for the v0 frame. Numbers frozen by
prototype_v0/sim_v0_frame.m (layout, mass, tank turn, turning envelope).

Datum:  ground = 0,  X = across (track),  Y = travel,  Z = up.

Frozen layout (mm)
  wheelbase 260   axle centres at Y = +/-130
  track     420   wheel centres at X = +/-210
  wheels    170 OD x 45 wide, all four the same; rear pair = hub motors
  frame     SHS 25 x 25 x 1.6, UNDERSIDE at Z 104 - lifted 19 mm clear of the
            hub motors' axle stubs, nuts and washers (see the bracket notes).
            Rails at X = +/-160 (inboard of the wheels)
  deck      350 (Y) x 355 (X) x 1.6, top ~146.5 - sits BETWEEN the wheels
  cutter    775 vertical at the centre, 200 mm swath, cut height 25-60
  corners   FOUR identical 6 x 60 x 60 brackets. Front wheels run on O20 stub
            axles in them; the rear pair carry the hub motors' 16 D-shafts.
            No full-width axle, and nothing is notched through a tube.
  mass      ~20.5 kg

Run:  python build_v0_frame.py
Out:  v0_frame.step   fabricated parts
      v0_frame.stl
      v0_layout.step  everything incl. bought wheels + motor (visual check)
      v0_frame_views.svg
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from build123d import (
    Box, Compound, Cylinder, Pos, Rot, export_step, export_stl,
)

OUT = Path(__file__).resolve().parent

# ------------------------------------------------------------------ wheels
TRACK     = 420.0
WHEELBASE = 260.0
WHEEL_OD  = 170.0
WHEEL_W   = 45.0
WHEEL_BORE = 20.6                    # solid-model running clearance over the O20
                                     # front stub axle. The real wheel carries its
                                     # own bearing/bush; the rear pair are the hub
                                     # motors' O16 D-stubs (modelled separately).
R_WHEEL   = WHEEL_OD / 2.0
AXLE_Z    = R_WHEEL                  # 85
X_WHEEL   = TRACK / 2.0              # 210
Y_WHEEL   = WHEELBASE / 2.0          # 130

# ------------------------------------------------------------------ frame
TUBE    = 25.0
WALL    = 1.6
RAIL_X  = 160.0                      # lateral centreline, long rails
RAIL_Y  = Y_WHEEL                    # rails run between the axles
# The frame sits 19 mm ABOVE the axle line. It used to be centred on the axles
# (underside at Z 85 = the axle axis), which buried the hub motors' 57 mm axle
# stubs - and the nut and washer that clamp them - inside the rear cross
# member. Nothing can be notched out of the member there (that is its weld
# line), so the whole frame moves up instead. The deck height is unchanged:
# the tubes rise and the deck posts get SHORTER - see the clearance gates.
FRAME_Z0 = 104.0                     # underside of every frame tube
FRAME_ZC = FRAME_Z0 + TUBE / 2.0     # 116.5 = centreline of every frame tube

# ------------------------------------------------------------------ deck
# 1.6 mm = 16 gauge, the most common Indian sheet thickness. 1.5 is not stock.
# sim_v0_structure.m Q2: SF 11 on a 50 N hand press, 0.79 mm sag.
DECK_X, DECK_Y, DECK_T = 355.0, 350.0, 1.6
DECK_TOP = 146.5
DECK_Z0  = DECK_TOP - DECK_T

# ------------------------------------------------------------------ cutter
HUB_OD, HUB_H = 50.0, 15.0           # printed D50 hub + clamp plate
SWATH         = 200.0
R_TIP         = SWATH / 2.0          # 100
MOTOR_OD      = 44.5
MOTOR_L       = 66.0
CUT_H_MIN, CUT_H_MAX = 25.0, 60.0
MOTOR_Z0 = CUT_H_MAX + HUB_H         # 75  - bottom of can at max cut height
MOTOR_Z1 = MOTOR_Z0 + MOTOR_L        # 141 - top of can
GUARD_OD, GUARD_T = 244.0, 2.5      # 2.5 mm: SF 2.0 vs a 20 g stone at tip speed
                                    # (sim_v0_structure.m Q7). Steel only.
GUARD_Z0, GUARD_Z1 = 15.0, 70.0

# ------------------------------------------------------------------ carrier
# sim_v0_structure.m Q6: the ring OD is not bound by anything - O45.25 bore with
# M5 clamp bolts on R35 only needs OD >= 85. O120 keeps a 37 mm annulus and
# saves 0.35 kg off the old O160. 5 mm stays for M5 thread engagement.
CARRIER_R, CARRIER_T = 60.0, 5.0     # locating ring: bore + 4 x M5 clamp on R35
ARM_W, ARM_L, ARM_Y = 60.0, 95.0, 100.0   # 2 arms: 7.5 mm into the ring (R60) at
                                          # the inner end, 5 mm past the cross member
                                          # outer face (142.5) at the outer end, with
                                          # the M6 hole landing on Y = 130
CARRIER_Z0 = FRAME_Z0 + TUBE        # 129 - sits on top of the cross members
POST_OD, POST_X, POST_Y = 16.0, 160.0, 100.0   # deck posts: SOLID O16 bar, M6 tapped

fails = 0


def gate(name: str, value: float, limit: float, kind: str = "min") -> None:
    """Print a PASS/FAIL clearance gate."""
    global fails
    ok = value >= limit if kind == "min" else value <= limit
    if not ok:
        fails += 1
    word = "PASS" if ok else "FAIL"
    rel = ">=" if kind == "min" else "<="
    print(f"  [{word}] {name:<44} {value:7.1f}  {rel} {limit:6.1f}")


print("=" * 66)
print(" PROTOTYPE V0 - CHASSIS CAD (build123d)")
print("=" * 66)
print(f"\nFROZEN  wheelbase {WHEELBASE:.0f} | track {TRACK:.0f} | "
      f"wheel OD {WHEEL_OD:.0f} x {WHEEL_W:.0f}")
print(f"        frame SHS {TUBE:.0f}x{TUBE:.0f}x{WALL} | rails at X = +/-{RAIL_X:.0f}"
      f" | underside Z {FRAME_Z0:.0f}")
print(f"        deck {DECK_X:.0f} x {DECK_Y:.0f} x {DECK_T} | top {DECK_TOP:.1f}")
print(f"        cutter {SWATH:.0f} swath | cut height {CUT_H_MIN:.0f}-{CUT_H_MAX:.0f}")

# ================================================================== parts
parts: dict[str, object] = {}

# --- frame: 2 long rails + 2 cross members --------------------------------
def shs(axis: str, length: float) -> object:
    """SHS 25x25x1.6 (WALL), open ends, centred on the origin, running along `axis`."""
    inner = TUBE - 2 * WALL
    if axis == "y":
        return Box(TUBE, length, TUBE) - Box(inner, length + 2, inner)
    return Box(length, TUBE, TUBE) - Box(length + 2, inner, inner)


rail = Pos(RAIL_X, 0, FRAME_ZC) * shs("y", 2 * (RAIL_Y - TUBE / 2))
rail_m = Pos(-RAIL_X, 0, FRAME_ZC) * shs("y", 2 * (RAIL_Y - TUBE / 2))
cross_len = 2 * RAIL_X + TUBE
cross_f = Pos(0, Y_WHEEL, FRAME_ZC) * shs("x", cross_len)
cross_r = Pos(0, -Y_WHEEL, FRAME_ZC) * shs("x", cross_len)
parts["rail_L"], parts["rail_R"] = rail_m, rail
parts["cross_F"], parts["cross_R"] = cross_f, cross_r

# --- deck lid (between the wheels) ----------------------------------------
# The deck BOLTS to the 4 posts so it lifts off for service - a welded lid over
# the cutter on a prototype is a decision you regret at the first teardown.
deck = Pos(0, 0, DECK_Z0 + DECK_T / 2) * Box(DECK_X, DECK_Y, DECK_T)
deck -= Pos(0, -140, DECK_Z0 + DECK_T / 2) * Cylinder(10, DECK_T + 4)   # wiring grommet
for sx in (-1, 1):                                    # 4 x M6 into the tapped posts
    for sy in (-1, 1):
        deck -= Pos(sx * POST_X, sy * POST_Y, DECK_Z0 + DECK_T / 2) * \
            Cylinder(3.25, DECK_T + 4)
parts["deck"] = deck

# --- motor carrier: locating ring + 2 arms out to the cross members --------
# A full 240 x 300 x 5 slab weighs 2.8 kg for a job that is only "hold the can",
# so the carrier is a Ø160 ring (bore + clamp bolts) with two 60 mm arms.
carrier = Cylinder(CARRIER_R, CARRIER_T)
carrier -= Cylinder(MOTOR_OD / 2 + 0.25, CARRIER_T + 4)                  # can bore
for k in range(4):                                                       # clamp bolts
    a = math.radians(45 + 90 * k)
    carrier -= Pos(35 * math.cos(a), 35 * math.sin(a), 0) * Cylinder(2.5, CARRIER_T + 4)
for sy in (-1, 1):                                                       # arms
    arm = Box(ARM_W, ARM_L, CARRIER_T)
    arm -= Pos(0, sy * (Y_WHEEL - ARM_Y), 0) * Cylinder(3.25, CARRIER_T + 4)
    carrier += Pos(0, sy * ARM_Y, 0) * arm
carrier = Pos(0, 0, CARRIER_Z0 + CARRIER_T / 2) * carrier
parts["motor_carrier"] = carrier

# --- deck posts: SOLID O16 bar, M6 tapped, 16 mm ---------------------------
# MfD pass: a 20x20x1.6 box welded under a 1.6 mm sheet is the worst weld on the
# machine (thin on thin, and it pulls the deck out of flat). A SOLID bar welds
# to the rail with ONE thick-on-thin fillet and takes an M6 tap, so the deck
# bolts down and comes off. +0.09 kg for a much easier joint.
# sim_v0_structure.m Q3: the load is 60 N - Euler buckling is 3 orders clear.
# Raised frame shortened these from 35 to 16 mm; a 10 mm tap still leaves
# 5.9 mm of bar under the bolt, which is plenty.
post_h = DECK_Z0 - CARRIER_Z0                                          # 15.9
for sx in (-1, 1):
    for sy in (-1, 1):
        p = Cylinder(POST_OD / 2, post_h)
        p -= Pos(0, 0, post_h / 2 - 5.0) * Cylinder(2.5, 10.0)         # M6 tap (10 deep)
        parts[f"post_{'F' if sy > 0 else 'R'}_{'L' if sx < 0 else 'R'}"] = \
            Pos(sx * POST_X, sy * POST_Y, CARRIER_Z0 + post_h / 2) * p

# --- blade / line guard band ----------------------------------------------
gm = (GUARD_Z0 + GUARD_Z1) / 2
band = Pos(0, 0, gm) * (Cylinder(GUARD_OD / 2, GUARD_Z1 - GUARD_Z0) -
                        Cylinder(GUARD_OD / 2 - GUARD_T, GUARD_Z1 - GUARD_Z0 + 2))
parts["guard"] = band

# --- four identical corner brackets + front stub axles ---------------------
# MfD pass (option B). The old front axle was a O20 x 420 rod that had to be
# NOTCHED 320 mm through the front cross member's bottom wall - the hardest
# single operation on the machine, and it destroys the member there.
# Instead: the front wheel runs on a short O20 STUB held in a corner bracket,
# exactly the way the rear hub motor is held. All four corners are the SAME
# 6 x 60 x 60 plate, cut and drilled in one batch. Only the bore differs:
#   front = O20 round bore (our stub, length under our control)
#   rear  = O16.2 bore + a flat at 13.5 across  (the hub motor's 16/13.5 D-shaft)
# The D-flat is what reacts the motor's torque - a plain round hole would let
# the stator spin. The stub is retained by a washer + split pin in a O4 hole.
# The plate's top is flush with the rail top, so it hangs BELOW the raised
# frame - which is what keeps the axle line clear of the cross member.
BR_X0 = RAIL_X + TUBE / 2                 # 172.5 = cross member end face (butt weld)
BR_T, BR_W, BR_H = 6.0, 60.0, 60.0        # 6 mm MS plate (6 clears stress)
BR_ZC = (FRAME_Z0 + TUBE) - BR_H / 2 - AXLE_Z      # +14: plate top flush with rail top
STUB_L, STUB_D = 70.0, 20.0               # O20 MS round bar, bracket face out past the wheel
STUB_X0 = BR_X0                           # stub starts at the bracket's inner face
STUB_BORE = STUB_D / 2 + 0.05             # 0.1 mm running clearance in the model only
SHAFT_D, SHAFT_L, SHAFT_FLAT = 16.0, 57.0, 13.5    # hub motor's D-stub (spec file)
BORE_D = SHAFT_D + 0.2                    # O16.2 bore
FLAT_CLEAR = 0.1                          # the hole's flat clears the shaft's flat
for sx in (-1, 1):
    for sy in (-1, 1):
        tag = f"{'F' if sy > 0 else 'R'}_{'L' if sx < 0 else 'R'}"
        b = Pos(0, 0, BR_ZC) * Box(BR_T, BR_W, BR_H)
        if sy > 0:                                              # front: round bore
            b -= Rot(Y=90) * Cylinder(STUB_BORE, BR_T + 4)
        else:                                                   # rear: D-hole
            # The D-hole is the BORE INTERSECTED WITH THE HALF-PLANE above the
            # flat - not the bore minus a fat box, which would also gouge the
            # plate outside the bore. Bore O16.2, flat at 5.6 from the axis
            # (13.7 across); the shaft's flat sits at 5.5 (13.5 across), so
            # there is 0.1 mm under the flat and 0.1 mm all round the arc.
            zm = SHAFT_FLAT - SHAFT_D / 2 + FLAT_CLEAR           # +5.6
            d = Rot(Y=90) * Cylinder(BORE_D / 2, BR_T + 4)
            d -= Pos(0, 0, zm + 10.0) * Box(BR_T + 4, 40, 20)
            b -= d
        parts[f"bracket_{tag}"] = Pos(sx * (BR_X0 + BR_T / 2), sy * Y_WHEEL, AXLE_Z) * b
    stub = Rot(Y=90) * Cylinder(STUB_D / 2, STUB_L)
    stub -= Pos(STUB_L / 2 - 8.0, 0, 0) * Cylinder(2.0, 20.0)          # O4 split-pin hole
    # The stub butts flush in the bracket bore and is plug-welded on the
    # bracket's inboard face; the washer + split pin outboard keep the wheel on.
    parts[f"stub_{'L' if sx < 0 else 'R'}"] = \
        Pos(sx * (STUB_X0 + STUB_L / 2), Y_WHEEL, AXLE_Z) * stub

# --- guard mounting tabs ---------------------------------------------------
# The guard is not left floating: 2 tabs, cut from the SAME 2.5 mm strip as the
# band (so the weld to the rim is same-thickness), reach UP from the band's top
# rim to the cross member's underside. That was 15 mm with the old frame; with
# the frame lifted it is 34 mm. They are what stops the guard swinging.
TAB_W, TAB_T, TAB_L = 30.0, 2.5, FRAME_Z0 - GUARD_Z1
for sy in (-1, 1):
    parts[f"guard_tab_{'F' if sy > 0 else 'R'}"] = \
        Pos(0, sy * (GUARD_OD / 2), GUARD_Z1 + TAB_L / 2) * Box(TAB_W, TAB_T, TAB_L)

# --- bought parts (visual only) -------------------------------------------
bought: dict[str, object] = {}
for sx in (-1, 1):
    for sy in (-1, 1):
        # bored for the dead axle / hub-motor shaft (the wheel spins on it)
        w = Rot(Y=90) * (Cylinder(R_WHEEL, WHEEL_W) - Cylinder(WHEEL_BORE / 2, WHEEL_W + 2))
        bought[f"wheel_{'F' if sy > 0 else 'R'}_{'L' if sx < 0 else 'R'}"] = \
            Pos(sx * X_WHEEL, sy * Y_WHEEL, AXLE_Z) * w
bought["motor_775"] = Pos(0, 0, (MOTOR_Z0 + MOTOR_Z1) / 2) * Cylinder(MOTOR_OD / 2, MOTOR_L)
bought["hub_D50"] = Pos(0, 0, CUT_H_MAX + HUB_H / 2) * Cylinder(HUB_OD / 2, HUB_H)

# --- the bought REAR AXLE STACK, drawn so the clash check can see it -------
# This is the geometry that forced the frame up. The hub motor is the wheel and
# its own O16 x 57 D-stub is the axle; a plain washer and an M16 nyloc clamp the
# corner bracket onto it. Modelling all three means freecad_build.py's all-pairs
# volume check covers them from now on - the original clash (stub + nut + washer
# buried inside the rear cross member) was invisible because none of it was in
# the model. These are BOUGHT parts: they are excluded from the fabricated-steel
# mass, and freecad_mass_check.py skips them.
WHEEL_IN = X_WHEEL - WHEEL_W / 2.0                 # 187.5 = inboard tyre face
WASHER_OD, WASHER_T = 30.0, 2.0                    # plain M16 washer
NUT_ACROSS, NUT_H = 27.8, 13.0                     # M16 nyloc, across corners
for sx in (-1, 1):
    tag = 'L' if sx < 0 else 'R'
    sh = Rot(Y=90) * Cylinder(SHAFT_D / 2, SHAFT_L)
    sh -= Pos(0, 0, SHAFT_FLAT - SHAFT_D / 2 + 10.0) * \
        Box(SHAFT_L + 4, SHAFT_D + 4, 20)          # the D-flat, 13.5 across
    bought[f"hub_shaft_{tag}"] = \
        Pos(sx * (WHEEL_IN - SHAFT_L / 2), -Y_WHEEL, AXLE_Z) * sh
    wa = Rot(Y=90) * (Cylinder(WASHER_OD / 2, WASHER_T) - Cylinder(8.5, WASHER_T + 2))
    bought[f"axle_washer_{tag}"] = \
        Pos(sx * (BR_X0 - WASHER_T / 2), -Y_WHEEL, AXLE_Z) * wa
    nu = Rot(Y=90) * (Cylinder(NUT_ACROSS / 2, NUT_H) - Cylinder(BORE_D / 2, NUT_H + 2))
    bought[f"axle_nut_{tag}"] = \
        Pos(sx * (BR_X0 - WASHER_T - NUT_H / 2), -Y_WHEEL, AXLE_Z) * nu

# ================================================================== checks
print("\nCLEARANCE GATES")
r_corner = math.hypot(X_WHEEL, Y_WHEEL)
gate("rail outer face -> wheel inner face", (X_WHEEL - WHEEL_W / 2) - (RAIL_X + TUBE / 2), 5.0)
gate("deck edge -> wheel inner face", (X_WHEEL - WHEEL_W / 2) - DECK_X / 2, 5.0)
gate("line tip -> nearest wheel surface", r_corner - R_WHEEL - R_TIP, 20.0)
gate("guard OD -> nearest wheel surface", r_corner - R_WHEEL - GUARD_OD / 2, 8.0)
gate("motor top -> deck underside", DECK_Z0 - MOTOR_Z1, 1.0)
gate("hub top -> motor can bottom (contact)", MOTOR_Z0 - (CUT_H_MAX + HUB_H), 0.0)
gate("deck top -> wheel top (wheels poke above by)", (AXLE_Z + R_WHEEL) - DECK_TOP, 0.0)
gate("carrier edge -> wheel inner face", (X_WHEEL - WHEEL_W / 2) - CARRIER_R, 5.0)
gate("carrier top -> deck underside", DECK_Z0 - (CARRIER_Z0 + CARRIER_T), 5.0)
gate("motor can OD -> carrier bore (grip)", 2 * (MOTOR_OD / 2 + 0.25) - MOTOR_OD, 0.2)
gate("hub bottom -> ground at min cut height", CUT_H_MIN - HUB_H, 5.0)
gate("corner bracket -> wheel inner face", (X_WHEEL - WHEEL_W / 2) - (BR_X0 + BR_T), 5.0)
gate("front stub overhang past the wheel (pin room)",
     (STUB_X0 + STUB_L) - (X_WHEEL + WHEEL_W / 2), 5.0)
gate("guard top rim -> cross member underside", FRAME_Z0 - GUARD_Z1, 5.0)
gate("deck post length (room for the M6 tap)", post_h, 12.0)
# --- why the frame sits at Z 104: clear the WHOLE bought axle stack ---------
gate("hub motor stub -> frame underside", FRAME_Z0 - (AXLE_Z + SHAFT_D / 2), 5.0)
gate("axle nut envelope -> frame underside", FRAME_Z0 - (AXLE_Z + NUT_ACROSS / 2), 3.0)
gate("axle washer -> frame underside", FRAME_Z0 - (AXLE_Z + WASHER_OD / 2), 3.0)
gate("front stub top -> frame underside", FRAME_Z0 - (AXLE_Z + STUB_D / 2), 5.0)

r_sweep = r_corner + R_WHEEL
print(f"\nTURNING  corner radius {r_corner:.0f} mm -> swept circle {2 * r_sweep:.0f} mm dia")

print("\nCUT LIST (all MS 25x25x1.6 SHS except the sheets)")
print(f"  2 x long rail    {2 * (RAIL_Y - TUBE / 2):.0f} mm   (at X = +/-{RAIL_X:.0f}, "
      f"butting the cross members)")
print(f"  2 x cross member {cross_len:.0f} mm   (at Y = +/-{Y_WHEEL:.0f})")
print(f"  2 x handle leg   790 mm + 1 brace 300 mm   (not modelled yet - open item 6)")
print(f"  deck sheet       {DECK_X:.0f} x {DECK_Y:.0f} x {DECK_T} mm, 4 x O6.5 bolt holes")
print(f"  carrier plate    ring OD {2 * CARRIER_R:.0f} x {CARRIER_T} + 2 arms "
      f"{ARM_W:.0f} x {ARM_L:.0f}, bore {MOTOR_OD:.1f} + 4 x M5 on R35")
print(f"  guard band       OD {GUARD_OD:.0f} x {GUARD_Z1 - GUARD_Z0:.0f} tall x {GUARD_T} mm "
      f"+ 2 x {TAB_W:.0f}x{TAB_L:.0f} mount tabs from the same strip")
print(f"  4 x corner brkt  MS plate {BR_T:.0f} x {BR_W:.0f} x {BR_H:.0f}   (ONE part; front O20 bore,")
print(f"                     rear O16.2 bore + a flat) - cut + drilled in one batch")
print(f"  2 x front stub   MS O20 round bar x {STUB_L:.0f} mm + a O4 split-pin hole")
print(f"  4 x deck post    MS O16 round bar x {post_h:.0f} mm, M6 tapped 10 deep")
print(f"  bought axle kit  hub motor's own O16 x {SHAFT_L:.0f} D-stub + M16 nyloc + O30 washer")

# ================================================================== mass
# Real volumes off the solids (the tubes are hollow, so this is a true mass).
STEEL = 7850.0            # kg/m3
DENSITY = {"fabricated": STEEL, "bought": None}
tube_len_m = 2 * (2 * (RAIL_Y - TUBE / 2)) / 1000.0 + 2 * cross_len / 1000.0
vol_tube = sum(s.volume for s in (rail, rail_m, cross_f, cross_r))
m_tube = vol_tube * STEEL * 1e-9
m_fab = sum(sh.volume for sh in parts.values()) * STEEL * 1e-9
m_sim_fab = 3.2 + 2.2 + 0.30         # sim_v0_frame.m: k_frame + k_lid + m_misc
print("\nMASS (from CAD volumes)")
print(f"  4 frame tubes (hollow)          {m_tube:6.2f} kg"
      f"   [{m_tube / tube_len_m:.2f} kg/m over {tube_len_m:.2f} m;"
      f" 25x25x1.6 SHS tables say 1.12]")
print(f"  all fabricated steel            {m_fab:6.2f} kg")
print(f"  sim assumed (frame+lid+misc)    {m_sim_fab:6.2f} kg"
      f"   -> delta {m_fab - m_sim_fab:+.2f} kg")

# ---------------------------------------------------------- parts manifest
manifest = []
for group, table in (("fabricated", parts), ("bought", bought)):
    for name, sh in table.items():
        bb = sh.bounding_box()
        manifest.append({
            "name": name, "group": group,
            "bbox_min": [round(bb.min.X, 4), round(bb.min.Y, 4), round(bb.min.Z, 4)],
            "bbox_max": [round(bb.max.X, 4), round(bb.max.Y, 4), round(bb.max.Z, 4)],
            "volume_mm3": round(sh.volume, 3),
            "density_kg_m3": DENSITY[group],
        })
(OUT / "v0_parts.json").write_text(
    json.dumps({"units": "mm", "n_parts": len(manifest), "parts": manifest}, indent=1))
print(f"\nwrote v0_parts.json  ({len(manifest)} parts)")

# ================================================================== export
# Two OCCT/build123d traps hit here, both verified:
#  * Compound(children=...) re-parents the shapes, so building the layout
#    compound before exporting the fab compound made the STEP writer emit
#    1 of 14 solids. Export each compound immediately after building it.
#  * write_pcurves=False; the default writer drops solids sharing coincident
#    faces (frame tubes butt into each other).
export_step(Compound(children=list(parts.values())),
            str(OUT / "v0_frame.step"), write_pcurves=False)
export_stl(Compound(children=list(parts.values())), str(OUT / "v0_frame.stl"))
asm = Compound(children=list(parts.values()) + list(bought.values()))
export_step(asm, str(OUT / "v0_layout.step"), write_pcurves=False)

try:
    from build123d import ExportSVG
    views = []
    for name, origin, up in (("top", (0, 0, 3000), (0, 1, 0)),
                             ("front", (0, -3000, 0), (0, 0, 1)),
                             ("side", (3000, 0, 0), (0, 0, 1))):
        vis, _ = asm.project_to_viewport(origin, up)
        if not len(vis):                          # OCCT HLR projects NOTHING when
            vis, _ = asm.project_to_viewport(     # the eye sits exactly on an
                tuple(v + 0.1 for v in origin), up)   # axis. Nudge it 0.002 deg.
        if len(vis):
            views.append((name, vis))
    if not views:
        raise RuntimeError("no view projected")
    placed, x, GAP = [], 0.0, 80.0
    for name, vis in views:                       # lay the views out left to right
        if not hasattr(vis, "bounding_box"):      # project_to_viewport -> ShapeList
            vis = Compound(children=list(vis))
        bb = vis.bounding_box()
        placed.append(Pos(x - bb.min.X, -bb.min.Y, 0) * vis)
        x += (bb.max.X - bb.min.X) + GAP
    svg = ExportSVG(scale=0.28)
    svg.add_layer("visible", line_weight=0.35)
    svg.add_shape(Compound(children=placed), layer="visible")
    svg.write(str(OUT / "v0_frame_views.svg"))
    print(f"\nwrote v0_frame_views.svg  ({' | '.join(n for n, _ in views)})")
except Exception as exc:                                  # never fatal
    print(f"\n(SVG view export skipped: {exc})")

# ---------------------------------------------------------------- verify
from build123d import import_step
back = import_step(str(OUT / "v0_frame.step"))
n_solids = len(back.solids())
bb = back.bounding_box()
print(f"re-imported v0_frame.step: {n_solids} solids, "
      f"{bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")
fails += 0 if n_solids == len(parts) else 1
print(f"  [{'PASS' if n_solids == len(parts) else 'FAIL'}] "
      f"solid count {n_solids} == part count {len(parts)}")

print(f"\nwrote v0_frame.step / v0_frame.stl / v0_layout.step")
print(f"RESULT: {'all gates PASS' if fails == 0 else f'{fails} gate(s) failed'}")
print("=" * 66)
