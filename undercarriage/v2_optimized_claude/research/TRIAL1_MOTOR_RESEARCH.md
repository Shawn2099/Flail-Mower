# TRIAL-1 TRACTION MOTOR RESEARCH — coffee-estate flail rover (undercarriage v2)

Status: **research / option study, 31 Oct 2026. Not frozen.** Nothing here changes `COMPONENTS.md`,
`sim_v2.m` or any frozen spec. Prices are listing prices or estimates, not quotations.
Tags: **[V]** seen on a source page, **[V-partial]** from search snippets only, **[EST]** my estimate,
**[CALC]** my own arithmetic from the model in the sims.

Sims (base MATLAB, run with `matlab -batch`; the MATLAB MCP was not exposed in this session):
`v2_trial1_drive.m`, `v2_trial1_compare.m`, `v2_trial1_compare_all.m` (writes `../trial1_compare.png`),
`v2_trial1_levers.m`, `v2_trial1_widearc_speed.m`. Summary doc: `../TRIAL1_DRIVE.md`.

---
## 1. Brief and how the load case changed
- Trial 1: coffee plantation in India, **firm/flat ground and mild slopes only**, 180x72x37 rubber tracks,
  undercarriage v2 (48T wheel sprocket, 428 chain, Rp 105.26 mm), carrying flail rev2.
- Goal: right-size traction motors and cut electrical cost; allowed to spend about Rs 10k extra for usability.
- The inherited sizing used a **400 kg / 20 deg** envelope. Replaced here by the as-built **282 kg** all-up
  machine (`WEIGHT_EFF.md`), slopes 0-10 deg, dry and wet soil, 0.5-0.88 m/s.
- The user did not give slope, speed, turn style or soil, so all were swept.

## 2. Model (what the sims compute)
Per-side wheel torque = (grade + Bekker bulldozing resistance + internal track/roller resistance + flail
reaction)/2 x Rp, plus, for a pivot, the skid-steer turning moment (Wong): `Mr = mu_t * W * Ls / 4`, force per
side `Mr / gauge`. Ls = 1.0013 m, gauge 0.52 m.

| Term | Value | Status |
|---|---|---|
| Dry soil Bekker n 0.7, kc 5.27, kphi 1515 (kN units) | existing sim_v2 set | [V-partial]: matches arXiv 2603.28965 and UMD ENAE788X L07; Wong's own table not opened |
| Wet soil n 0.5, kc 13.19, kphi 692.15 | "clayey/loam" row | [V-partial] low: conference paper citing Wong, units not stated; not a measured coffee-estate soil |
| mu_t (lateral grip, tracks on soil/grass) | 0.3-0.6 swept | [EST]; real value unmeasured |
| Internal rolling coefficient | 4% dry / 8% wet of weight | [EST] |
| Flail reaction on rover | 100 N | [EST] |
| Chain efficiency | 0.95 | [EST] |
| Allowed peak utilisation | 0.8 of cap | engineering margin [EST] |
| RMS limit | 0.85 x rated (intermittent, 40 C) | [EST] |

### Wheel torque per side (282 kg)
| Case | Nm/side |
|---|---:|
| Flat dry mow | 11 |
| Flat wet mow | 17 |
| 5 deg dry | 24 |
| 8 deg wet | 37 |
| Wide-arc turn, wet | 42 |
| Pivot dry, mu 0.5 | 81 |
| Pivot wet, mu 0.6 | 101 |

**Key finding:** on flat/mild ground the grade term is small. The **pivot (skid-steer) turn sets the
requirement**. Wide-arc turns cut the worst case to 42 Nm (42%).

## 3. Pivot turns
In a pivot one track drives forward and the other backward (counter-rotating), so both motors work at the
same time against the ground's turning resistance. At 0.3 m/s track speed this is about 430 W electrical in
total, about 13-16 A from the pack. The existing repo rule stands: never pivot on slopes.

## 4. Can the design reduce the motor requirement? (`v2_trial1_levers.m`)
Worst case wet pivot, mu 0.6, base 101 Nm:

| Lever | Wheel Nm | vs base |
|---|---:|---:|
| **Wide arcs only (turn load ~0.3x [EST])** | **42** | **42%** |
| Weight 282 -> 262 kg (`WEIGHT_EFF.md` cuts) | 94 | 93% |
| Weight 240 kg | 87 | 86% |
| Gauge 0.52 -> 0.60 m | 90 | 89% |
| Contact length 1.0 -> 0.8 m (needs a redesign) | 84 | 83% |
| Real mu_t 0.45 (measure it) | 80 | 79% |
| 262 kg + wide arcs | 40 | 39% |

Only the **no-pivot turning rule** matters much. Weight and gauge give 7-11% each. Slowing a pivot to half
speed halves the power (about 580 W to 290 W) but not the torque. Operational alternative: three-point turn at
the headland, or an arc of roughly 1.5 m radius; needs about 2 m of clear headland (machine is 0.83 m wide).

## 5. Motor options researched

### 5.1 Baseline in the repo
- Mecwin 1.2 kW L3-BLDC, 48 V, 25 N-m gearbox output at 275 rpm (nameplate), Rs 10,421; Mecwin 60 A
  controller Rs 13,867 (`COST_DOWN.md`). Frozen drive uses a 14T pinion on the 48T sprocket (0.88 m/s).
- `MOTOR_SWAP.md` proposed the MY1020Z 48 V 600 W brushed gearmotor. **Correction:** the Yalu datasheet
  (via search summary) gives **1.80 N-m at 3200 rpm on the motor shaft**, 16 A at 48 V, 1:6.67, 480 rpm
  output, so output torque is about **10.2 N-m** after a 0.85 gear efficiency [CALC], not the 12 N-m used
  there. Source: [Yalu datasheet on Robu](https://aws.robu.in/wp-content/uploads/2022/05/Wenzhou-Yalu-DC-Motor-MY1020Z-1265090.pdf) [V-partial].

### 5.2 Searched categories (snippets mostly; many product pages blocked direct fetch)
| Candidate | Result |
|---|---|
| 24 V Dongzheng wheelchair gearmotor 350 W, 32:1 | About 119 rpm, 23.5 Nm, 7.2 kg, listed 60 Nm max output; price/IP/brake unverified; needs 24 V controller plus 48->24 V DC-DC (about Rs 4.1k each). [DirectIndustry](https://directindustry.com/prod/zhejiang-dongzheng-motor-co-ltd/product-209469-2128453.html) |
| SuperDroid PCS-250 / 320 W wheelchair motors | Torque unpublished; discontinued variants; US prices |
| Senchuan SCD2-A 250 W | Rs 10,855, torque not published; too weak for pivots |
| MY1016Z 250 W 75 rpm | About Rs 24,000 landed; torque unpublished |
| Worm / planetary small motors (Rhino NEMA23 etc.) | 7-20 Nm at low rpm, 100 W class; too weak |
| MY1020 1 kW 48 V brushed go-kart motor, 3000 rpm, 3.2 Nm | Rs 4.9-7.6k; needs ~48:1 reduction (worm gearbox price not found) |
| Motenergy ME0909/0708/1003, Etek | US$385-760 each; oversized/expensive |
| Golden Motor HPM 3-5 kW | Oversized |
| ibots 1.5-2 kW mid-drive motors | Listed torques (63-103 Nm) inconsistent with ratings; not used |
| Treadmill DC motors | 180 V; do not fit |
| 48 V 500 W e-bike geared motor (Robodo, out of stock) | About 10 Nm; same family as 5.3 |

Controllers and packs (snippets, low confidence):
- Cytron 60 A dual driver limited to 45 V; Sabertooth 2x60 limited to 30 V: both unusable on a 48 V pack.
- Generic reversible 60 A brushed modules Rs 1.0-2.7k; one spec sheet says 40 A or less continuous.
- Votol EM50-series BLDC 50 A: Rs 5-6k from an Indian seller; Kelly KLS: no Indian price found.
- 48 V to 24 V 30 A DC-DC: about Rs 4.1k. 48 V 30-40 Ah LiFePO4: no firm price (about Rs 16-27k range, low confidence).

### 5.3 Robokits 1418ZXF 48 V 500 W (E-bike geared BLDC) — page fetched
Rated 102 kg-cm (about 10 Nm), 450 rpm rated / 516 no-load, 13.4 A rated, 4.0 A no-load, 1:6, **4.13 kg**,
Rs 5,620, in stock. Peak torque, IP, gear material and shaft style not listed. Nylon gears assumed.
[Robokits page](https://robokits.co.in/motors/rhino-bldc-brushless-dc-motor/rhino-500w-48v-bldc-motors/e-bike-brushless-dc-geared-motor-1418zxf-48v-450rpm-500w-premium-quality)

### 5.4 BM1418ZXF 750 W 48 V kit — search + Robodo page
Rated 15.36 Nm, 2800 rpm before / about 480 rpm after 1:6, 20 A full load, 5 A no load, Rs 5,670 motor only
([Robodo](https://robodo.in/products/unite-dc-48v-750w-bm1418zxf-brushless-gear-motor)). Zbotic page returned 403.
Listings disagree: one claims 45 Nm continuous / 72 Nm peak (discarded as generic copy; 15.36 Nm used);
kit controllers are described as 350, 500 or 750 W by different sellers. Gear material and weight not
stated; stock unclear. [Robu 750 W kit](https://robu.in/?p=1400895), [Engineer Store](https://www.theengineerstore.in/products/bm1418zxf-750w-48v-brushless-tricycle-motor-kit).

### 5.5 LION EV e-rickshaw parts
- [Motor collection](https://www.lionev.in/collections/e-rickshaw-bldc-motor): 1 kW 48/60 V motors Rs 6,000-6,600; 55 A controller Rs 3,800.
  One listing: rated current 25 A, max speed 3000 rpm, max power 1000 W.
- **User-supplied spec for the chosen model: 48 V, 13.5 A, 3000 rpm, "1000 W".** 48 V x 13.5 A is only about
  650 W in, so continuous output is about 550 W and **rated torque about 1.75 Nm**; "1000 W" is a peak.
  Peak assumed 3.3 Nm (about 25 A) [EST].
- [Closed differential gearbox](https://www.lionev.in/products/lion-ev-e-rickshaw-closed-type-differential-gearbox): 1:10, 800-1500 W class,
  sealed cast-iron housing, alloy-steel gears, 33"/35" axles, Rs 2,600. Input spline, weight, torque rating not listed.
- User plan: one gearbox per side with the differential **locked** so both outputs turn together (an open
  diff would give the driven side almost no torque). Prefer a bolt-in pin over welding hardened gears.
  Chain pull on the axle stub is about 1 kN at the pivot peak; confirm bearing capacity.
- [Paddle-rickshaw 1 kW kit](https://www.lionev.in/collections/e-bike-conversion-kit-spares-accessories/products/lion-ev-1000w-48v-paddle-rickshaw-kit): Rs 9,000, "brushless or hub motor"; rpm, torque, ratio,
  controller rating all unstated. **Not gradable.**

## 6. Comparison (`v2_trial1_compare_all.m`, graphs in `../trial1_compare.png`)
Four panels: torque demand vs rated, wheel-torque envelope vs speed, cost, row-cycle energy.

Pivot (hard case) before the no-pivot rule, % of motor rated torque, wet mu 0.6 / peak margin:
| Option | Pivot wet % rated | Cap/need | Top speed (pivot-capable pinion) |
|---|---:|---:|---:|
| A Mecwin 1.2 kW, 9T | 80% | 1.25 | 0.57 m/s |
| B 1418ZXF 500 W, 8T | 177% | 0.85 (fails) | 0.83 |
| C BM1418ZXF 750 W, 8T | 115% | 1.30 | 0.88 |
| D LION (corrected 1.75 Nm), 10T | 141% | 1.34 | 0.69 |

Row cycle (100 s mow at 0.5 m/s + 8 s pivot): about 172 W traction for A and D, 203 W for B and C; negligible
next to the mower motor.

## 7. Wide-arc turns only: top speed (`v2_trial1_widearc_speed.m`)
Gates: wet arc 42 Nm and 8 deg wet 37 Nm within 0.8 x allowed peak, RMS within 0.85 x rated.

| Option | Pinion for 0.88 m/s | Top speed | Peak vs cap |
|---|---:|---:|---:|
| A Mecwin 1.2 kW | 14T (frozen) | 0.88 m/s = **3.2 km/h** | 52% |
| B 500 W BM1418ZXF | 9T | 0.93 m/s = 3.3 km/h | 55% |
| C 750 W BM1418ZXF | 8T | 0.88 m/s = 3.2 km/h | 32% |
| D LION + locked diff | 13T | 0.89 m/s = 3.2 km/h | 41% |

Torque would allow 1.24-1.38 m/s (4.5-5.0 km/h) on A, B, D, but the v2 chain/tracks were proved only to the
1.0 m/s mow band, so **0.88 m/s (3.2 km/h) is the recommended top speed; mowing is about 0.5 m/s (1.8 km/h).**

## 8. Cost (both sides, Rs, mostly [EST])
| Option | Motor | Controller | Gearbox | Pinion | Plate | Shroud | **Per side** | **Both** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A Mecwin, stock Mecwin controller | 10,421 | 13,867 | 0 | 400 | 0 | 0 | 24,688 | 49,376 |
| A Mecwin, generic controller | 10,421 | 5,500 | 0 | 400 | 0 | 0 | 16,321 | 32,642 |
| B 500 W BM1418ZXF (mid) | 5,620 | 4,000 | 0 | 400 | 1,500 | 800 | 12,320 | 24,640 |
| C 750 W BM1418ZXF (low / mid / high controller) | 5,670 | 2,000 / 4,000 / 6,000 | 0 | 400 | 1,500 | 800 | 10,370 / 12,370 / 14,370 | 20,740 / 24,740 / 28,740 |
| D LION 1 kW + 55 A ctrl + diff | 6,000 | 3,800 | 2,600 | 400 | 1,500 | 500 | 14,800 | 29,600 |

Against the Mecwin with generic controllers the realistic BM1418ZXF saving is about Rs 8k (range Rs 4-12k);
the Rs 20-29k saving exists only against the stock Mecwin controllers. Pinion, plate, shroud, bracket are
guesses; battery, harness and the mower are unchanged. Packs: typical mowing draws about 49-52 A with the mower;
keep two packs for trial 1 until BMS/cell datasheets show a single pack can carry about 100 A pivot+mower peaks.

## 9. Controllers: generic vs matched
Generic or no-name controllers on the Mecwin motor are **not recommended without a bench test**: unverified
hall timing, peak-vs-continuous ratings (a "60 A" module was reported at 40 A or less continuous), weak
protection, no IP rating, and a runaway risk on a 285 kg machine with a flail. Prefer a **matched motor +
controller set from one seller**, with written confirmation that the controller is rated for the motor at
48 V. Keep the contactor, fuse and e-stop outside the controller.

## 10. Recommendation and plan
1. Adopt **wide-arc turns, no pivots** (needs about 2 m headland; pivot only slow, flat, emergency).
2. Shortlist: **C (750 W BM1418ZXF kit)** best value; **D (LION set)** for steel gears and local spares;
   **A (Mecwin)** proven fallback, most expensive; B only with the no-pivot rule.
3. Ask sellers in writing: BM1418ZXF gear peak and kit controller rating; LION motor peak current/torque, weight,
   spline fit; reverse-at-torque support on both controllers.
4. Bench-test one C kit and one D set (about Rs 15k): unloaded, locked-wheel, 8 s overload, temperatures.
5. Order the winner for both sides; keep A as fallback. Field-measure mu_t with a spring-scale pull test and rerun the sims.

## 11. Not verified / open
- Wong's Table values for dry/wet soil, mu_t, internal rolling resistance; coffee-estate slope and soil data.
- Gear material and peak torque of both BM1418ZXF motors; LION motor peak torque, weight, IP, shaft; all weights.
- Prices for the controller options and gearbox accessories; brushed controller prices; 48 V LiFePO4 pack prices and BMS ratings.
- Most pages were read from search snippets; several (Zbotic, Robu direct, SuperDroid, DirectIndustry) were blocked.
