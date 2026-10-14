"""weigh.py - per-part mass table for the box-5 deck (run from matlab/)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "cad"))
import build_enclosure_box5 as m

S, R = 7850.0, 1200.0
steel = ["shell", "stiffener", "cheeks", "doublers", "roller", "axles", "deflector",
         "comb", "straps", "lipbar", "clamp", "strip_header", "skids", "torque",
         "gussets", "ucf", "motor_plate", "motor_feet", "guard", "guard_sides",
         "pulleys", "drum", "shaft"]
rubber = ["flap", "strips", "skirts"]
tot = 0.0
for n in steel + rubber:
    o = getattr(m, n)
    items = o if isinstance(o, list) else [o]
    v = sum(p.volume for p in items) / 1e9   # mm3 -> m3
    kg = v * (R if n in rubber else S)
    tot += kg
    print(n.ljust(14), f"{kg:6.2f} kg")
print("TOTAL deck".ljust(14), f"{tot:6.2f} kg")
