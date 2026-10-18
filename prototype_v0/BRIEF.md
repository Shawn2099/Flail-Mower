# BRIEF — prototype_v0 (775 + nylon-line walk-behind cart)

Independent thread. Nothing here touches `common/`, `flail/`, or `undercarriage/`.
Simplest possible machine: a 4-wheel tube-frame cart carrying a 775/nylon-line cutter.

## Concept (decided)
- Square/rectangular tube frame, simple box; one wheel at each corner.
- Cutter in the middle: **775 DC motor + nylon trimmer line** (drives the cutter ONLY).
- **Rear 2 wheels driven, one motor per side -> tank turn** (skid steer). Drive motors are a
  user-supplied pair (specs + links pending) — *not* the 775.
- **Front 2 wheels idle, fixed, free-rolling** (they drag/skid during a tank turn; keep them light).
- Metal sheet lid on top of the frame (supported at 4+ points) carrying a platform for
  battery + electronics.

## Recommended layout (mm) — from `sim_v0_frame.m` (all gates PASS)
**Small + nimble build.** Keep the 775 cutter; size the machine around it.
- Wheels: 6.5in airless, **OD 170, all FOUR the same** (rear = hub motors; front = plain
  free-rotating on a stub axle in a corner bracket). Same OD keeps the deck level.
- **Wheelbase 260** (axle to axle) | **track 420** (centre to centre) | footprint ~430 L x ~465 W.
- Frame: MS square tube **25 x 25 x 1.6 mm** (SF ~17 static, SF 5.6 at a 3 g kerb — bending is a
  non-issue at this scale). Rectangle: 2 long rails at **X = ±160**, 2 cross members (345 mm) on
  the axles at Y = ±130. The rails sit **inboard of the wheels** (wheel inner face at X = ±187.5
  → 15 mm clear). **The frame's UNDERSIDE sits at Z = 104, i.e. 19 mm above the axle line** —
  any lower and the hub motors' 57 mm axle stubs, their nuts and their washers are buried inside
  the rear cross member, which is its weld line and cannot be notched. One 6 m length of this
  tube covers the frame, the deck posts **and** the handle (that is why 25x25, not 20x20 — see
  `sim_v0_structure.m` Q1).
- Deck lid: **1.6 mm MS/CRCA sheet (16 gauge), 350 L x 355 W, top ~146.5, sitting BETWEEN the
  wheels.** 1.6 mm, not 1.5 — 1.5 is not an Indian stock thickness. They are 170 OD and poke
  ~23 mm above it, so the **wheels stay exposed at the 4 corners** (alternative: notch a wider
  deck — more area, more work). ~17.5 mm above the rail top, doubling as the debris shield and
  the battery platform. Deck edge clears the wheels by 10 mm.
- Cutter: 775 + 200 mm head at frame centre, **cut height 25-60 mm** adjustable.
- Handle to ~900 mm carrying the drive controls (tank turn = two throttles / joystick).
- Est mass **~20.5 kg (design 21 kg)** — one-person liftable, easy to shove around.
- Tank turn **3.25 Nm/wheel** (cont 3.50 / peak 7.21) -> PASS *within continuous torque*.
- Stability: lateral tip **54 deg**; longitudinally the CG sits **46 mm behind centre** (hub motors
  + handle), so the worst case is the **rear at 28 deg** — the thin margin, though still far above
  the 5 deg working grade. Moving the battery forward takes it to 32 deg.
  (Both numbers come from the CAD: CG 155 mm high / 46 mm back, tip 54 / 49 / 28 — see
  `cad/freecad_mass_check.py`. `sim_v0_frame.m` Q4 uses the same 155/46 and agrees.)
- Ground pressure 25.8 kPa (4 wheels, 40 x 50 mm contact patch — turf-safe <50 kPa).
- **Turning envelope**: skid steer pivots about its own centre -> corner radius 247 mm,
  swept circle ~664 mm dia (needs ~0.7 m clear to spin) — the tightest a 4-wheel machine does.
- Sizing rule (Q8 in the sim): **mass scales with size**, so shrinking also lightens, and the
  pivot gets easier. At this mass, 240-300 wheelbase all PASS; 280 x 440 is the next step up.




## Sim / spec state
- `sim_775_trimmer_POC.m` — cutter head sizing (tip speed, line stress, power, operating
  point, duty, sensitivity). **Refactored to load `specs/motor_775_DC.m` + `specs/nylon_line_1p6.m`; runs clean.**
- `sim_v0_drive.m` — traction drive sizing: speed band, traction, tank-turn pivot torque,
  battery, ground pressure. Loads `specs/motor_hub_6p5in_350W.m`. **Runs clean.**
- `sim_775_torque_types.m` — grass + line-type torque sweep (stay on 1.6 mm round).
- `sim_775_SPlectron_check.m` — controller adequacy: the 3 A SEN51 PWM is NOT enough.
- `specs/motor_775_DC.m` — standard 775 electrical + mechanical (44.5 x 66 mm can, 5 mm shaft).
- `specs/nylon_line_1p6.m` — confirmed FASTRIM 1.6 mm round nylon, 75 m spool + D50 head geom.
- `sim_775_swath.m` — swath trade: line length vs aero drag / power (200 mm is a choice, not a limit).
- **`sim_v0_structure.m`** — **material + thickness sizing against India-available stock** (Q1-Q12:
  frame, deck, standoffs, axle, dropouts, carrier, guard impact, handle, fasteners, mass effect,
  alternatives, buy list). 8 sizing gates, all PASS. Base MATLAB, loads the specs. This is what
  sets the numbers in `MATERIALS.md`.
- `specs/motor_hub_6p5in_350W.m` — the two drive hub motors (datasheet + [EST] Kv/Kt/R).
- `cad/gen_adapter_775_ziptie.py` (+ STEP/STL) — 5 mm-bore hub pattern for the 775 shaft.
- `cad/README_adapter_775_ziptie.md` — adapter dims + assembly.
- **`cad/build_v0_frame.py`** — parametric chassis (build123d, the CAD single source of truth).
  Frame + deck + motor carrier + guard + **4 identical 6 mm corner brackets** carrying the front
  stub axles and the rear hub motors; **19 clearance gates** (all PASS) + a STEP re-import check
  + a mass check. Writes `v0_frame.step/.stl`, `v0_layout.step` (with the wheels, the 775 and the
  bought rear axle stack), `v0_parts.json`, `v0_frame_views.svg`.
  Run: `python cad/build_v0_frame.py`.
- **`cad/freecad_build.py`** — FreeCAD half of the check (run inside FreeCAD).
  Re-reads the STEP and verifies it independently: explodes it, matches every solid to
  `v0_parts.json` (centroid + size), runs an all-pairs **volume interference** check, and
  recomputes the steel mass from FreeCAD's own volumes. Saves `prototype_v0.FCStd`.
  Run: `exec(open('C:/Users/malliath/Desktop/matlab/prototype_v0/cad/freecad_build.py').read())`
  **All checks PASS** (31/31 solids matched = 19 fabricated + 12 bought, **0** unintended
  interferences, **5.64 kg** fabricated steel both sides). Its `INTENDED_JOINTS` whitelist is
  now **empty** — no part shares volume with another any more.
- **`cad/freecad_mass_check.py`** — real mass + CG + tip angles from the CAD, instead of an
  assumed CG (run inside FreeCAD, after `freecad_build.py`).
  **CG (+0.0, −46.4, 155.3) mm; tip lateral 54 deg / fwd 49 / rear 28 -> worst 28 deg PASS.**
  **Mass budget closes**: 19.53 kg modelled + discrete, + 1.00 kg misc the CAD omits
  (fasteners, wire, cables) = **20.53 kg vs the sim's 20.50 kg — delta +0.03 kg.**
  It also prints the battery-move sensitivity: battery at Y = +40 mm → CG 34 mm behind,
  worst tip 32 deg (vs 28 deg now).
- **`MATERIALS.md`** — what to buy and why that thickness: the Indian stock list, the member
  schedule with the governing constraint for each part, the buy list, and the mass effect.
- **`tests/test_v0_specs.m`** — `runtests` regression tests for the frozen numbers: the three
  specs, the 200 mm swath, a guard that the frozen **260 x 420 / 21 kg** layout agrees
  across the frame sim, the drive sim, the CAD and the sketch (exactly the drift that once left
  `sim_v0_drive.m` on a stale 450 x 550 / 30 kg build), and guards that **every CAD thickness is
  an Indian stock size**, that the structure sim's picks and the CAD's constants agree, that the
  sim's CG and the mass check's CG agree, and that the raised frame height is the same in the
  CAD and the frame sim. **12/12 pass, base MATLAB only.**
  Run: `runtests('prototype_v0/tests/test_v0_specs.m')`
- Shared input: `common/specs/grass_light_maintained.m` (Es = 800 J/m2).

> **Consistency state (checked):** the frame sim and the drive sim agree to 1e-9 on mass,
> tank turn, ground pressure and layout. All 13 MATLAB files are Code Analyzer clean, and no
> toolbox function is used anywhere in the thread. Every thickness on the drawing is an Indian
> stock size (guarded by `tests/test_v0_specs.m`).

## Drive numbers (from `sim_v0_drive.m`, all [EST] until bench-confirmed)
- Hub motors: 2x Robokits RKI-9011, 36 V 350 W, 2.30 kg each, **170 mm rolling dia**, 25 pole
  pairs, hall + temp, airless tyre, D-axle 16/13.5 mm x 57 mm.
- **Speed is the issue, not power**: 26 km/h top end = 811 rpm, but mow feed is only
  **22-67 rpm (0.2-0.6 m/s)** -> ~21-36x below top speed. Drive must be **current-limited
  (torque mode)**, not voltage-throttled.
- Traction cruising: 1.46 Nm/wheel (21 kg, 5 deg, Crr 0.08) vs ~3.5 Nm continuous -> PASS.
- **Tank turn**: pivot needs **3.25 Nm/wheel** vs 3.50 continuous -> **PASS inside continuous**
  (no current-limited bursts needed). Casters instead of fixed fronts halve it to 1.63 Nm/wheel.
- Battery: mow load is only ~72 W (drive 14 W + cutter 58 W) -> 36 V 10 Ah ~4.0 h / ~1000 m2
  at the walkable 0.35 m/s feed, or ~430 m2 at the 0.15 m/s the cutter was actually sized at.
  Feed the 775 cutter from the 36 V bus via a step-down. Ground pressure 25.8 kPa (turf-safe).

> All `sim_v0_drive.m` inputs are the FROZEN v0 geometry/mass (260 x 420, 21 kg). They were
> 30 kg / 450 x 550 before the freeze, which made the tank turn look MARGINAL at 6.14 Nm/wheel.
> If the size or mass changes, change it in BOTH sims or they will disagree again.

## Cutterside numbers to design against (from the POC sim)
- **Line + motor now CONFIRMED.** Line = FASTRIM 1.6 mm (0.065 in) round nylon, 75 m blue
  spool (Amazon.in B077Y1M12W); motor = standard "regular" 775 (RS-775 class, 44.5 x 66 mm can,
  5 mm shaft). Head = our printed D50 zip-tie hub -> trim to **75 mm/side** -> swath 200 mm.
- Clean cut needs >=50 m/s tip -> >=4,800 rpm at Rtip 100 mm (35 m/s only tears).
- Predicted op point ~5,800 rpm @12 V (Vtip ~61 m/s, ~58 W elec, ~4.8 A) but **12 V is
  duty-limited**; 18-24 V is comfortable. Controller needs >=20 A. 20 A fuse, ammeter, tacho,
  perforated guard, eye protection.

## CAD numbers (from `cad/build_v0_frame.py`, all 19 gates PASS)
- Axis heights: **frame underside 104**, rail centreline 116.5, rail top 129, **deck 144.9-146.5**
  (1.6 mm), wheel top 170. The frame was lifted 19 mm above the axle line to clear the hub
  motors' axle stack; the deck height and the wheel poke (~23 mm) are unchanged, so the deck
  posts shortened to ~16 mm.
- Cutter stack (at max cut height 60): hub 60-75, 775 can **75-141**, deck underside 144.9 →
  **3.9 mm** of can-to-deck clearance. That is the whole vertical budget — do not grow the hub.
- Motor carrier: **Ø120 x 5 ring + two 60 x 95 arms** on the cross members, bore 45 + 4 x M5 on
  R35 (band clamp). The ring OD was never bound by anything — Ø45 bore + M5 on R35 only needs
  OD 85 — so Ø160 was cut to Ø120 (−0.35 kg). Was a 240 x 300 x 5 slab (2.8 kg) before that.
- Guard band OD 244 x 55 tall x **2.5 mm** (Z 15-70) → 40 mm clear of the wheels; line tip 62 mm clear.
  Two 30 x 2.5 tabs, now 34 mm tall, tie its rim to the cross member's underside.
- Frame corners: **4 identical 6 x 60 x 60 MS plates**, one part for all four corners — front
  bored Ø20 for the **stub axle** (welded in the bore, retained by a washer + Ø4 split pin);
  rear bored Ø16.2 with a flat for the motor's **16 / 13.5 D-shaft** (the flat reacts the torque).
  The full-width notched Ø20 front axle is **gone**: all four corners share one part, cut and
  drilled as one batch. `freecad_build.py`'s `INTENDED_JOINTS` is now **empty** — no part shares
  volume with any other.
- Rear axle stack (bought, now modelled): the hub motor's own Ø16 x 57 D-stub, an M16 nyloc
  (27.8 across corners) and a plain Ø30 washer. They clear the raised frame by 11 / 5.1 / 4.0 mm.
- Mass: 4 tubes 1.36 kg, fabricated steel **5.64 kg** vs the sim's 5.70 kg assumption (−0.06).
- Turning: corner radius 247 mm, swept circle ~664 mm dia.
- `sketch_v0.m` rail_x corrected 185 → **160** (185 ran the rails into the wheels).

## Open items
1. **Front wheels** — fixed free-rotating (stub axle, not a dead axle). Must be OD 170 to match the
   rears; keep them smooth/hard so they skid rather than dig in.
2. **Drive controller** — dual 36 V 350 W BLDC (one per hub), independent left/right for tank
   turn. Pick the throttle scheme (2 throttles / joystick / MCU) and current-limit it.
3. **Bench-confirm** hub Kv + phase R to lock the [EST] torque numbers.
4. **Cutter supply** — 36 V -> 24 V (or 12 V) step-down; the sim picks the cutter voltage.
5. **Cut-height adjust** — the 775 shaft is only 17 mm long, so the 25-60 mm range cannot be
   slid on the shaft. Either a spacer sleeve between the hub and the motor face, or a slotted
   bracket that moves the whole motor + hub (35 mm of travel). Deck has only 4 mm of spare
   height, so the motor must not move *up*.
6. **Handle + controls** — layout, and how tank turn is driven from the operator's hands.
7. **Front wheel sourcing** — 2 more of the same 6.5in, or a lighter plain 170 mm wheel.
8. **Fore-aft balance** — the CAD puts the CG 46 mm *behind* centre (hub motors + handle), so the
   rear is the thin tip margin (28 deg, though the grade is only 5). Mount the battery forward of
   centre and the mass check says it goes to 32 deg. Free to do — just a layout choice.
9. **Guard lip** — add the 15-20 mm downward lip on the guard band (free, cut from the same
   strip). See `MATERIALS.md` §7.
10. **Rear axle retention** — bench-confirm the hub motor's D-flat clocking and the shaft shoulder
    / spacer length before the bracket is welded: the stub is 57 mm and the bracket sits 9 mm
    inboard of the wheel, so the shoulder must land at 178.5 (X) or a spacer is needed. The
    nut/washer clamp must not foul the cross member (now cleared by 4-5 mm).

