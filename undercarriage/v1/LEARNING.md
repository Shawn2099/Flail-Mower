# Undercarriage Learning — for 180x72x37 easy-fab rigid build (15° work / 30° burst, light grass)

Date: 2026-10-13. Sources actually read (no guessing): items 1-4 fetched + local CAD/sims + standard books cited by name.

## 1. Sources used
1. Chamorro Coneo et al., Sci Rep 15:24829 (2025), PMC12246062 — full MBS model read (methods + Tables 1-4 + tension/slip results). Geometric twin of our CAD: discrete segments + bushing kx/cx/kb/cb, sprocket+idler+3 bottom +1 top roller + tension-spring preload, polygonal contact, Bekker+Janosi soil, belt tension peaks at sprocket.
2. FTS "How to measure a rubber track" — size = W×P×N, P insert-centre inside over 10 spans, link = one insert, Ld=P×N, never round 52.5/72.5, 180x72 links 30-45 (ours 37 OK).
3. UST "Rubber Track Fitment Guide" — pitch+links must match sprocket exactly (pitch controls indexing), width = clearance/floatation only, verify guide vs roller/flange, tread per terrain, leave adjuster range, replace in pairs.
4. FTS "Rubber track tension and maintenance" — grease-cylinder principle, sag 10-50mm class-dependent, over-tension (hot, heavy steer, fast wear) vs under-tension (sag, knock, skip, detrack), weekly sag check, monthly sprocket/roller/idler check, tensioner at end-of-stroke = diagnose, cuts vs cord-exposed replace rule.
5. Local: ACETRAX pdf row 180/72/23/66/28.5/28.5, track/sprocket builders + sims, CHASSIS_BRIEF, INPUTS.md.
6. Books/standards (principles, not URLs): Wong Theory of Ground Vehicles + Bekker pressure-sinkage (soil equations reused in sims), Shigley (Lewis tooth, keys, bolted joints), DIN6885-1/ISO773 (12x8 key for dia40), ISO606/ASME B29.1 (chain background; >=17T rule does NOT transfer to track sprockets), ASAE D497.5 (draft equation — not needed for mower, slope component only), Fukushima (tension oscillation), patents US6588862/US7413268/US7425044 (link shaping, gap-closure, gorge play 1.5-5mm/side).

Web search returned no results on this machine, so no other books/papers were added rather than invented.

## 2. Architecture that fits our shop (laser ≤8 + lathe + arc/TIG/MIG, rigid, light)
- Per side: rear drive sprocket (done 72z9) + front idler (fab disc) + 3 bottom rollers + optional 1 top/slide + screw-slider tensioner + 2 flat side plates + spacers/RHS spine. L/R frames tied by 2 cross members + deck mounts. Shared through-axle on plummer blocks carrying both sprockets (user layout). Chain motor->axle = reduction stage.
- Why this is the easy-fab minimum: no castings, no grease cylinder, no suspension pivots, no brake-formed channels. One sprocket DXF cut twice, one roller drawing repeated 6-8x, one idler drawing repeated 2x, side plates mirrored.
- Rear drive (user pick) is correct: same parts as front, but tight-side on top when climbing, better approach at front idler, motors+chains stay rear-high out of dirt, tension screws at front where you can reach them.

## 3. Geometry rules to freeze (all verified in our sims/CAD)
- Track: Ld=P×N=2664 cord line, 0 closure error. Ls=(Ld-2πR)/2 ≈1018 @R100. R stays parametric.
- Sprocket: PD=P/sin(π/z). z9 → 210.51, Rp 105.26. Chordal dv=1-cos(π/z)=6.0% @z9. Keep tip at pitch line, root 40-52 window, tip 22 fits 72-32=40 window and B=23 gap with 3.5/side (patent 1.5-5). Wrap ≥150°.
- Rollers run on belt inner face between horns; horn pairs straddle centre pack for guidance. Keep roller path near-flat (C=D=28.5 helps — flat by pdf). Idler dia ~ sprocket root or larger to keep bend loss low; bottom roller dia 100-140 turned from pipe/disc is the fab sweet spot.
- Windows: solid belt MUST get drive windows (~52 insert-to-insert) exposing insert flanks, else teeth hit belt. This is the one track rev blocking the sprocket.
- Chain: motor pinion → big wheel on through-axle. Size chains per ISO606/Shigley (Lewis + wear), keep ratio so vtop 1.5-2.5 m/s and 15° cont / 30° burst torques met for 1 vs 1.2 kW. Centre distance slotted for chain tension, separate from track tensioner.

## 4. Soil + traction scaled to OUR duty (not the 4600 kg planter)
- MBS paper equations (reused in sim_track_compare/sim_motor_track_4combo): p=(kc/w+kφ)z^n, τ=(c+p·tanφ)(1-e^(-j/K)), Rc from sinkage integral, Fmax=A·c+W·cosθ·tanφ. Soil Table 4 (dry sand/sandy loam/clay) = mineral reference; plantation mulch/mud needs field calibration (sim_calibrate_grass).
- Paper 4600 kg @7 km/h: slip 6-10% no draft, 11-15% with 13 kN draft, 20% on 20° ramp; belt tension peaks at sprocket 7.5 kN no draft, 10-12 kN with draft, low on top run, steps at each roller/idler.
- Scale to ours (~200 kg, 1 m/s, no draft, 15-30°): same SHAPE, ~20x smaller absolute. Our sims already show margins >1 on mineral soils and torques 59 N·m @30°/78 @45° @r=0.10 for 200 kg — at 15° work / 30° burst demand drops ~half. So frame/axle/bearings size for burst torque + belt tension (~0.5-1.5 kN class per side, not 7.5 kN), plus shock factor. Do NOT copy 4600 kg tensions into our shaft sizing.
- Turf thatch not in Bekker tables: keep grass μ=0.12 rolling allowance + ground pressure check (2×Ls×W ≈0.37 m² @200 kg → ~5.4 kPa, turf-safe). Longer Ls of 72-pitch helps floatation vs 60-pitch.

## 5. Tensioner — screw-slider (easiest, chosen)
- Function from FTS + MBS: take up stretch/wear, hold preload so belt doesn't skip/detrack, NOT drum-tight. Reserve travel ~30-50 mm at idler; slots in side plates + threaded rod + jam nuts + sliding idler axle blocks.
- Set/check: firm level ground, clean clay, measure sag mid-span (roller underside to belt inner) — class spec 10-50 mm; use ~15-25 mm starting point for our size, confirm on sample. Re-check after short run. Over-tight = hot rollers, heavy steer, fast wear; loose = knock, skip, sideways walk (FTS signs).
- Fukushima watch: belt stiffness + idler spring affect torque/speed ripple; rigid screw needs periodic re-check (weekly/soil-change per FTS), monthly full roller/sprocket/idler look. Tensioner at end of stroke = worn system, diagnose before ordering track.

## 6. Rollers + idler — fab pattern (no catalogue part found)
- Bottom roller (repeat 6-8x): turned disc/pipe Ø100-140 × width <B or straddling horns per UST roller/flange check, 2x 6204/6205/6208 deep-groove (common, cheap, swappable) on fixed stub shaft, contact-sealed (2RS), spin-free with no play. Width must clear horns (A=66 outer / B=23 inner) — prove on section DXF before cutting.
- Front idler (2x): larger fab disc Ø180-210 (near sprocket root) on same bearing/stub pattern + sliding blocks for tension screws. Crown 0.5 mm or flat per C≈D; confirm against sample roller path.
- Top: omit or 1 small slide/roller per side if top sag > spec — decide at assembly, bracket pre-drilled.
- Materials: MS IS2062 plates ≤8 laminated/doubled where needed, turned C45/EN8 shafts, pipe stock for drums. Weld 5 mm fillets, clamp flat, alternate sides (same practice as sprocket boss).

## 7. Frame + axle + mounts — light without losing strength
- Side plates: 2x 6-8 mm laser flats per side with lightening pockets (keep ≥3x hole-dia edge distance, bridge ≥ plate thickness), spaced by turned tubes/RHS + cross members. Triangulate to deck mounts; avoid bending loads into thin plate — carry vertical via rollers-to-frame direct stack.
- Through-axle dia40 h6 (matches sprocket H7/JS9) on 2-4x UCP/plummer blocks; size for burst torque (chain pull + belt tension vector), deflection <0.001×span, critical speed far above ~150 rpm. Keys DIN6885 12x8, t1=5.0 shaft / t2=3.3 hub.
- Deck: 4x M12 rubber mounts + 2 lift points (CHASSIS_BRIEF coords to re-check once frame sized); keep belt plane x297-339 clear on drive side; pack low between tracks for CG.
- Weight levers: pockets, 6 mm where 8 not needed, hollow rollers/idler, holes only where sealed bearings keep dirt out; NO thinning at tension slots, axle seats, mount lugs.

## 8. What NOT to copy from heavy machines
- Grease-cylinder tensioner, cast rollers/idlers, sprung suspension, ≥17T chain rules, conveyor pulley minimums (400+ mm) — none apply to this light rigid rubber-track mower (see TRACK_MODEL_RULES §3.5-3.6 for why).
- 4600 kg belt tensions, planter draft loads, 7 km/h slip numbers — equations yes, absolutes no.

## 9. Build-then-buy checks (before cutting steel in quantity)
- On delivered track sample: pitch over 10 spans, W/A/B/C/D caliper, weigh, window/insert form photo, roller-path hardness/crown. Re-cut sprocket/roller widths only after this.
- At assembly: seating/wear-in check (US7425044 0-1% over-pitch bed-in note), sag set + run-in re-check, skip/detrack test at 15°/30° on grass, roller temp + noise check.
