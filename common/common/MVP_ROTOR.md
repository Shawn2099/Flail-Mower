# MVP ROTOR — FINAL BUILD DOCUMENT (all mm unless noted)
Generated from executed MATLAB sims (R2026b). Supersedes all chat summaries.

## Rotor assembly (~12.3 kg)
| Part | Spec | Qty | Mass |
|---|---|---|---|
| Tube | 60.3 OD × 3.65 wall × 500 LG, IS 1239 50NB Medium | 1 | 2.5 kg |
| End discs | Ø140 × 8 MS plate, Ø25 bore + keyway, 6× Ø10 on BCD90, 10 station marks | 2 | 1.9 kg |
| Shaft | Ø25 × 700 EN8 bright | 1 | 2.7 kg |
| Fins (tabs) | MS flat 50W × 40H × 6T + 2 spacer washers/eye, hole Ø17.2 at 20 above tube surface | 10 | 1.0 kg |
| Shoulder bolts | Turned Ø17 × 40, M14 thread, 10.9 grade + spacer + washer + nyloc | 10 | 0.8 kg |
| Blades | Straight mulcher 340 g, Ø17 hole (Meevin Agro) | 10 | 3.4 kg |
| Bearings | UCP205 sealed, 600 span | 2 | — |

## Layout
- Stations x = 15 + k×52.2 mm (k = 0..9) → 15…485 mm. Helix 36° steps.
- Cutting circle Ø316 (Rcut 158). Tip 36.4 m/s @2200, 41.4 @cap 2500.
- Balance: static, trial weights on discs. Disc runout ≤ 0.3 mm after welding.

## Drive + control
- Motor 3 kW PMSM; work 2200 rpm, controller hard cap 2500, floor 2100.
- Rotation: UP-CUT at front (verify clippings exit rear flap).
- Drive 2x SPZ belt 1:1 (taper-lock pulleys); electronic torque limit = 12 Nm via controller current cap, belt slip as backup. No mechanical slip clutch.
- Pack: sim sizes 72V 70Ah (5.9 h mowing); MVP field pack 48V 20Ah PENDING Mecwin 2500-rpm confirmation.

## Deck interface
- Housing inner 550 W; box-5 roof flat Z405 (187 above centre); centre 218 above ground.
- Full-width rear roller Ø114 (100NB-L stock) + skids (cut 40–80 mm); double rubber-strip front curtains.
- 4× rubber mounts + 2 lift points; ~64 kg deck steel (CAD-weighed) + ~30 mast (rotor hw 7.1, motor 15, pack 8) = ~96 before chassis.

## Commissioning (fills the last estimates)
- Test A: no-load amps @2000/2200/2500 → windage curve + droop check (≤3%).
- Test B: amps mowing timed 100 m → true Es → paste into `specs/grass_light_maintained.m`.
- Feed both into `sim_calibrate_grass.m`; re-run suite; file results.

## Files (`common/cad/` for shop files, `flail/rev2/cad/` for housing CAD)
`build_drum.m` → `common/cad/drum_rotor.stl` + `common/cad/drum_disc.dxf` + renders.
`sim_drum_specsheet.m` → dimension sheet (16 lines, verified). J-upgrade: same drum,
10 J-blades hooks-forward at 2300 rpm. Hammers: parked (phase 2, forked tabs required).
