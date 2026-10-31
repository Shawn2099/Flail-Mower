# v2_optimized_claude - status (2026-10-31)

Folder `undercarriage/v2_optimized_claude/` is a **copy of v2 plus a new parametric build** (`cad_v4/`). The frozen v2 files are unchanged and are not used by `cad_v4`.

## What this design is
Rubber-track undercarriage for a Kerala coffee-plantation flail mower. ACETRAX 180x60x37 track (link count 37 = repo size code, NOT in the PDF), CUSTOM 12-tooth track sprocket (pitch 60; chosen by opt_sprockets.m for stability, track bend radius 110 mm), gauge 860, overall width 1168 mm (limit 1190), single-stage 428 chain drive 13T (Apache RTR 160 front) -> 52T (MT-15 rear) on each side, bolted to a flange hub so tooth counts are swappable (env vars UC_PINION_T / UC_WHEEL_T / UC_SPR_Z), BM1418ZXF 750 W 48 V geared motor (1:6 in-built), speed 5.2 km/h top / 1 km/h mowing at 19% throttle, one-piece centre-groove idler (8NB pipe rims + hub tube), three two-drum roller spools per side, 6 mm plates with windows and pockets, SHS40 cross beams bolted into tapped pads, two UCFL208 per axle.

## Rebuild
- `python -I cad_v4/build_uc_v4.py` -> `uc_v4_assembly.step`, `uc_v4.json` (mass, gates, drive), `dxf/` (10 laser parts), `uc_v4_bom.csv`, `parts/*.step`, `preview/cat_*.step`. All inputs: the parameter block in the script + `cad_v4/catalogue.json`.
- FEM (FreeCAD 1.1 GUI via the FreeCAD MCP): `CASE='vertical'` / `'lateral'`; `exec(open('.../cad_v4/fem_plate.py').read())` -> `parts/fem_plate_result*.json`. (CASE='ucfl' is a known issue: no node loads generated - do not use.)
- Sim: `run('sim_uc_v4.m')` (MATLAB, base only) reads the JSON files. Motor sizing details: `motor_bm1418zxf.m`.
- `*_backup.py` and `patch_*.py` files record each edit step; the current `build_uc_v4.py` is the source of truth.

## Results now
- 23 computed CAD gates pass (12 'measured', 11 'by construction' - tagged in uc_v4.json), 0 interference (> 20 mm3).
- Mass 185.1 kg incl. 8.5 kg of labelled allowances. v2 frozen = 185.7 kg, BUT not like for like: v4 uses lighter catalogue inputs (motor 7.12 vs 9.0, UCFL 1.5 vs 2.2, track 17.1 vs 18.0 kg) and omits v2's deck mounts/lift lugs (4.5 kg) and misc (1.8 kg). At equal scope v4 is roughly 9 kg HEAVIER than v2. Treat the weight reduction as NOT achieved yet.
- FEM inner plate, 6 mm, pad faces restrained (CalculiX via FreeCAD): vertical max 13 MPa; lateral max 79 MPa, p99 30 MPa (allowable 167, yield 250). Mesh ~11 mm tet10 under-resolves bending: indicative only, convergence check still to do.
- Drive at design mass 306 kg (60 kg deck ASSUMED): holds 10 deg at rated torque (0.96x, rr 0.15); wide-arc turn 1.06x and spin turn 1.36x need the motor's UNPUBLISHED overload. At 5 km/h up 10 deg the motor is at ~94% of rated power.
- opt_sprockets.m: ga + enumeration agree -> 12T track sprocket, 13T pinion, 52T wheel.

## Not done / open (see also TRACK_CHANGE_SOP.md, WELD_SCHEDULE.md)
1. **Motor mount + chain take-up not designed** (motor is a placeholder cylinder; no shaft/mount drawing exists - ask yalu@wzyalu.com).
2. Chain guards, lift lugs and deck mounts (0 kg or allowance only). 52T wheel bottom is 36.6 mm above ground (plate edge 30). The MT-15 chain pitch (428?) and 12-tooth track-sprocket tooth form are UNVERIFIED.
3. Unverified inputs: track link count / minimum bend radius / roller line load / is the gap between the horns rollable (ask ACETRAX); UCFL208 flange thickness; 8NB wall; motor mass (3.0 / 7.12 / 10.66 kg listed) and peak torque; soil resistance; deck mass.
4. Extra FEM cases (frame twist, track pretension) are analytic only in the sim; the UCFL plate-load FEM did not run.
5. Turned-part drawings with fits and the A3 layout pack are NOT produced (Opus review blocker B3); DXF units are mm now (v2's were tagged metres).
6. Nothing outside this folder was changed.

**Tracker:** see `TRACKER.md` for the task list, decisions and how to continue.
