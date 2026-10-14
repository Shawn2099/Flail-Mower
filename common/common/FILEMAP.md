# FILEMAP — which file does what, and in which order to run them

Layout: `common/` (shared once) + `flail/revN/` (one folder per housing revision).

## Run order (base MATLAB only)
Run `common/` sims from `common/`; run `flail/revN` sims from their folder (they link `../../common/specs`).
1. `common/sim_mvp_rotor.m` — master chain: tip, power, pin/tab, drum, battery + build sheet.
2. `common/sim_drum_specsheet.m` — pipe selection by constraint gates + 16-line dimension sheet.
3. `common/sim_rotor_structural_sizing.m` — drum sweep, station loads, pin/tab/drum/bearing, spin-up.
4. `common/sim_light_grass_rotor_sizing.m` — blade×drum×rpm matrix, motor margins.
5. `common/sim_blade_count_shape.m` + `common/sim_station_packing.m` — count/shape optimum + fit in 500.
6. `common/sim_combo_efficiency.m` + `common/sim_shape_pattern_search.m` + `common/sim_pattern_optimize.m` + `common/sim_opposing_pair.m` — config ranking, pattern search.
7. `common/sim_battery_speed.m` — pack voltage/Ah + forward-speed sweep.
8. `common/sim_benchmark.m` — product-envelope audit. `common/sim_feasibility_edge_cases.m` — grass/brush/rock + guards.
9. `common/sim_2J_pattern.m` + `common/sim_2J_loads.m` — J-blade upgrade (loads, balance).
10. `flail/rev2/sim_enclosure_design_v2.m` — box-5 housing + fab sheet + §12 CAD closed-loop check
    (reads `flail/rev2/cad/enclosure_cad.json`). (`flail/rev1/sim_enclosure_design.m` = superseded volute.)
11. `flail/rev2/sim_structural_audit.m` — resonance + member checks.
12. `common/build_drum.m` / `common/build_drum_2J.m` — rotor STL + disc DXF (→ `common/cad/`) + renders.
13. `common/sim_calibrate_grass.m` — field data in (needs Test A/B measurements).

## CAD
- `flail/rev2/cad/build_enclosure_box5.py` — THE BUILD → `enclosure_box5.step/.stl` + `enclosure_cad.json`.
- `flail/rev2/cad/tilt_check.py` — deck CG + track-width table. `flail/rev2/cad/weigh.py` — per-part masses.
- `flail/rev2/cad/export_dxf.py` → `flail/rev2/cad/dxf/` — 8 plasma files (CUT/PILOT/BEND/NOTE).
- `flail/rev1/cad/` — superseded volute/faceted scripts + STEP/STL (reference only).
- `common/cad/` — rotor shop files (`drum_rotor.stl`, `drum_disc.dxf`).

## Specs (`common/specs/`, one struct per file)
Blades: `blade_straight_mulcher` (MVP) / `blade_jtype_mulcher` (2J) / `blade_hammer` (parked).
Rotor: `drum_50NB_medium` (optimum) / `drum_50NB_heavy` (fallback) / `drum_65NB_heavy` (roomy) /
`tab_msflat` (6 or 8) / `pin_EN8` / `shaft_bearing_25` / `config_2J_opposing`.
Drive: `motor_Mecwin_BLDC_1p2kW` (ruled out) / `motor_Mecwin_PMSM_3kW` (picked) /
`motor_Mecwin_PMSM_4p5kW` (later) / `controller_Mecwin_PMSM_300A`.
Field: `grass_light_maintained` (Es=800 EST) / `machine_500mm_tracked`.

## Docs (`common/`)
- `MVP_ROTOR.md` — authoritative rotor dims. `GUIDE.md` — decisions + run order + shop.
- `PROJECT_INPUTS.md` — user-supplied inputs only (not recommendations).
- `REFERENCES.md` — books, standards, benchmark products. `COMPONENTS.md` — frozen per-part values.
- `step_*.m` + `medium.stp` + `step_solids.mat` — reference-design measurement chain.
- `prototype_1/` (root) — frozen archive snapshot (refreshed at handover).
