"""
freecad_mass_check.py - real mass + CG + tip angles for prototype v0.

The sim (sim_v0_frame.m Q4) ASSUMES a CG height of 155 mm to get its tip angles.
This script computes the CG from the actual CAD geometry plus a table of the
masses that are not modelled, then reports the stability the machine really has.

Run inside FreeCAD, after freecad_build.py:
  exec(open('C:/Users/malliath/Desktop/matlab/prototype_v0/cad/freecad_mass_check.py').read())
"""
import FreeCAD as App
import math

STEEL_KG_M3 = 7850.0
G = 9.81

# Geometry of the frozen layout (mm) - keep in step with build_v0_frame.py
TRACK, WHEELBASE = 420.0, 260.0
X_WHEEL, Y_WHEEL = TRACK / 2, WHEELBASE / 2

# Masses the CAD does not model: (name, kg, x, y, z mm)
#   hub motors + front wheels ARE modelled as solids, so they are given an
#   explicit density instead - see DENSITY_BY_NAME below.
DISCRETE = [
    ("battery 36V 10Ah",  2.50,   0.0,  -60.0, 155.0),
    ("controller + wiring", 1.00, 0.0, -140.0, 155.0),
    ("handle + grips + 2 throttles", 2.20, 0.0, -200.0, 525.0),
    ("775 motor",         0.35,   0.0,    0.0, 108.0),
    ("D50 hub + clamp",   0.15,   0.0,    0.0,  67.5),
    ("2 x M16 nyloc + plain washers", 0.09, 0.0, -130.0, 85.0),   # on the axles
]

# Bought solids that ARE in the model: give them a real mass by density.
#   rear = hub motor 2.30 kg, front = plain wheel 1.50 kg [EST]
BOUGHT_MASS = {"hub_motor": 2.30, "front_wheel": 1.50}


def classify(name):
    if name in ("motor_775", "hub_D50"):
        return "discrete_in_model"
    if name.startswith("wheel_R"):
        return "hub_motor"
    if name.startswith("wheel_F"):
        return "front_wheel"
    # The bought rear-axle stack is drawn so the CAD's clash check covers it.
    # Its mass is already in the numbers above: the O16 stub IS the hub motor's
    # (inside its 2.30 kg) and the nut + washer are one DISCRETE line.
    if name.startswith(("hub_shaft", "axle_nut", "axle_washer")):
        return "axle_hardware"
    return "fabricated"


doc = App.getDocument("prototype_v0")
print("=" * 74)
print(" PROTOTYPE V0 - MASS / CG / STABILITY (from the CAD, not assumed)")
print("=" * 74)

rows = []
for obj in doc.Objects:
    if obj.TypeId != "Part::Feature":
        continue
    sh = obj.Shape
    com = sh.CenterOfMass
    kind = classify(obj.Label)
    vol_m3 = sh.Volume * 1e-9
    if kind == "fabricated":
        m = vol_m3 * STEEL_KG_M3
    elif kind in BOUGHT_MASS:
        m = BOUGHT_MASS[kind]          # wheels: use the real mass, not the solid volume
    else:
        continue                        # 775 + hub: handled in DISCRETE
    rows.append((obj.Label, kind, m, com.x, com.y, com.z))

print(f"\n{'item':<22}{'kind':<16}{'kg':>7}{'x':>8}{'y':>8}{'z':>8}")
for n, k, m, x, y, z in sorted(rows, key=lambda r: -r[2]):
    print(f"{n:<22}{k:<16}{m:7.2f}{x:8.1f}{y:8.1f}{z:8.1f}")

m_steel = sum(r[2] for r in rows if r[1] == "fabricated")
print(f"\nfabricated steel {m_steel:.2f} kg from {sum(1 for r in rows if r[1]=='fabricated')}"
      f" solids (FreeCAD volumes x 7850 kg/m3)")

# ------------------------------------------------------------- combine
items = [(n, m, x, y, z) for n, k, m, x, y, z in rows]
for name, m, x, y, z in DISCRETE:
    items.append((name, m, x, y, z))

M = sum(i[1] for i in items)
cx = sum(i[1] * i[2] for i in items) / M
cy = sum(i[1] * i[3] for i in items) / M
cz = sum(i[1] * i[4] for i in items) / M

print(f"\n{'item':<32}{'kg':>7}{'y':>9}{'z':>9}")
for n, m, x, y, z in sorted(items, key=lambda r: -r[1]):
    print(f"{n:<32}{m:7.2f}{y:9.1f}{z:9.1f}")
print(f"{'TOTAL':<32}{M:7.2f}")
print(f"\nCG = ({cx:+.1f}, {cy:+.1f}, {cz:.1f}) mm   (datum: chassis centre, ground z=0)")

# ------------------------------------------------------------- stability
z_cg = cz
d_fwd = Y_WHEEL - cy           # CG to the front axle line
d_rear = Y_WHEEL + cy          # CG to the rear axle line


def tips(cy_v):
    """Tip angles for a CG Y offset cy_v. Returns lat, fwd, rear, worst."""
    tl = math.degrees(math.atan2(X_WHEEL, cz))
    tf = math.degrees(math.atan2(Y_WHEEL - cy_v, cz))
    tr = math.degrees(math.atan2(Y_WHEEL + cy_v, cz))
    return tl, tf, tr, min(tl, tf, tr)


tip_lat, tip_fwd, tip_rear, worst = tips(cy)

print("\nTIP ANGLES (about the wheel contact rectangle)")
print(f"  lateral            {tip_lat:5.1f} deg   (track/2 {X_WHEEL:.0f} vs CG {z_cg:.0f} high)")
print(f"  longitudinal fwd   {tip_fwd:5.1f} deg   ({d_fwd:.0f} mm to the front axle line)")
print(f"  longitudinal rear  {tip_rear:5.1f} deg   ({d_rear:.0f} mm to the rear axle line)")
worst = min(tip_lat, tip_fwd, tip_rear)
print(f"  WORST              {worst:5.1f} deg")

# ------------------------------------------------------------- vs the sim
SIM_CG, SIM_LAT, SIM_LONG = 155.0, 54.0, 28.0
print("\nAGAINST THE SIM (sim_v0_frame.m Q4: CG 155 mm, 54 lat / worst-long 28 deg)")
print(f"  CG height      CAD {z_cg:.0f} mm  vs sim {SIM_CG:.0f} mm"
      f"   -> sim is {SIM_CG - z_cg:+.0f} mm conservative")
print(f"  lateral        CAD {tip_lat:.0f}  vs sim {SIM_LAT:.0f} deg")
print(f"  longitudinal   CAD {min(tip_fwd, tip_rear):.0f}  vs sim {SIM_LONG:.0f} deg"
      f"   (worst is {'forward' if tip_fwd < tip_rear else 'rearward'})")
ok = worst >= 25.0
print(f"\n  [{'PASS' if ok else 'FAIL'}] worst tip angle {worst:.0f} deg >= 25 deg"
      f"   (working grade is 5 deg)")
if not ok:
    print("         -> ballast the front / move the battery forward / lower the handle")
elif abs(cy) > 20:
    print(f"  [note] the CG sits {abs(cy):.0f} mm {'behind' if cy < 0 else 'ahead of'}"
          f" centre - the hub motors and handle are at the back.")
    print("         Move the battery forward to even the fore-aft balance if you like.")

# --- the cheap fix: slide the battery forward on the deck --------------------
print("\nIF THE BATTERY MOVES (it is the only easily-placed mass on the deck):")
for y_new in (-60.0, 0.0, 40.0):
    cy2 = (sum(i[1]*i[3] for i in items if i[0] != "battery 36V 10Ah")
           + 2.50*y_new) / M
    _, tf2, tr2, w2 = tips(cy2)
    tag = "  <== current" if abs(y_new - (-60.0)) < 1 else (
        "  <== suggested" if abs(y_new - 40.0) < 1 else "")
    print(f"  battery at Y = {y_new:+5.0f} mm -> CG {cy2:+6.1f} mm behind centre, "
          f"worst tip {w2:4.1f} deg{tag}")

# ------------------------------------------------------- mass budget closure
SIM_DESIGN, SIM_MISC = 20.5, 1.00
print("\nMASS BUDGET vs sim_v0_frame.m Q2 (20.5 kg, design 21)")
print(f"  modelled + discrete here   {M:6.2f} kg")
print(f"  + misc the CAD omits       {SIM_MISC:6.2f} kg   (fasteners, wire, throttle cables)")
print(f"  =                          {M + SIM_MISC:6.2f} kg  vs sim {SIM_DESIGN:.2f} kg"
      f"   -> delta {M + SIM_MISC - SIM_DESIGN:+.2f} kg")
budget_ok = abs(M + SIM_MISC - SIM_DESIGN) < 0.25
print(f"  [{'PASS' if budget_ok else 'CHECK'}] the sim's design mass is honest"
      f" (21 kg design is {SIM_DESIGN/21*100:.0f}% of the 21 kg design figure)")
print("=" * 74)
