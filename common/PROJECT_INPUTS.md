# Project Inputs — Tracked Flail Mower, 500 mm (USER-SUPPLIED)

> Everything in this file was supplied by the user (images + chat). 
> Values marked **[EST]** are estimates filled in where the datasheet was silent.
> Nothing here is a recommendation — see `sim_*.m` outputs for results.

## 1. Machine intent
- Tracked undercarriage with own chassis carrying a flail mower deck.
- Working width: **500 mm = drum width** (no adjustment needed there).
- Drum diameter is a **FREE variable — find the optimum**, do not restrict to 2–3 in.
- Scope: **MVP build** — simplest off-the-shelf construction, one config to test first.
- Drive: PMSM motor **3 kW or 4.5 kW** (see §3). 1.2 kW BLDC ruled out by sim.
- Duty: **light grass only, 2–3 in (50–75 mm) long, regularly mowed, clean known ground — no rocks, branches, or surprises.**

## 2. Blades (Meevin Agro, boron steel 30MnCrB5)

| Blade | Length | Width | Thick | Weight | Hole | Hardness | Feature |
|---|---|---|---|---|---|---|---|
| Straight mulcher | 130 mm | 58.0 mm | 8.0 mm | **340 g** | Ø17 mm | 46–50 HRC | flat flail |
| J-type mulcher | 131 mm | 58.5 mm | 8.0 mm | **400 g** | Ø17 mm | 46–50 HRC | 125° hook bend |
| Hammer | R110 tip radius | 130 mm | measure (1050 g user-weighed) | Ø16.25 mm | 47–51 HRC | double-edge, blunt impact edge |
- All three blades look **blunt/impact type, not razor sharp** (per photos) → needs 35+ m/s tip speed, not 30.
- Sources: `multure blade straight type.jpg`, `multure blade j type.jpg`, `hammer blade.jpg`.
- ⚠️ Open: hammer blade **thickness** still not on datasheet — caliper it (mass resolved: 1050 g).

## 3. Motors (Mecwin EV mid-drive, 48/60/72 V)

| Motor | Rated | Max speed | Shaft | Source |
|---|---|---|---|---|
| L3-BLDC | 1.2 kW @ 3300 rpm | 3500 rpm | helical gear, 25 N·m stall | `Screenshot_...225138_Chrome.jpg` |
| PMSM mid | 3 kW | 4000 rpm | keyed variant (confirm bore 24/25/28 at order) | `Screenshot_...225241_Chrome.jpg` |
| PMSM mid | 4.5 kW | 4500 rpm | keyed variant | `Screenshot_...225249_Chrome.jpg` |
- Treat nameplate as **peak (EV) rating**; assume ~65% continuous in mower duty **[EST]**.
- Controller: Mecwin PMSM 300 A, Hall/encoder, GUI programmable, ₹16,386 (`Screenshot_...225210_Chrome.jpg`).
- ⚠️ Rotor RPM **must be capped in GUI (2200 grass / 2500 cap / 3000 hard ceiling)** — uncapped tip speed hits 70–80 m/s.

## 4. Tab / blade combinations under study
- **C1:** 1× J single per tab, 10 stations (hook direction alternates L/R).
- **C2:** 1× straight single per tab, 10 stations, 36° helix. **(MVP)**
- **C3:** 1× hammer per tab. **Parked** (Ø16 pin fails at 1050 g).
- **C4 (triple on one pin): REJECTED** — three 58 mm blades cannot share one tangential pin;
  pin bending 262+ MPa with no upsize path. Approved form is **C5: alternating S/J singles**.
- Mount: **single-hole bolt-mount** (one fin lug + tangential shoulder bolt + nyloc per blade;
  R-clips rejected — they walk off at 2500 rpm). Shackles NOT needed in this pattern.
  Ø17 is non-standard: turned shoulder bolts with M14 thread (lathe job).
  Reference photos (eg_rotor, fab photo) show the *narrow-blade* variant: axial pins
  between lug pairs, ~20 stations/m. Ours is the *wide-blade* variant of the same law.

## 5. Simulation-ready spec files (`specs/`)
Each file = one component, returns a struct: `blade_straight_mulcher`, `blade_jtype_mulcher`,
`blade_hammer`, `motor_Mecwin_BLDC_1p2kW`, `motor_Mecwin_PMSM_3kW`, `motor_Mecwin_PMSM_4p5kW`,
`controller_Mecwin_PMSM_300A`, `grass_light_maintained`, `machine_500mm_tracked`,
`drum_50NB_medium` (optimum), `drum_65NB_heavy` (roomy alternative), `tab_msflat`, `pin_EN8`, `shaft_bearing_25`.

## 7. Open decisions (user-confirmed Oct 2026)
- Blades **not purchased yet** — hang-test CG numbers pending; sims run on estimates.
- Runtime target: **20–30 min (MVP)** — pack sized by `sim_battery_speed.m`.
- Pack voltage open: **48V vs 72V** — 48V must be confirmed to hold 2500 rpm.
- Forward speed **not finalized** — swept 0.5–1.5 m/s in `sim_battery_speed.m`.
- Blade counts from `sim_blade_count_shape.m`: **C1=10 singles, C2=10, C3 parked, C5=10 mixed**.
- J-blade audit (Oct 2026): all 9 datasheet values verified; chord 105±5 mm → run C1 at **2300 rpm**, not 2200.

## 6. Simulations (`sim_*.m`, base MATLAB only)
Verified by execution in MATLAB R2026b (Oct 2026) — all run clean.
- `sim_mvp_rotor.m` — master decision chain, prints the build sheet.
- `sim_battery_speed.m` — pack voltage/Ah + forward-speed sweep.
- `sim_light_grass_rotor_sizing.m` — tip speed / power / motor margin sweep.
- `sim_rotor_structural_sizing.m` — drum dia sweep, station loads, pin/tab/drum/bearing checks.
- `sim_combo_efficiency.m` — C1–C4 energy-per-hectare ranking + battery runtime.
- `sim_blade_count_shape.m` — blade count + shape optimization per config.
- `sim_station_packing.m` — physical packing limit in 500 mm.
- `sim_feasibility_edge_cases.m` — grass/brush/rock feasibility + protection spec.
- `sim_calibrate_grass.m` — field-test calibration (needs measured data).
- `sim_drum_specsheet.m` — constraint-framework pipe selection + dimension sheet.
- `sim_enclosure_design_v2.m` — box-5 housing + fab sheet + §12 CAD closed-loop check
  (reads `cad/enclosure_cad.json`, verifies CAD-measured corners/clearance/gap/mass). (v1 = superseded volute ref).
- `sim_structural_audit.m` — resonance + member checks.
- `cad/build_enclosure_box5.py` → STEP/STL; `cad/tilt_check.py`, `cad/weigh.py`, `cad/export_dxf.py` → `cad/dxf/`.
- `sim_benchmark.m` — real-product benchmark audit (Orec, Great Plains, tractor rule).
- `build_drum.m` — parametric 3D + STL + laser DXF + coverage proof (the build itself).
