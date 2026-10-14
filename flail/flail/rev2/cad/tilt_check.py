"""tilt_check.py - deck CG from real CAD volumes + track-width requirement for slope claims.
Run: ..\\.venvs\\build123d\\Scripts\\python.exe cad\\tilt_check.py  (from matlab/)
MASS MODEL: steel 7850 (MS/Hardox), rubber 1200, rotor assy 12.8kg @ (0,0,218),
motor 15kg @ body centre, pack 15kg @ stated assumption. Chassis UNKNOWN -> requirement table.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import build_enclosure_box5 as m

STEEL, RUBBER = 7850.0, 1200.0
steel_parts = ["shell", "cheeks", "roller", "axles", "deflector", "comb", "straps",
               "lipbar", "clamp", "strip_header", "skids", "torque", "gussets",
               "ucf", "motor_plate", "motor_feet", "guard", "guard_sides", "pulleys", "drum", "shaft"]
rubber_parts = ["flap", "strips", "skirts"]

def comps(names):
    tot_m, my, mz = 0.0, 0.0, 0.0
    for n in names:
        obj = getattr(m, n)
        items = obj if isinstance(obj, list) else [obj]
        for p in items:
            b = p.bounding_box()
            v = p.volume / 1e9   # mm3 -> m3
            tot_m += v
            my += v * (b.min.Y + b.max.Y) / 2
            mz += v * (b.min.Z + b.max.Z) / 2
    return tot_m, my / tot_m, mz / tot_m

ms_v, ms_y, ms_z = comps(steel_parts)
mr_v, mr_y, mr_z = comps(rubber_parts)
deck_steel = ms_v * STEEL
deck_rubber = mr_v * RUBBER
print(f"deck steel {deck_steel:.1f} kg @ CG y {ms_y:.0f} z {ms_z:.0f} | rubber {deck_rubber:.1f} kg")

# lumps (kg, y, z). Rotor drum+shaft already in CAD (6.4kg); add blades/tabs/hardware only.
lumps = [(7.1, 0.0, 218.0, "rotor hardware (blades+fins+bolts+discs; drum+shaft in CAD)"), (15.0, -60.0, 511.0, "motor"),
         (8.0, -150.0, 120.0, "pack 48V20Ah low-rear (MVP field pack)")]
M = deck_steel + deck_rubber + sum(l[0] for l in lumps)
Y = (ms_v * STEEL * ms_y + mr_v * RUBBER * mr_y + sum(l[0] * l[1] for l in lumps)) / M
Z = (ms_v * STEEL * ms_z + mr_v * RUBBER * mr_z + sum(l[0] * l[2] for l in lumps)) / M
print(f"deck+mast {M:.1f} kg @ CG y {Y:.0f} z {Z:.0f} (excl. tracked chassis)")

print("\n--- track-width needed for slope angle (SF 1.3 on tip-over) ---")
print("chassis kg @h300 | total CG h | W for 30deg | W for 45deg")
for mc in (80, 120, 160):
    Mt = M + mc
    h = (M * Z + mc * 300.0) / Mt
    import math
    w30 = 2 * h * math.tan(math.radians(30)) * 1.3
    w45 = 2 * h * math.tan(math.radians(45)) * 1.3
    print(f"{mc:11d} | {h:9.0f} mm | {w30:9.0f} mm | {w45:9.0f} mm")
print("Slope parity vs Striker-45 needs ~730mm+ track width: size the tracked chassis to this table.")
