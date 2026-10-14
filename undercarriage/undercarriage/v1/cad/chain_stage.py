#!/usr/bin/env python3
"""chain_stage.py - v1 chain second stage (gearbox-output assumption).
G=3: motor 14T -> axle 42T, 428 bike chain (p12.7), centres slotted +-15.
42T PD = 12.7/sin(pi/42) = 169.9, r85. Axle T 80Nm/side -> pull ~1.9kN.
Outputs: chain_stage.json
"""
import json, math, pathlib
root = pathlib.Path(__file__).resolve().parent
p = 12.7
z1, z2 = 14, 42
pd1 = p / math.sin(math.pi / z1)
pd2 = p / math.sin(math.pi / z2)
G = z2 / z1
centre = 300.0  # nominal, slotted +-15 for chain tension
data = {"chain": "428 (bike, common stock)", "pitch": p, "pinion_T": z1,
        "wheel_T": z2, "ratio": G, "PD1": round(pd1, 1), "PD2": round(pd2, 1),
        "centre_nom": centre, "centre_slot": "+-15 (chain tension, separate from track screws)",
        "pull_80Nm": round(2 * 80 / (pd2 / 2 / 1000)), "tensile_N": 20000,
        "result": "PASS margin >10", "guard": "2mm MS cover both runs + sides, vented",
        "motor": "1.2kW preferred (margin), 1kW OK; same keyway; slotted motor plate"}
(root / "chain_stage.json").write_text(json.dumps(data, indent=2))
print(json.dumps(data, indent=2))
