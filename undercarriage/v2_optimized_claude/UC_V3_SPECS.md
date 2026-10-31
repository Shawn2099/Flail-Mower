# UC-V3 COMPONENT SPECS — three builds, exact published data

Status: **preliminary, 31 Oct 2026.** Published values only; items marked
**CONFIRM** need a supplier drawing or written quote before CAD is frozen.

## 1. The three builds

| | **E48-2.2** | **E48-3.0** | **H24** |
|---|---|---|---|
| Deck | 48 V 2.2 kW BLDC + 60 A controller | 48 V 3 kW Mecwin PMSM + 300 A | 9 hp petrol engine, belt |
| Traction | 2 × 48 V 600 W geared | 2 × 48 V 600 W geared | 2 × 24 V 450 W geared |
| Battery | 2P 48 V 40 Ah | 2 × 48 V 20 Ah, separate | 1 × 24 V 40 Ah |
| Charging | 48 V 10 A charger | 2 chargers | 24 V 80 A alternator |
| Remote | RC + ESP32 | RC + ESP32 | RC + ESP32 + throttle/clutch |

## 2. Motors

| Spec | Mecwin 3 kW PMSM | Generic 2.2 kW 48 V | Mecwin 1.2 kW | Mecwin 1.0 kW | MY1020Z 48 V 600 W | MY1020Z 24 V 450 W |
|---|---:|---:|---:|---:|---:|---:|
| Rated power | 3,000 W | 2,200 W | 1,200 W | 1,000 W | 600 W | 450 W |
| Voltage | 48/60/72 | 48 | 48/60 | 48/60 | 48 | 24 |
| Rated speed | 3,000 rpm | 3,000 rpm | 3,300 rpm | 3,000 rpm | 3,200 rpm | 3,000 rpm |
| Max speed | 4,000 rpm | 3,500 rpm | 3,500 rpm | 3,300 rpm | 3,400 rpm | 3,400 rpm |
| Gearbox | none (spline) | none (keyed) | 1:13.2 helical | 1:12 helical | 1:6.67 spur | 1:6.67 spur |
| Output torque | 9.5 Nm @ 3,000 | 7.0 Nm @ 3,000 | **25 Nm @ 250** | **23 Nm @ 250** | **12 Nm @ 480** | **9.67 Nm @ 450** |
| Peak torque | 2× [EST] | 2× [EST] | 25 Nm (stall) | 23 Nm (stall) | 24 Nm [EST] | 19.3 Nm [EST] |
| Max DC current | 300 A ctrl | 60 A ctrl | 60 A | 55 A | 16 A | 24 A |
| Mass | 15 kg [EST] | 10 kg [EST] | 9.0 kg | 8.0 kg [EST] | 5.4 kg | 5.4 kg |
| Shaft | spline/sprocket | 25 mm keyed | helical output | helical output | 18 mm keyed | 18 mm keyed |
| Price | ₹19,400 | ₹10,000-15,000 | ₹10,421 | ~₹9,000 [EST] | ₹8,850* | ₹7,874 |

`*` 36 V 480 rpm listing; confirm 48 V price.

**CONFIRM:** Mecwin 3 kW shaft drawing, foot pattern, hall/encoder, mass.
**CONFIRM:** generic 2.2 kW continuous rating, shaft, hall type, controller match.

### Flail motor selection for E48-2.2

The 2.2 kW is a **class**, not a part. The specific Indian candidate is the
**Datai 2.5 kW PMSM** (Nanya Airconn, New Delhi, ~₹8,000-9,000):

- 2.5 kW at 3,000 rpm = 8.0 Nm at the motor.
- At 2,200 rpm (1.36:1 pulley) = 10.9 Nm at the deck.
- Rotor needs 8.7 Nm at 2 kW, so **+25% margin**.
- 48 V, keyed shaft, halls — **confirm drawing**.

The **Datai 3 kW PMSM** (~₹10,500-11,000) gives 13 Nm at 2,200 rpm (+50%)
for about ₹2k more. Controller: 48 V 60 A sine wave (₹3,000-5,000) for the
2.5 kW; 48 V 100 A (₹6,000-8,000) for the 3 kW.

## 3. Batteries

| Spec | 48 V 20 Ah | 24 V 40 Ah |
|---|---:|---:|
| Nominal | 51.2 V, 20 Ah, 1.02 kWh | 25.6 V, 40 Ah, 1.02 kWh |
| BMS continuous | 90 A (current spec) | 60 A |
| BMS 10 s | 120 A | 100 A |
| Charge current | 10-20 A | 20-30 A |
| Mass | ~8 kg | ~8 kg |
| Price | ₹27,000 | ₹27,000 |

**CONFIRM:** cell C-rate (≥3C for the 48 V flail pack), charge FET rating,
dimensions, connector type. A 20 Ah pack at 3 kW is 3.1C — not a commodity pack.

## 4. Engine and alternator (H24)

| Spec | Value |
|---|---|
| Engine | 9 hp / 270 cc, 3,600 rpm |
| Continuous | ~5.2 kW (7 hp) [EST] |
| Shaft | 25 mm keyed |
| Start | recoil (electric optional) |
| Fuel tank | 3.6-6.5 L |
| Fuel use | ~1.2 L/h at 3.8 kW |
| Mass | ~25 kg |
| Price | ₹14,000-19,000 |
| Alternator | 24 V, 80 A, 2.24 kW |
| Regulation | 28.8 V (8S LiFePO4 wants 29.2 V) |
| Efficiency | ~60% (2.0 kW mechanical for 1.2 kW electrical) |
| Mass | ~7.5 kg |
| Price | ₹8,000-12,000 |

**CONFIRM:** engine continuous kW at 3,600 rpm, shaft drawing, base pattern.
**CONFIRM:** alternator charge curve at 3,600 rpm and pulley ratio.

## 5. Controllers

| Controller | Voltage | Current | Price | Note |
|---|---|---:|---:|---|
| Mecwin 300 A | 48/60/72 | 300 A | ₹16,386 | Hall/encoder, GUI |
| Mecwin 60 A | 48/60 | 60 A | ₹13,867 | For 1.2 kW |
| Generic 48 V 60 A | 48 | 60 A | ₹3,000-5,000 | Confirm hall match |
| Generic 48 V 100 A | 48 | 100 A | ₹6,000-10,000 | For 3 kW |
| Brushed 48 V 30 A | 48 | 30 A | ₹1,500-2,500 | For 600 W |
| Brushed 24 V 60 A | 24 | 60 A | ₹1,500-2,500 | For 450 W |

## 6. Open items before the design is frozen

1. **Mecwin 3 kW shaft and foot** — spline vs keyed, drawing, mass.
2. **Generic 2.2 kW motor** — continuous rating, shaft, hall type, controller.
3. **Battery BMS** — 3C cells and charge FET for the 48 V flail pack; 60 A/30 A for 24 V.
4. **Engine** — continuous kW, shaft, base, fuel tank.
5. **Alternator** — output at 3,600 rpm, regulator voltage, pulley.
6. **Controller** — hall angle and connector for each motor.

Until these are confirmed, the sim uses the published values above and the
conservative 2× peak assumption where no peak is published.

## 7. Sim result (`sim_v3_options.m`)

All three pass the 400/15 continuous and 400/20 burst gates at the wheel.

| Build | v m/s | Wheel cont/burst | Build mass | Deck margin | Battery | Runtime | All-in new | Self-fab/used |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| **E48-2.2** | 0.88 | 68/137 Nm | 277.5 kg | **+45%** (0.65 derate) | 2P 1.49C | 40 min | ₹318k | **₹248k** (used pack) |
| **E48-3.0** | 0.88 | 68/137 Nm | 282.5 kg | +97% (0.65 derate) | flail 3.12C | 20 min flail | ₹367k | ₹292k (used packs) |
| **H24** | 0.83 | 55/110 Nm | 299.0 kg | engine 73% | 0.69C | 87 min + fuel | ₹323k | **₹245k** (used engine/alt/pack) |

Key result: the **3 kW + two separate 48 V packs** plan is the most expensive.
The **2.2 kW + one 2P pack** is the cheapest full electric, and the **H24** is the
only unlimited-runtime build. None fits ₹2.5L with all-new parts.
