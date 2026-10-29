# UC-V2 DESIGN AUDIT - 2026-10-29

Scope: re-run every v2 sim, rebuild the canonical FreeCAD assembly headless, measure
every STEP solid, and check the y-stack / keyway / chain-plane details against the
drawings-to-be. Frozen sizes (6 mm plate, 8 mm sprocket, SHS40) were not changed.

## Verdict

**Structure and sizing pass.** All sim gates print PASS after the corrections below.
The as-drawn machine is **186.9 kg** incl tracks + motors (v3 simple spool; 201.1 kg before the roller/idler change), **L1278 x W826 x H441**.
The old "~165 kg / 732 wide" figures were paper estimates and are superseded.

**V3 update (2026-10-29 later):** rollers and idlers replaced with the simple spool
(pipe + backplate + welded 65/52 seat + loose spacer; no Loctite/ring stacks).
Mass **186.9 kg**. P-002/P-003/GA-003 are superseded by the v3 sheets.

## Sim results (re-run 2026-10-29)

| Sim | Result |
|---|---|
| sim_v2 | ALL PASS; mass 186.9 kg <= 205 ceiling (target 165 missed +21.9) |
| sim_v2_margins | closest member beam bend 0.76; plates 0.06-0.47 |
| sim_v2_assemble | ALL PASS; chain plane 140; 826 overall |
| sim_v2_turn | flat pivot 250 kg PASS; 400 kg mu0.6 flat REVIEW; never pivot on slopes |
| v2_fatigue | beam weld 25.7k hr; all > 1000 hr |
| v2_pde_kt | Kt hole 3.20 / slot 2.30; flange grip SF 24 (Kt N/A, no slip) |
| v2_optimo | 5 mm/SHS32 feasible on paper (-13.9 kg), rejected for shop tolerance |
| v2_roller_trade | one-unit roller proposed, NOT adopted (CAD stays paired discs) |
| v2_wheel_material | MS-fab wins; PU rejected |
| sim_battery_uc | 57 / 30 / 23 min (flat / 250-15deg / 400-15deg) |
| v2_duty_batt | 50 min duty mix; motor Cu 52 C |

## Findings fixed

| # | Finding | Evidence | Fix |
|---|---|---|---|
| 1 | Axle L240 engaged only 17 mm of the 50 mm UCFL208 bore | axle bbox y140..380 vs UCFL 363..413 | axle **L300** (110..410), 47 mm engagement; 0.6 m bar = 2 axles |
| 2 | Axle keyways at y184..216 / 304..336 matched **no** part | STEP sections + FreeCAD bboxes | keyways **142..157** (48T hub) and **238..282** (72z hub) |
| 3 | 48T wheel had no axial stop (2 mm overhang off axle end) | wheel 138..142, axle started 140 | hub 142..157 butts inner plate + **D40 collar 126..138** |
| 4 | 72z hub free to walk on the axle | hub 238..282, nothing at either face | **D40 collar 282..294** |
| 5 | Chain plane 3-5 mm out; L/R wheels differed 4 mm | wheel 140, pinion 137; L wheel -144 | both **140**; L-side base corrected; pinion base 143/-137 |
| 6 | Docs said overall 732; CAD is 826 | FreeCAD envelope W826 (UCFL 363..413) | docs/BOM/json updated: 826 UCFL, 726 plates, 700 track, 820 axles |
| 7 | Docs had no height/length | envelope L1278 H441 | added |
| 8 | Mass rollup 205 kg from hand constants | STEP-measured parts | **201.1 kg** via `cad/mass_audit.py` -> `mass_audit.json`; sim reads it |
| 9 | BOM shafts "2 m, L220" could not reach collars at 375 | shaft L260 needed (130..390) | **2.2 m, 8 x L260** |
| 10 | BOM chain "58L" too short for C=168.7 | 60 pitches needed; 60L at C=170.15 | **60 links** |
| 11 | ASSEMBLY said "8xM12 ea" (16) vs BOM 28 | 4 mid joints x4 + 2 rear x4 + 2 front x2 | **28 total (14/side)** |
| 12 | BOM "6 keyways" | 4 axle + 2 hub76 + 2 pinion | **8 keyways** |
| 13 | v2_pde_kt printed flange 248 MPa REVIEW | free-hole Kt applied to a friction-grip joint | slip check **SF 24**; Kt N/A (no slip); gate PASS |
| 14 | Roller shaft used 32 Nm (half the overhang moment) | 1.7 kN x 38 mm = 65 Nm | 65 Nm -> **42 MPa** (was 21), still PASS |
| 15 | Idler D200 on R105.26 | 0.7 mm radial preload on 99.26 belt inner | accepted (rubber), stated in sim/assembly |
| 16 | UCFL bolt spacing 120 vs plate slots 90 nominal | ref STEP holes y=+-60 | slots 60 long take bolts at z 43/163 - **fits** |
| 17 | Spacers not in BOM | 4 x dia48 x 200 between plates | added to mass/BOM |
| 18 | BOM SHS40 "L320 x5" | CAD has 4 beams | **4 fitted + 1 spare** |
| 19 | Roller shell called "cut 40" + 2x6 cheeks -> 52 wide | STEP drum is 174.6 cm3 = 28 shell + 2 cheeks | **shell cut 28**, 2x6 cheeks, 40 overall; BOM/STOCK/build script fixed |
| 20 | Idler had NO connection between tread rings (r75..100) and hub (r32.5) | idler_disc volume = 5 rings + hub only | **5 rings + 1 web OD150/ID65x6 inside the bore**; tread stays 40 wide; CAD rebuilt |
| 21 | Lift lugs at z210 were buried inside the motors | Motor z250..440, y4..134; lug y70..130 | moved **under the rear tie, z130..210**; check Lift1 vs MotorR 74 mm |

## Deliverables

- `drawings/UCV2_DRAWING_PACK.pdf` - 14 x A3, bookmarked (GA-001..004, P-001..010).
- `drawings/README.md` - sheet index, sources, regeneration commands.
- `MASS.md` / `cad/mass_audit.json` - per-part mass, read by `sim_v2`.
- `cad/build_v2_axle.py`, `cad/build_v2_idler.py` - corrected solids + DXF.

## Open items (not blocking the drawing pack)

1. **Width 826 vs 750 mock.** UCFL208 flanges set the width. Mounting them on the
   inboard face of the outer plate drops it to ~760 and still leaves 47 mm axle
   engagement, but puts the housing 9 mm from the belt inner. Decision needed before
   a 750 mm transport limit is imposed.
2. **48T wheel hub.** The CAD uses a 4 mm reference tooth plate at y=140; the donor
   wheel hub is assumed 15 mm (142..157). Confirm hub width/key length before boring.
3. **Motor mount bolts** (size/grade) and rail slot positions are not yet on a drawing;
   see sheet P-007 note.
4. **Mecwin winding R** (0.05 ohm assumed) - confirm before summer trials (FMEA #10).
5. Track sample horn height (for the rejected one-unit roller) - only relevant if the
   roller trade is adopted later.
