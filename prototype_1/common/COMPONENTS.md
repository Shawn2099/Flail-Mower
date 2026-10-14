# COMPONENTS — final frozen values, one section per part
Source of truth: executed sim outputs (R2026b). `sim` = which sim proved it.

## Rotor group (~12.3 kg total, `sim_mvp_rotor` Q1–Q4, `sim_drum_specsheet`)
| Part | Frozen value | Source |
|---|---|---|
| Tube | 60.3 OD × 3.65 wall × 500 LG, IS 1239 50NB Medium, 2.55 kg | specsheet winner (6mm-tab gate) |
| Fins/tabs | 50W × 40H × 6T + 2 spacer washers/eye, hole Ø17.2 at 20 above tube, 4mm fillet E7018 | specsheet #7/#10 |
| Shoulder bolts | Turned Ø17 × 40, M14 thread, 10.9 + spacer + washer + nyloc | specsheet #8 |
| Pins | Shear 11/150, bend 61/180 MPa, hole-brg 24 MPa @cap 2500 | mvp Q3 PASS |
| Straight blades (MVP) | 340 g, Ø17, 30MnCrB5 | inputs; 10×, 36° helix, stations 15…485 |
| J blades (upgrade) | 400 g, hooks-forward, 2300 rpm, 20× opposing pairs | 2J sims |
| Hammers | 1050 g, PARKED (Ø16 pin fails) | structural C3 |
| Shaft/bearings | Ø25 × 700 EN8, UCF205 flanges (photo pattern), 600 span | mvp Q4: sag 0.0095, crit ~9700 |
| Rotor speed | Work 2200 / cap 2500 / floor 2100; tip 36.4 / 41.4 m/s | mvp Q1 |

## Drive + electric (`sim_mvp_rotor` Q2/Q5, enclosure §9c)
| Part | Frozen value | Source |
|---|---|---|
| Motor | Mecwin 3 kW PMSM, 4000 max, 65% cont duty | inputs; 35% loaded |
| Pulleys | 2× SPZ 100×3-1610 1:1 (Fenner/Pix stock) | drive block |
| Bushes | 1610: rotor bore 25+key; motor bore = keyed shaft (confirm 24/25/28 at order) | OPEN purchase item |
| Belts | 2× SPZ now (grooves 1–2); 3rd belt = 5 kW upgrade; length at fit-up (900/912/925) | C≈299, slots ±15 |
| Fuse | Electronic torque limit 12 N·m (21 on 5 kW); belt slip backup. NO slip clutch | DRIVE block |
| Controller | Mecwin 300 A, GUI-programmable (rpm cap + current cap) | inputs |
| Pack | MVP field: 48V 20Ah ~8 kg (960 Wh). 72V 70Ah sim case ≈ 30 kg (overkill, 5.9 h) | mvp Q5 + open item |

## Deck group, box-5 (`flail/rev2/sim_enclosure_design_v2` + `flail/rev2/cad/` scripts)
| Part | Frozen value | Source |
|---|---|---|
| Shell | ONE 867×550×4 development (308+330+229), 2 manual bends ~80°, r≥8, 11.7 kg | §5b, gates PASS |
| Corners (Y,Z rel) | Lip (205,100) / FTC (160,405) / RTC (−170,405) / mount (−210,180) | §5b Bx/Bz |
| Cheeks | 4mm, chamfered, SAME P/N flip; + 4mm doublers at UCF; 12× M10; 15.2+1.4 kg | audit + FreeCAD |
| Roller | 114.3×3.65 (100NB-L stock) × 562, centre (Y−343, Z57), 6004 + scraper, ~6 kg | §7, gap 11 |
| Deflector | 86 × 550 × 4 @50°, tip Z125, gap 11 over roller | §7 |
| Comb | ONE plasma part, tips Rcut+12, 2 hanger straps, unbolts for finish cut | D2 |
| Curtains | 12 rubber strips 80W (6+6 staggered), header Y210, in-swing + stop bar | F2/F3 |
| Flap | 8mm belt 550×160, mount Z180 → bottom Z25, slots 45–85 | O1 |
| Skids / skirts | Hardox 6, 280×90, slots 40–80 / rubber skirts to Z20 | L2 |
| Torque tube | SHS40×40×2.6 EXTERNAL backbone (Y−190, Z425) + 4 gussets | FreeCAD clash fix |
| Stiffener | 30×4 flat bolted across top (panel-buzz fix) | audit |
| Motor plate/guard | 300×290×6 pocketed + slotted; guard cover + 2 sides | drive visuals |
| Mass | Deck steel ~64 (CAD-weighed) + hw 7.1 + motor 15 + pack 8 = **~96 mast** | rev2/cad weigh.py + tilt |
| Slope | ~730 mm track for 45° (SF 1.3); pack assumed low-rear | rev2/cad tilt_check.py |

## Duty + field (open until Test A/B)
Grass Es 800 / windage 400@3000 are estimates (`grass_light_maintained`); Test B fixes Es,
Test A fixes windage + droop. Branch mode ≤20 mm green only; stones excluded. 15 m exclusion stands.
