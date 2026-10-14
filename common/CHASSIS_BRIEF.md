# CHASSIS BRIEF — body, tracks, 2 traction motors (all values to design against)

## 1. Envelope (mm, ground = 0, rotor centre = machine datum)
- Overall: ~800 W × ~1150 L × ~650 H (motor top 593 + margin). Mock `medium.stp` #598
  reads 1000 × 750 × 495 — width matches; length/height to reconcile (mock has no tall motor).
- Deck datum: rotor centre (Y0, Z218). Lip +205 fwd, roller rear −400, roof 405, skirts to Z20.
- Belly clearance: chassis belly ≥100 (deck tips run at 60; skids set 40–80 cut band).

## 2. Mass budget (weighed where possible)
| Item | kg | Source |
|---|---|---|
| Deck steel | ~64 | `flail/rev2/cad/weigh.py` |
| Rotor hardware (blades/tabs/bolts/discs) | 7.1 | sim − modelled drum+shaft |
| Mower motor 3 kW | 15 | Mecwin class estimate |
| Pack 48V 20Ah (MVP field pack) | **~8** | 960 Wh LiFePO4; corrected (15 was 2× over) |
| Traction motors 2× | ~16 | `motor_traction_geared` EST |
| Tracked chassis + electronics + harness | 60–100 | **OPEN: biggest lever, unbuilt** |
| **Mast (no chassis)** | **~96** | tilt_check (pack corrected) |
| **Total** | **~160–200** | vs Striker 150 (wheeled IC) |

## 3. Stability (from real CAD CG, `tilt_check.py`, SF 1.3)
Track outer width for slope: 30° → ~430 mm, 45° → ~750 mm (120 kg chassis case).
**Set track outer = 750.** Pack must sit low (z ≤ 150, between tracks); motor stays top (clean air beats CG).

## 4. Traction sizing (μ = 0.12 tracks-on-grass, sprocket r = 0.10, 200 kg case)
| Grade | Force total | Power @1 m/s | Torque/track |
|---|---|---|---|
| Flat | 235 N | 235 W (matches sim 200 W allowance) | — |
| 30° continuous | 1185 N | 1.2 kW | 59 N·m |
| 45° burst | 1554 N | 1.6 kW | 78 N·m |
- Spec: 2× 48V ~1 kW geared, ≥60 N·m out, ~150 rpm max (≈1.5 m/s). Separate BLDC drivers.
- Ground pressure @200 kg on 2×(0.75×0.15): **8.7 kPa** — turf-safe. Keep contact ≥0.2 m².
- Runtime: rotor 689 W + traction 235 W = 924 W → 48V20Ah (768 Wh usable) ≈ **50–60 min**.

## 5. Deck interface (deck coords, rel rotor centre)
- 4× M12 rubber mounts: x ±250, y +150 / −300, z ≈ 60 zone on cheeks (ADD Ø13 holes to cheek DXF next rev).
- 2× M12 lift points: torque-tube gussets (±269, −190, 415).
- Belt plane x ≈ 297–339, guard to x 357 — keep chassis rails clear of x > 290 on drive side.
- Pack bay: ~300×200×250 low between tracks. Motor plate slots ±15 already in deck.

## 6. Electrical
48 V common bus (traction + drivers + mower IF Mecwin confirms 2500 rpm on 48 V, else 60/72 V for mower only).
Mower fuse: 12 N·m current cap. Traction fuse: driver current caps per 60/78 N·m table.

## 7. Open inputs (block purchase, not design)
Mecwin keyed-shaft bore + foot pattern • track supplier combo (assembly + gearmotor as unit?) •
pack final (48V20Ah assumed) • chassis frame design (the actual remaining machine).
