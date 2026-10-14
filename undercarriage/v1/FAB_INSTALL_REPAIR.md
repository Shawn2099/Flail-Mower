# FAB / INSTALL / REPAIR — v2 plug-and-play ed. (outside welders, outsourced laser,
# weak crew. Rule: parts fit TOGETHER despite errors. Fit > weight. Frozen 2026-10-13)

## 0. Golden rules (apply to every DXF at cut stage)
1. Clearance bias: M12->dia14, M10->dia12, M16 rods->dia18 slots. Slots (not holes) at EVERY module joint (+-2 take-up). Holes never reamed.
2. Tabs-and-slots: beams locate into laser slots in plates (poka-yoke, no measuring, no square needed).
3. Etch every part (laser TEXT, no extra op): part no + L/R + arrow FRONT + hole callouts.
4. Self-aligning bearings only: UCFL208 inserts forgive +-2deg weld error; shafts nut-clamped (no fits).
5. Welds: 5-6mm fillets, flat position, single-side access, stitch + alternate; comb jig (laser template) so welder clamps, not measures.
6. Plasma rule: plasma ONLY for gussets/guards/spacers (no fit faces); dross ground + chamfered. ALL holed/aligned parts = laser.
7. Check fixtures, no precision tools: dummy dia25 bar through plate pairs (must slide by hand), tape diagonals (diff <3mm), straightedge twist (<2mm) — go/no-go per step.
8. Lift plan: build at waist height on stands; heaviest single lift = track 18kg (2-person); modules <45kg (2-person, no crane).
9. Shims: 1mm washer packs at 4 deck mounts + motor rails (absorb stack-up, set chain/track alignment).
10. Manual with pictures (FreeCAD views) per step: even a first-timer assembles in order.

Scale: EASY / MEDIUM / HARD. Ratings assume careful hand work + jig discipline.

## 1. MFD (manufacturing difficulty per part)
| Part (qty) | Process | Rating | Notes / risks |
|---|---|---|---|
| Side plates 6mm x4 (1302x190) | laser + ream 25H7 seats, slots | EASY | Confirm laser bed >=1400 long. Deburr; check slot edges for slider fit |
| Spacers/gussets/beams (SHS40/50, flats) | cut + MIG weld | EASY-MED | Cut square; jig + clamp flat; alternate welds (distortion = the real enemy) |
| Roller discs D120x40 x12 | lathe OD/bore52H7 + circlip groove | MEDIUM | Repetitive (12x) but simple; groove tool or snap-ring pliers + filed groove |
| Idler discs D200x40 x4 | lathe (hollow later) | MEDIUM | Solid v1 = heavy (9.9kg ea); hollow rev needs pipe+disc weld + true-up |
| Shafts dia25 x8 (L220) + side axles dia40 x2 | lathe + thread ends | EASY-MED | Straightforward turning; keep g6/H7 fits honest with bore gauges |
| Keyways 12x8 (2 axle + 2 hub + 2 chain wheels) | slot/broach JS9 | HARD | Hardest manual job. No shaper? Outsource broaching OR mill if access. Do NOT hand-file keyways on torque parts |
| Sprocket 8mm x4 + hub boss | laser + turn + weld + ream40H7 | MEDIUM | Same keyway warning; weld boss alternate sides, clamped flat, check runout <0.5 |
| Slider blocks + M16 screws x2 sides | lathe/drill/tap | MEDIUM | Sliding fit in plate slots: file-to-fit, mark L/R (slots wear in, keep pairs) |
| Chain 428 2x (14T/42T) | cut + rivet/split link | EASY | Bike chain tool; align with straightedge; slots give tension |
| Motor rails/plates, guards 2mm | laser/drill | EASY | Guards folded by hand over angle iron (no brake): bend line holes help |
| Track windows | NOT fabbed (bought track has them) | — | Our windowed STL is reference only; bought ACETRAX windows govern |

Outsource shortlist: laser cutting, keyway broaching (6 slots). Everything else in-house.

## 2. INSTALL (assembly order + difficulty)
1. Weld 3 modules (L/R frames, centre) on flat table — MEDIUM (measure diagonals, check twist with straightedge).
2. Fit roller/idler shafts + discs + bearings (arbor press/hand press + circlips) — EASY.
3. Bolt side modules to centre (8xM12 each, torque cross-pattern) — EASY. This split is why install stays easy.
4. Side axles + UCFL flanges + sprockets + keys (check runout, backlash in windows) — MEDIUM (first-time mesh check slow; later routine).
5. Motors + chains (align, set slack 10-15mm, guard) — EASY.
6. Tracks: slide loops over (18kg ea, 2 people), engage sprocket teeth in windows by barring axle — MEDIUM first time.
7. Tension screws to sag 20, run-in 50m, re-check — EASY.
Total: ~2-3 shop-days first build (incl. fit/file), ~1 day second time.

## 3. REPAIR (field + shop)
| Job | Difficulty | How |
|---|---|---|
| Sag check / re-tension | EASY | Jam nuts + tape, weekly |
| Chain split-link replace | EASY | Chain tool, 15 min/side |
| Bearing swap (6205 all round) | EASY-MED | Puller + press; one size everywhere = one spare covers all 32 |
| Track replace | MEDIUM | Slacken screws fully, slide off (2 people); replace sprocket every 2nd track (FTS rule) |
| Sprocket swap | MEDIUM | Unbolt UCFL + hub bolts; no frame cutting (bolted modules win again) |
| Idler/roller re-true | MEDIUM | Lathe skim or swap disc; sliders re-fit |
| Plate/beam crack | MEDIUM | Arc weld + grind; gussets placed for exactly this |
| Motor swap | EASY | Slotted rails, same keyway; re-align chain |

Spares to stock: 6205-2RS x8, 428 links + 14T/42T set, M16 screw+nuts, UCFL208 x1, belt dressing none (dry only).

## 4. Hardest items (honest list)
1. Keyways (6x) — outsource or borrow mill/slotter. Only HARD item.
2. Weld distortion on 1.3m plates — jig, stitch, check; MEDIUM with discipline.
3. First sprocket-window meshing — patience, then routine.
Everything else is EASY-MEDIUM hand work. Overall: very buildable in your shop.
