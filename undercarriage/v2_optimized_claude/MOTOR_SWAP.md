# MOTOR SWAP — brushed geared motors vs the 1.2 kW BLDC

Status: **option study, not frozen.** Frozen drive stays `2x Mecwin 1.2 kW` until a
swap is chosen and re-proved. Sim: `v2_motor_swap.m` (base MATLAB, prints PASS/FAIL).

## 1. What the v2 drive actually needs

From `sim_v2.m` (all PASS): wheel torque at the 48T sprocket, `G = 48/14 = 3.43`,
`eta = 0.95`, top speed 0.88 m/s at 275 rpm motor.

| Case | Wheel Nm | Motor Nm | Motor W @275 rpm |
|---|---|---|---|
| 400 kg / 15 deg, continuous | 53.5 | 16.4 | 473 |
| 400 kg / 20 deg, burst | 70.7 | 21.7 | 625 |
| 250 kg / 15 deg, daily duty | 33.4 | 10.3 | 295 |

So the real specification is **torque**, not the 1.2 kW label: about **22 Nm at
275 rpm** per side. The sim freezes the gearbox output at the 25 Nm nameplate
stall, which is why the burst limit is 81.4 Nm at the wheel.

Note: `undercarriage/v1/INPUTS.md` rejected a 1 kW motor at the **existing 3.43
ratio** (1.4% short). The 600 W result below is not a contradiction: it only
works because the 8T pinion raises the ratio to 6:1. At 3.43 the 600 W motor
gives 39 Nm and fails.

## 2. Minimum motor count = 2

One motor cannot skid-steer. With a locked differential both tracks turn at the
same speed (infinite turn radius); with an open differential the torque goes to
the unloaded inside track. A 1 m-radius turn at 0.5 m/s needs 0.63 / 0.37 m/s
across the 0.52 m track gauge, and a pivot turn needs -0.5 / +0.5 m/s.
Two motors, one per track, is the minimum. Four is unnecessary.

## 3. Candidate screen (`v2_motor_swap.m`)

Re-geared to hold 0.88 m/s (pinion = 48/G):

| Candidate | V | Rated W | Out rpm | Rated Nm | Peak Nm | Pinion | Wheel cont | Wheel burst | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| Mecwin 1.2 kW (reference) | 48 | 1200 | 275 | 25.0 | 25.0 | 14T | 81.4 | 81.4 | PASS |
| MY1016Z2 250 W | 24 | 250 | 357 | 6.65 | 11.5 | 11T | 28.1 | 48.6 | FAIL |
| MY1016Z3 350 W | 24 | 350 | 300 | 11.1 | 19.0* | 13T | 39.4 | 67.5 | FAIL |
| MY1020Z 450 W | 48 | 450 | 450 | 9.7 | 19.4* | 9T | 51.7 | 103.4 | FAIL (3% short cont) |
| **MY1020Z 600 W** | **48** | **600** | **480** | **12.0** | **24.0*** | **8T** | **68.2** | **136.5** | **PASS** |
| Wheelchair 250 W 19:1 | 24 | 250 | 150 | 16.95 | 33.9* | 26T | 30.1 | 60.2 | FAIL at 0.88 m/s |
| Rhino NEMA34 worm 500 W (BLDC) | 48 | 500 | 150 | 19.6 | 39.0* | 26T | 34.8 | 69.3 | FAIL at 0.88 m/s |

`*` peak not published by the maker — taken as 2x rated.

Drop-in with the existing 3.43 chain (no sprocket change):

| Candidate | Speed m/s | Wheel cont | Wheel burst | Verdict |
|---|---|---|---|---|
| MY1016Z2 250 W | 1.15 | 21.7 | 37.5 | FAIL, too fast |
| MY1016Z3 350 W | 0.96 | 36.2 | 61.9 | FAIL torque |
| MY1020Z 450 W | 1.45 | 31.6 | 63.2 | FAIL, too fast |
| MY1020Z 600 W | 1.54 | 39.1 | 78.2 | FAIL cont, too fast |
| **Wheelchair 250 W 19:1** | **0.48** | **55.2** | **110.4** | **PASS torque, 4% below mow band** |
| Rhino NEMA34 worm 500 W (BLDC) | 0.48 | 63.8 | 127.0 | PASS torque, slow |

## 4. Answer

- **Least number:** 2 motors.
- **Least rating that keeps the full 400 kg / 20 deg / 0.88 m/s envelope:**
  a **48 V, 600 W geared brushed motor, about 12 Nm rated / 24 Nm peak at
  450-480 rpm, with an 8T-9T pinion on the existing 48T wheel sprocket.**
  The MY1020Z 48 V 600 W (6.67:1) is the catalogue example. At 8T it runs
  9.4 Nm (0.78 of rated) on the 400 kg/15 deg continuous case and 0.88 m/s.
- **Cheapest true drop-in (no sprocket change):** a **24 V 250 W wheelchair
  gearmotor, 19:1, 150 rpm, 17 Nm rated / 34 Nm peak**, one per side. It gives
  55 Nm at the wheel and 0.48 m/s. It passes on torque (400/15 needs 16.4 Nm vs
  16.95 rated, 400/20 burst 110 Nm available vs 70.7 needed), but the 400/15
  continuous point is 1.03x its 250 W rating and 0.48 m/s is 4% below the 0.5 m/s
  mow band. It also has a 33 Nm fail-safe brake.
- **All the small e-bike motors fail** for the same reason: they are fast and
  weak (6-12 Nm at 300-500 rpm). Through the 3.43 chain that is only
  22-39 Nm at the wheel, versus 53.5 Nm needed. The 250 W MY1016Z2 is less than
  half the required wheel torque.

## 5. Practical caveats

1. **Voltage.** The pack is 48 V. Buy the 48 V version of the motor. A 24 V
   motor on 48 V runs at double speed; either re-gear for it, cap the controller
   duty at 50%, or use a 48->24 V 30 A DC-DC. Capping duty is cheap but puts 48 V
   pulses across 24 V brushes; a DC-DC is cleaner.
2. **Heat.** Brushed is about 78% efficient vs about 85% for the BLDC. At the
   400 kg/15 deg continuous point the 600 W motor runs at 472 W (79% of rating);
   the daily 250 kg/15 deg point is 295 W (49%). Add airflow and a temp sticker
   (FMEA #10 already asks for one).
3. **Ingress.** E-bike motors are typically IP33 — splash-resistant, not mud-
   proof. The v2 has no chain guards and the motors sit low (z250-440). Add a
   shroud with a vent, or accept shorter brush/gearbox life.
4. **Brushes.** About 5000 h mechanical life, replaceable. At 50 min/day that
   is decades; inspect yearly for dust and wear.
5. **Efficiency/runtime.** About 6% more battery draw on the duty mix; 50 min
   becomes about 47 min on the 768 Wh usable pack.
6. **No regen** with a brushed controller. Minor for a mower.
7. **Mounting is not drop-in.** The MY1020Z has a 120 x 73 mm foot, 99 x 57 mm
   holes, 18 mm keyed shaft; the v2 rails are drilled for the Mecwin. Expect an
   adapter plate and a new bored/keyed pinion (8T or 9T, 428). The 10T supplied
   with the motor is #420 and gives 1.10 m/s at 0.98 of rated torque — no margin.
8. **Parking.** The MY1020Z has no brake; keep the existing pin lock on the 48T
   hub (155 Nm at 30 deg). The wheelchair motor's 33 Nm brake is only 114 Nm at
   the wheel, so it does not replace the pin either.
9. **Gearbox peak is the open number.** The 600 W motor's 24 Nm peak is an
   estimate, not a datasheet value. The 400/20 grade needs 12.4 Nm at the motor,
   which even a 1.5x peak clears. The `sim_v2_turn` turn+15 deg cases need
   19-21 Nm at the motor (1.6-1.75x rated), so get the gearbox peak rating from
   the supplier before relying on those. The existing "never pivot on slopes"
   rule still stands.

## 6. Cost (indicative, Oct 2026)

| Item | Each | Qty | Total |
|---|---|---|---|
| Mecwin 1.2 kW L3-BLDC | Rs 10,421 | 2 | Rs 20,842 |
| Mecwin BLDC controller 60 A | Rs 13,867 | 2 | Rs 27,734 |
| **Mecwin total** | | | **Rs 48,576** |
| MY1020Z 48 V 600 W | Rs 8,850* | 2 | Rs 17,700 |
| 48 V 30 A brushed controller | Rs 1,500-2,500 | 2 | Rs 3,000-5,000 |
| **Brushed total** | | | **Rs 20,700-22,700** |

Saving about Rs 26,000-28,000, plus about 3.6 kg/side (5.4 kg vs 9.0 kg).
`*` Zbotic price seen on the 36 V 480 rpm listing; confirm the 48 V variant.

## 7. Recommendation

If the 400 kg / 20 deg envelope is kept: **2x MY1020Z 48 V 600 W, 8T pinion
(0.88 m/s) or 9T (0.99 m/s, gentler chain), 48T wheel, 428 chain, 48 V 30 A
brushed controller per side.** Re-run `sim_v2.m` with the new motor mass and the
new chain pull before cutting metal.

If the real duty is 250 kg / 15 deg and 0.48 m/s is acceptable: **2x 24 V 250 W
wheelchair gearmotors (19:1)** are the cheapest true drop-in and bring a
fail-safe brake, at the cost of speed and continuous margin.

Do not use the 250-450 W e-bike motors: they fail the wheel-torque gate.

If you want to stay BLDC and 48 V, the **Rhino NEMA34 worm 500 W** (19.6 Nm at
150 rpm, Rs 12,300) is the same slow-but-strong trade as the wheelchair motor,
with no 24 V conversion.

Electrical cost-down: `flail/rev2/procurement/COST_DOWN.md`. Weight cut and the
850 W comparison: `undercarriage/v2/WEIGHT_EFF.md`. The competitor's 850 W is
37% over the 400/20 burst; 600 W is the smallest that keeps the envelope.

## 8. Sources

- MY1016Z2 250 W sheet: ebikethaikit.com PDF — 9.78:1, 6.65 Nm at 357 rpm,
  11.5 Nm max.
- MY1020Z 450/600 W sheet: Yalu PDF (robu.in) — 6.67:1, 1.45/1.80 Nm motor,
  450/480 rpm output, 78%, IP33, 5.4 kg.
- Wheelchair 24 V 250 W, 19:1: imimg datasheet — 150 rpm, 16.95 Nm rated,
  33.4 Nm brake, 80%.
- Rhino NEMA34 worm 500 W 48 V: Robokits — 200 kg-cm at 150 rpm, Rs 12,300.
- Prices: Mecwin from `flail/rev2/procurement/HANDOFF_PROMPT.md`; MY1020Z from
  Zbotic (Rs 8,850, Oct 2026).
