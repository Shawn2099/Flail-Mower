#!/usr/bin/env python3
"""mass_audit.py - v2 as-drawn mass rollup.

Fab parts are measured from the STEP solids (density 7850 kg/m3). Bought
parts use catalogue/estimate masses. Run after any CAD change; sim_v2.m
reads mass_audit.json so the sim mass gate tracks the CAD, not a hand list.

Outputs: mass_audit.json, MASS.md
"""
import json, pathlib
from build123d import import_step

ROOT = pathlib.Path(__file__).resolve().parent
RHO = 7850e-9  # kg/mm3

# part key -> (step file, qty, category)
FAB = {
    "side plate 1240x220x6": ("side_plate.step", 4, "structure"),
    "roller drum v3 (pipe+backplate+seat)": ("v3_roller_drum.step", 12, "running"),
    "idler drum v3 (pipe+backplate+seat)": ("v3_idler_drum.step", 4, "running"),
    "spacer 42.4/35.5x109": ("v3_spacer.step", 8, "running"),
    "shaft D25x260": ("shaft_D25_L260.step", 8, "running"),
    "collar D25": ("collar_D25.step", 16, "running"),
    "washer D25/OD50": ("washer_D25_OD50.step", 8, "running"),
    "pin D6x40": ("pin_D6_L40.step", 8, "running"),
    "side axle D40x300": ("side_axle.step", 2, "drive"),
    "collar D40 OD60": ("collar_D40_OD60.step", 4, "drive"),
    "sprocket 72z9 8mm": ("sprocket_72z9.step", 4, "drive"),
    "hub 76/42 stack": ("hub76_OD76.step", 2, "drive"),
    "beam SHS40 L320": ("beam_SHS40.step", 4, "structure"),
    "rail SHS40 L300": ("rail_SHS40_L300.step", 4, "structure"),
    "flange mid 140x70x8": ("flange_mid_140x70x8.step", 6, "structure"),
    "flange front 50x70x8": ("flange_front_50x70x8.step", 2, "structure"),
    "deck mount 80x80x20": ("deck_mount.step", 4, "structure"),
    "lift lug": ("lift_lug.step", 2, "structure"),
    "chain guard 1.5mm": ("chain_guard.step", 2, "drive"),
    "tension lug": ("tension_lug.step", 4, "drive"),
    "tension rod M12": ("tension_rod_M12.step", 4, "drive"),
    "rod eye": ("rod_eye.step", 4, "drive"),
    "spacer tube 48x3.2x200": (None, 4, "structure"),
}
# bought / not modelled as final solids
COTS = {
    "6205-2RS": (16, 0.13, "running"),
    "48T chainwheel (adapted)": (2, 1.60, "drive"),
    "UCFL208": (4, 2.20, "drive"),
    "motor 1.2 kW + gearbox": (2, 9.00, "drive"),
    "428 chain (60L)": (2, 0.80, "drive"),
    "track 180x72x37": (2, 18.00, "track"),
    "M12 nut (tension)": (8, 0.022, "misc"),
    "fasteners/paint/misc": (1, 1.82, "misc"),
}

items = []
for name, (f, qty, cat) in FAB.items():
    if f is None:
        unit = 2.84 / 4          # 48.3 x 3.2 tube, 200 long
    else:
        unit = import_step(str(ROOT / f)).volume * RHO
        if "SHS40 L320" in name:
            unit *= 320 / 314          # STEP is 314; cut length 320
    items.append(dict(part=name, qty=qty, unit_kg=round(unit, 3),
                      mass_kg=round(unit * qty, 2), category=cat,
                      source=f or "calculated"))
for name, (qty, unit, cat) in COTS.items():
    items.append(dict(part=name, qty=qty, unit_kg=unit,
                      mass_kg=round(unit * qty, 2), category=cat,
                      source="COTS/catalogue"))

cats = {}
for it in items:
    cats[it["category"]] = round(cats.get(it["category"], 0) + it["mass_kg"], 1)
total = round(sum(it["mass_kg"] for it in items), 1)

out = dict(title="UC-V2 as-drawn mass rollup", density_kg_m3=7850,
           note="Fab parts measured from STEP; bought parts catalogue/estimate.",
           items=items, category_kg=cats, total_kg=total,
           target_kg=165, delta_kg=round(total - 165, 1))
(ROOT / "mass_audit.json").write_text(json.dumps(out, indent=2))

lines = ["# UC-V2 MASS ROLLUP (as drawn)", "",
         f"Fab parts measured from STEP at 7850 kg/m3; bought parts catalogue.",
         f"**Total {total} kg** (target 165 kg, delta +{total-165:.1f} kg).", "",
         "| Category | kg |", "|---|---:|"]
for k, v in sorted(cats.items(), key=lambda kv: -kv[1]):
    lines.append(f"| {k} | {v} |")
lines += ["", "| Part | Qty | kg each | kg | Source |", "|---|---:|---:|---:|---|"]
for it in sorted(items, key=lambda x: -x["mass_kg"]):
    lines.append(f"| {it['part']} | {it['qty']} | {it['unit_kg']} | {it['mass_kg']} | {it['source']} |")
(ROOT / "MASS.md").write_text("\n".join(lines) + "\n")
print(json.dumps({k: out[k] for k in ("category_kg", "total_kg", "delta_kg")}, indent=1))
