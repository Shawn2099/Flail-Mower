# TRACKER - v2_optimized_claude (READ THIS FIRST in any new session)

Single source of truth for **what was decided, what is done, what is open, and how to continue**. Update it at the end of every work session
(add a line to the Change log, move items between the tables, never delete history). Companion files: `STATUS.md` (current numbers), `WELD_SCHEDULE.md`, `TRACK_CHANGE_SOP.md`.
Last updated: 2026-10-31. Nothing in this folder has been git-committed (`?? undercarriage/v2_optimized_claude/` is untracked). Do NOT edit frozen v2 (`undercarriage/v2/`) or `prototype_1/`; all work stays inside this folder.

## 1. Goal and standing instructions from the user
- One prototype rubber-track undercarriage for a Kerala **coffee-plantation flail mower**. Flat to minor gradients; rows max 8 ft (2.44 m); overall width <= 1190 mm. Prove the idea, keep it **simple, buildable by an average welder, not over-engineered**, parts available in India/Kerala.
- Shop: outsourced laser/plasma (MS plate <= 8 mm), press brake, MIG welding, normal lathe, mill for keyseats. (FabLab Kerala has no steel machines - only printers/CNC router/Trotec engraver; useful for 3D-printed fit checks only.)
- Track is a hard requirement (rubber). User wants: ~5 km/h top speed, ~1 km/h mowing speed. Motor housing/mount and deck mounts are **skipped for now**. Deck hosts battery (lithium, size TBD) + electronics.
- Working rules: **show the plan and wait for "start/approve" before applying fixes**; use subagents (Haiku for small jobs, **Opus for planning/reviews**), MCPs (build123d, FreeCAD, MATLAB), existing toolkits/add-ons (don't reinvent); verify claims with web search; be honest about unverified inputs; previews: delete stale ones, show different sides.

## 2. Decisions made (do not re-litigate without the user)
| # | Decision | Source / date |
|---|---|---|
| D1 | Track ACETRAX **180x60x37** (PDF row W180 P60 IGB24 OGB62 C25 D24.5; E=22 frozen). Link count 37 is the repo's size code, NOT in the PDF. | user, 10-31 |
| D2 | Gauge 860 mm (track centre y=+-430), overall width 1168.4 mm | user: width just under 1190 |
| D3 | Roller = **two-drum spool** per station (pipe + backplate + welded seat + 6205), 3 stations/side; nylon wheel only as fallback | user |
| D4 | Idler = **one-piece centre-groove** unit (two 8NB 219.1 pipe rims + hub tube + 2x 6205); rollers stay two-drum | user ("single at the middle") |
| D5 | Two UCFL208 per axle (inner + outer plate); plates 6 mm; SHS40 cross beams bolted to 8 mm tapped pads (no nuts on the track side) | design review |
| D6 | Motor **BM1418ZXF 750 W 48 V** (Yalu, 1:6 box, 480 rpm out, 15.36 N.m rated) | user |
| D7 | **Single-stage 428 chain**, bolt-on wheel (flange hub, 6xM8 PCD100) so tooth counts are swappable. Optimiser (`opt_sprockets.m`, ga + enumeration) chose **12-tooth custom track sprocket + 13T pinion (Apache RTR160 front) + 52T wheel (MT-15 rear)** = ratio 4.0, 5.24 km/h | user asked for optimiser, 10-31 |
| D8 | Weight reduction is done only after open issues are fixed ("proof and value guided"); like-for-like mass comparison required | user |

## 3. Current baseline (re-run to confirm: `python -I cad_v4/build_uc_v4.py` then MATLAB `sim_uc_v4.m`)
- Build: 23 computed gates pass (12 measured / 11 by-construction, tagged in `cad_v4/uc_v4.json`), 0 interference, width 1168.4, **mass 185.1 kg incl. 8.5 kg allowances** (chain, guards, motor rails). v2 frozen 185.7 kg, but NOT like for like: at equal scope v4 is ~9 kg heavier. Weight reduction NOT achieved.
- FEM (FreeCAD+CalculiX, inner plate, pad faces fixed, tet10 ~11 mm mesh - indicative): vertical max 13 MPa; lateral max 79 MPa, p99 30 MPa (allow 167, yield 250).
- Sim (deck 60 kg ASSUMED, design mass 306 kg): 10 deg at rated torque 0.96x; wide-arc turn 1.06x; spin turn 1.36x (needs unpublished motor overload). Motor loads: flat mowing 45% torque / 9 A; 10 deg 96% / 19 A; spin turn 136% / 27 A phase. Battery 3.5 A flat mowing, 37.7 A at 10 deg 5 km/h.
- Turning vs v2 (306 kg spin turn): requirement 131 -> 79 N.m (-39%) but available torque 81 -> 58 (smaller motor): net 1.60x -> 1.36x. **Turning is partly solved: wide arcs OK, pivot turns still need overload.**
- Ground clearance: chain wheel bottom 36.6 mm (plates 30 mm). Larger wheels trade speed (ratio fixed by 480 rpm motor); real fix = lower-rpm / higher-torque motor.

## 4. Task list
Status: DONE / OPEN / BLOCKED (needs user or supplier info).
| ID | Task | Status | Notes |
|---|---|---|---|
| T01 | v2 copied to this folder; audit of v2 (CAD vs BOM, sim integrity) | DONE | v2 had 2 UCFL in CAD vs 4 in BOM; hard-coded PASS lines; stale 201.1 kg FreeCAD |
| T02 | Parametric master `cad_v4/build_uc_v4.py` + `catalogue.json`; gates; BOM; 9 laser DXFs (mm); part STEPs | DONE | `patch_*.py`, `*_backup.py` = edit history; script is source of truth |
| T03 | Sim `sim_uc_v4.m` reads JSON; motor script `motor_bm1418zxf.m`; optimiser `opt_sprockets.m` | DONE | motor_min_sizing.m, sim_track_motor_matrix.m, layout_v4.* are SUPERSEDED (labelled) |
| T04 | FEM plate vertical + lateral on current geometry | DONE | mesh: pass `MESH=(max,min)`; retry sizes if "nonpositive jacobian" |
| T05 | Opus reviews 1-4 + Haiku validations | DONE (round 4) | latest verdict: NOT ready for first-article; items below |
| T06 | Weld schedule, track-change SOP (outer plate must come off) | DONE (draft) | unproven until first build |
| T07 | **Motor mount + chain take-up** (62-66 links fixed at C~197 needs >= 1 pitch take-up) | BLOCKED | needs Yalu drawing (shaft, mounting, body, weight, peak torque) - email yalu@wzyalu.com; user said skip for now |
| T08 | **Turned-part drawings with fits/process notes + A3 layout pack** | OPEN | review blocker B3. `draftwright` not installed in system python; fallback ezdxf+pymupdf. Confirm 6205 housing fit M7 vs N7 with supplier |
| T09 | Chain guards, guard shoe under wheel, lift lugs/lift points, deck mounts | OPEN | currently allowances / 0 kg |
| T10 | FEM follow-ups: mesh convergence (6-7 mm), outer plate + beam joints, track pretension; UCFL plate-load case | OPEN | `CASE='ucfl'` produced no loads (empty *CLOAD) - known bug, analytic only |
| T11 | **Weight-reduction pass (value-guided, like-for-like)** | OPEN | candidates: bigger plate windows (FEM headroom), plate bottom edge up, UCFL207 + D35 axle (~3.5 kg), thinner idler hub/backplates, beam wall; keep 6 mm plates (lateral governs) |
| T12 | Raise plate bottom edge 30 -> ~50 mm (mud/sinkage) | OPEN | suggested, waiting for user OK; UCFL bolt hole z=72 leaves 14 mm ligament |
| T13 | Supplier confirmations before ordering | OPEN | ACETRAX: inner-face drawing (is the gap between horns a solid floor?), min bend radius, link counts, roller load; MT-15 chain pitch (428?); 12-tooth track sprocket tooth form; 8NB wall (IS 3589/1161); UCFL208 flange thickness; Kerala stock/prices (LRL Motors Kochi = Rolon dealer) |
| T14 | Motor alternatives: lower-rpm (~150 rpm, 50-80 N.m) gearmotor to remove the 4:1 stage, give GC and pivot-turn torque | OPEN | no published Indian unit found yet |
| T15 | First build: tow test (rolling resistance) + drag-turn test (lateral coefficient); log motor temp at 1 km/h on 10 deg | OPEN | replaces assumed rr 0.10-0.15, mu_t 0.65 |
| T16 | Final Opus review before any order | OPEN | |

## 5. Open questions for the user
1. Battery type/size (lithium; mass drives design mass: 40/60/90 kg deck -> spin turn 1.25x/1.36x/1.52x).
2. Apply T12 (plate edge 50 mm)? Approve starting T08 drawings now?
3. Accept pivot-turn limits (wide arcs only) for v1, or pursue a stronger/lower-rpm motor (T14)?

## 6. How to run things
- Build: `cd cad_v4; python -I build_uc_v4.py` (~2.5 min). Variants without editing: env vars `UC_SPR_Z` (track sprocket teeth, default 12), `UC_PINION_T` (13), `UC_WHEEL_T` (52), `UC_LINKS` (even; auto if unset). **Variant builds overwrite the default outputs - re-run the default afterwards.**
- Sim: MATLAB MCP `run_matlab_file` on `sim_uc_v4.m`, `motor_bm1418zxf.m`, `opt_sprockets.m` (sims `clear` all variables; use literal paths).
- FEM: FreeCAD GUI via MCP `execute_code` only (no `freecadcmd` on the MCP host). Set `CASE='vertical'` or `'lateral'`, optionally `MESH=(10.5,2.6)`, then `exec(open('.../cad_v4/fem_plate.py').read())`. Results -> `cad_v4/parts/fem_plate_result*.json` (the sim reads them). Transient FreeCAD docs `FEM_plate`, `UC_Kerala_v4` can be closed; do NOT save the open doc `UndercarriageV2` (belongs to v2).
- Previews: build writes `cad_v4/preview/cat_*.step`; import into the build123d MCP and `render_view` (renderer ignores colour dict; groups are blue-grey structure, red running gear, green drive, cream track). Delete stale PNGs before re-rendering.
- Shell gotchas: heredocs containing triple quotes break the Bash tool - write patch scripts with the Write tool and run them. The harness sometimes injects "repeated failure / no verification" hook notes that did not match reality; check the actual outputs.

## 7. Known unverified inputs (carry these flags into any report)
Track link count / bend radius / roller load / gap floor; 12-tooth track sprocket tooth form (scaled from the repo 72z9 design); MT-15 chain pitch; UCFL208 flange thickness and housing OD; 8NB wall (6 mm used); SHS40 table; motor mass (3.0/7.12/10.66 kg listed), shaft, peak torque, overload, current for the 750 W version (20 A used); deck mass (60 kg guess); soil rr/mu_t; DIN key depths; M24 clamp torque (draft 100 N.m); 428 chain breaking load 17.8 kN (08B listing).

## 8. File map (this folder)
`cad_v4/` build + data: `build_uc_v4.py`, `catalogue.json`, `uc_v4.json`, `uc_v4_bom.csv`, `uc_v4_assembly.step`, `dxf/`, `parts/` (STEPs, FEM inputs/results), `preview/`, `fem_plate.py`, `patch_*.py`.
Root: `sim_uc_v4.m`, `motor_bm1418zxf.m`, `opt_sprockets.m` (current); `STATUS.md`, `WELD_SCHEDULE.md`, `TRACK_CHANGE_SOP.md`, this tracker; legacy v2 copies (`sim_v2*.m`, `BRIEF.md`, `cad/`, `drawings/`, ...) are history only.

## 9. Change log
- 10-31 Folder created from v2; independent CAD verification; Opus reviews; parametric build; FEM; single-stage drive; optimiser selected 12T/13T/52T; weight/turning honestly reassessed; this tracker added.
