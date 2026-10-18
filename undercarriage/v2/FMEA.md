# V2 FMEA (grounded in sim_v2 / margins / PDE-Kt / fatigue / duty runs, 2026-10-14)

Ratings 1-10. RPN = S x O x D. Occurrence from Miner lives + margins; Detection = shop/field check strength.

| # | Item / mode | Effect | S | O (evidence) | D | RPN | Action (done / to-do) |
|---|---|---|---|---|---|---|---|
| 1 | Beam SHS40 yields at midspan (400kg/20° burst) | Frame folds, deck drops | 9 | 2 (peak 114/225, life 25k hr) | 4 (visual bow check) | 72 | KEEP section; re-check if deck >150kg |
| 2 | Flange hole-edge crack | Joint loosens, beam walks | 7 | 2 (friction-grip bypass, peak 74/225 w/ preload) | 5 (torque audit) | 70 | TVS 8.8 + nylock + 80Nm torque + paint-mark (ASSEMBLY) |
| 3 | Plate slot-end crack (idler/UCFL slots) | Shaft cocks, track throws | 8 | 2 (peak 163/225, life 218k hr) | 5 (slot dye-check at service) | 80 | KEEP 6mm; break slot edges at build |
| 4 | Roller shaft bends (stump shock) | Bearing binds, flat spot | 6 | 1 (21/150, life ~inf) | 6 (felt play) | 36 | None — D25 locked by 6205 bore |
| 5 | Drum/ring weld toe fatigue | Disc wobbles, belt wear | 6 | 1 (tau<3MPa, life 25k+ hr) | 6 (wobble check) | 36 | Min 3mm fillet stays on drawing |
| 6 | M12 joint loosening (mow vibration) | Fretting, hole oval | 7 | 2 (TVS nylock everywhere structural) | 4 (paint-mark nuts) | 56 | Torque-mark all M12s at build; modal check only if loosening seen in trials |
| 7 | 6205 seizure (mud ingress) | Track drags, driver trips | 6 | 3 (2RS on plantation soil) | 3 (noise/heat felt) | 54 | Grease caps on BOM; blow-out at service |
| 8 | 428 chain snap (debris jam) | One side dead, slope skid | 8 | 2 (SF12) | 3 (guard + stretch check) | 48 | Guards fitted; carry spare link set |
| 9 | Track throws (tension loss) | Immobilised | 7 | 2 (33/50 tension PASS) | 4 (sag gauge 30-40mm) | 56 | Sag check in FAB_INSTALL doc |
| 10 | Motor overtemp (summer 40C, long 15° pulls) | Demagnetise/derate | 7 | 2 (52C vs 120C class, R unconfirmed) | 5 (hand-check) | 70 | CONFIRM Mecwin R vs datasheet; add temp sticker |
| 11 | Battery shortfall (400kg/15° all day) | 23min worst vs expected 1hr | 5 | 4 (duty-mix 50min; worst 23min) | 3 (fuel-gauge habit) | 60 | Quote 2nd 48V20Ah as field spare; duty-mix briefing |
| 12 | Slope tip (CG600 + side slope) | Rollover | 10 | 1 (tilt 31/40 PASS, rule: no pivot on slope) | 4 (operator rule) | 40 | Rule placard on machine; CG audit at deck fit |

Highest RPN = plate slot-end crack (80); bolt loosening dropped 84->56 with the TVS-nylock rule. Everything structural carries margin evidence.
