# Flail Mower Rotor — Build Guide (what we did and why)

## 1. Goal
500 mm tracked flail mower deck for light maintained grass (50–75 mm, clean plots).
MVP first: cheapest build that provably cuts, with upgrade paths that reuse the drum.

## 2. Inputs (all in `PROJECT_INPUTS.md`, specs in `specs/`)
- Meevin Agro boron-steel blades (30MnCrB5): straight 340 g / J 400 g / hammer 1050 g.
- Mecwin EV mid motors: 1.2 kW (ruled out), 3 kW (picked), 4.5 kW (later).
- 20–30 min runtime target; 48V vs 72V open pending Mecwin's rpm confirmation.

## 3. Decisions and why
| # | Decision | Why |
|---|---|---|
| 1 | 3 kW PMSM | 1.2 kW runs at 127% continuous; 3 kW at 35–60%; 4.5 kW buys nothing for grass |
| 2 | 50NB Medium drum (60.3×3.65) + 6mm tabs | Lightest IS-1239 pipe passing tip≥35 (with 3% droop), weld, sag, critical gates |
| 3 | 10 straight singles, 36° helix | Leanest count covering 500 mm (100%, 5.8 overlap); exhaustive search optimum at 558 W |
| 4 | Single-fin + tangential shoulder bolt + nyloc | Only mount fitting 58 mm punched-eye blades with full coverage; pin 61/180 MPa @cap |
| 5 | 2200 work / 2500 cap / 2100 floor | Blunt floor 35 m/s needs ≥2114; cap keeps hammer-less pins safe |
| 6 | Up-cut front, rear discharge, 2x SPZ belt + 12 N·m electronic torque limit | Rock strike spikes 160× nominal; current-cap + belt slip is the fuse |
| 7 | Pack per §8 (48V vs 72V open) | Sim sizes 72V 70Ah; field pack waits on Mecwin rpm confirm |
| 8 | Rear roller Ø114 + skids, 40–80 mm | Skids alone scalp; roller is the height reference (industry pattern) |

## 4. What each sim does (run order)
1. `sim_mvp_rotor` — master chain, prints build sheet. Run first.
2. `sim_rotor_structural_sizing` — drum sweep, pin/tab/drum/bearing proof.
3. `sim_combo_efficiency` + `sim_shape_pattern_search` — why straight×10 (exhaustive).
4. `sim_blade_count_shape` + `sim_station_packing` — counts fit and cover.
5. `sim_battery_speed` — pack + speed sweep, 48V rpm warning.
6. `sim_feasibility_edge_cases` — grass/brush/rock + stem-level cut proof (17×).
7. `sim_benchmark` — six metrics inside the real-product envelope (Orec, Great Plains).
8. `sim_2J_pattern` + `sim_2J_loads` — the J upgrade (20 blades, perfect balance).
9. `sim_calibrate_grass` — turns field tests into true Es + windage (needs measured data).
10. `sim_drum_specsheet` — constraint-framework pipe pick + 16-line dimension sheet.
11. `build_drum` / `build_drum_2J` — 3D + STL + laser DXF + renders + coverage proof.
12. `sim_enclosure_design_v2` — box-5 housing + fab sheet (v1 = superseded volute ref).
13. `sim_structural_audit` — resonance + member checks. 14. `cad/` scripts — box5 STEP/STL, tilt, weigh, DXFs.

## 5. Shop package
`MVP_ROTOR.md` (authoritative dims) + `common/cad/drum_disc.dxf` (laser: Ø140, bore, BCD holes,
10 station marks = helix jig) + `drum_rotor.stl` (visual check). Clamp a straightedge
across matching disc marks, tack each fin to the line, weld 4 mm fillets (E7018),
static-balance, done.

## 6. Commissioning
Test A (no-load amps @3 rpms → windage + droop ≤3%), Test B (amps over timed 100 m →
true Es). Feed into `sim_calibrate_grass.m`, re-run suite, file results.

## 7. Upgrade paths (same drum)
- **2J finish** (767 cuts/m, perfect balance): 20 J-blades, 2300 rpm, hooks forward.
- **Brush**: same rotor, slow to 0.5 m/s (envelope in feasibility sim).
- **Hammers**: phase 2 only — needs forked tabs + ≤2500 cap (Ø16 pin fails otherwise).

## 8. Open items
Mecwin 48V-rpm confirmation • Mecwin keyed-shaft bore (24/25/28) + foot pattern • Test A/B data •
blade hang-test CGs (refines loads ~10%) • hammer thickness (caliper, phase 2).
