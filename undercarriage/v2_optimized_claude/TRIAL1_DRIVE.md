# TRIAL-1 TRACTION DRIVE: coffee estate, flat to mild slope

Status: **option study, not frozen.** Sim: `v2_trial1_drive.m` (base MATLAB, run with
`matlab -batch`; the MATLAB MCP was not exposed in this session). Frozen specs, `COMPONENTS.md` and
`sim_v2.m` are untouched.

## 1. What changed from the frozen envelope
The 400 kg / 20 deg case is dropped. Sizing uses the as-built **282 kg** all-up machine
(`WEIGHT_EFF.md`), slopes 0-10 deg, dry and wet soil, 0.5-0.88 m/s.

## 2. Result: the turn style decides the motor
| Scenario (282 kg, 5 deg) | Peak wheel Nm/side | Cheapest passing drive | 2 sides INR |
|---|---:|---|---:|
| Wide-arc turns, dry or wet | 36-42 | 2 x MY1020Z **450 W** 48 V, 8T pinion, 48 V 30 A brushed | ~20,600 |
| Pivot turns, dry or wet | 95-101 | 2 x Mecwin 1.2 kW BLDC, 8T pinion, generic 30 A BLDC controller | ~28,800 |

The grade term is small. The pivot (skid-steer) moment is 56-84 Nm/side and drives the sizing.
Banning pivot turns at row ends halves the torque requirement, so it is the biggest cost lever.
Against the current Rs 48,576 (Mecwin motors plus 60 A controllers), that saves roughly Rs 28k
(wide arcs) or Rs 20k (pivot).

## 3. Verification status of the assumptions
| Item | Status |
|---|---|
| Bekker dry sandy loam kc 5.27, kphi 1515, n 0.7 | Medium: matches arXiv 2603.28965 and UMD ENAE788X L07 via search snippets. Wong's original table was not opened. |
| Wet case (kc 13.19, kphi 692.15, n 0.5, "loam" row in a conference paper citing Wong) | Low. Labelled "clayey (wet)" in the sim. Not a measured coffee-estate soil. |
| MY1020Z: 1.80 Nm @ 3200 rpm motor shaft, 16 A @ 48 V, 6.67:1 | Medium (Yalu datasheet via search summary). Output is about 10.2 Nm, **not 12 Nm** as `MOTOR_SWAP.md` states. The gear efficiency of 0.85 is an estimate. |
| Peak torque = 2x rated | [EST]. Get the gearbox peak rating from the supplier. |
| mu_t 0.4-0.6, internal resistance 4-8% of W, flail reaction 100 N | [EST], unverified. |
| MY1020Z 450 W, MY1016Z3 and wheelchair prices; brushed controller prices | [EST]. The research found no brushed controller listing. Indian BLDC controllers: Rs 2,800-3,500 (low confidence). |
| Coffee estate slope / row spacing | Row spacing from a student deck only (low). No slope numbers found. |
| 0.85 RMS derate, 80% peak utilisation, 40 C ambient | [EST] engineering margins. |

## 4. Electrical (single pack question)
Typical mowing draws 49-52 A with a 60%-load mower; a pivot peak with the mower at 3 kW is about
103 A. A single 48 V 40 Ah pack is plausible only if its BMS and cells are rated at
least 2C continuous, which must be confirmed on the datasheet. Re-check `POWER_AND_BRAKE.md` §3
before dropping the second pack. Add about Rs 800 per motor for an ingress shroud (IP33 motors,
monsoon mud); this is included in the sim cost.

## 5. Open before ordering
1. Confirm wide-arc-only turning with the operator.
2. Get the MY1020Z 450 W price, the peak torque and the brushed controller current limit in writing.
3. Measure the real flail reaction and mu_t on the estate, and weigh the machine.

---
## 6. Update: option comparison and trial-1 plan (supersedes §2 where they differ)
Sims: `v2_trial1_compare_all.m` (graphs: `trial1_compare.png`), `v2_trial1_levers.m`, `v2_trial1_widearc_speed.m`.

**Operating rule: wide-arc turns only, no pivots (emergency pivot slow, flat only).** Wet wide-arc demand is
42 Nm/side vs 101 Nm for a wet pivot, so every drive below can run 0.88 m/s (3.2 km/h); mowing 0.5 m/s (1.8 km/h).
Measure the real lateral grip (mu_t) on the estate; the pivot case assumed 0.6 [EST].

| Option | Pinion (48T wheel) | Top speed | Peak vs cap, wet arc | Both sides, INR [EST] | Gears |
|---|---|---|---|---:|---|
| A Mecwin 1.2 kW + controller | 14T (frozen) | 0.88 m/s | 52% | 32.6k generic ctrl / 49k Mecwin ctrl | metal |
| B Robokits 1418ZXF 500 W (10 Nm, 1:6) | 9T | 0.93 | 55% | 24.6k | nylon |
| C BM1418ZXF 750 W (15.36 Nm, 1:6) | 8T | 0.88 | 32% | 24.7k | nylon |
| D LION EV 1 kW (48 V 13.5 A 3000 rpm) + locked 1:10 diff | 13T | 0.89 | 41% | 29.6k | steel |
| E LION paddle-rickshaw kit | - | - | not gradable (no torque/rpm/ratio on page) | 9k/side | - |

Unconfirmed: D peak torque (3.3 Nm assumed), D/BM1418ZXF weights, gear peak ratings, all prices except motor listings.

**Buy matched motor+controller sets, not mixed brands.** Mixed generic controllers on the Mecwin motor are untested
(hall timing, continuous vs peak amps, protection). Keep contactor, fuse and e-stop outside the controller.

**Trial-1 plan**
1. Get written confirmation: BM1418ZXF gear peak and kit controller rating; LION motor peak current/torque, weight, spline fit.
2. Bench-test one BM1418ZXF 750 W kit and one LION set (about Rs 15k): unloaded, locked-wheel, 8 s overload, temperatures.
3. Lock the differential with a bolt-in pin, not by welding hardened gears.
4. Pick the passing set for both sides; keep Mecwin (A) as fallback.
5. Field: spring-scale pull test for mu_t, then re-run the sims.
