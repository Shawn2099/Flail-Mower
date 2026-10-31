# ASSEMBLY v2 — plug-and-play order (weak crew, outside welders)

Tools: tape, caliper, straightedge, 2x dummy dia25x400 bars, spanners, hand drill, grinder + flap disc, chain tool, grease. No lathe/mill on site.

## Modules (build apart, on waist-high stands)
- M1/M2 side frames: plates + tabbed spacers + slider blocks. CHECK: dummy bars slide through all 3 roller seats by hand; diagonals diff <3mm; twist <2mm. If bar sticks: file slot/cheek, never force.
- M3 centre: beams + motor rails + deck mounts (tabbed). CHECK: diagonals + rail spacing = motor feet + shims.
- W eld: stitch, alternate sides, comb jig clamped. Grind dross/chamfer plasma edges first.

## Running gear (bench)
- Discs: weld stack (rings/cheeks+hub), flap-disc high spots, press 6205 + circlip. CHECK: spin by hand, no grind/rock.
- Shafts/axles: cut, face, drill R-clip holes; keys fitted at outsource (mark timed positions with punch).

## Final (order matters)
1. Bolt M1/M2 to M3 (8xM12 ea, cross-pattern, big washers). CHECK: track-centre distance 520 +-2 (tape).
2. Side axles + UCFL (loose), sprockets + keys; slide axle to centre teeth in B-gap by eye. CHECK: 3.5/side play (caliper spot).
3. Rollers/idlers + clamp nuts (do NOT fully tighten until track on).
4. Motors + plain 14T (bore+key at outsource), R15 chains cut to ~58 links + split/rivet link, guards with vent slots. Align by straightedge (pinion plane = wheel plane +-2), tension via rail slots. CHECK: 10-15mm mid-slack.
5. Tracks (2-person, 18kg): screws fully back, walk teeth into windows by barring axle. CHECK: all teeth seat (torch + mirror), sag 20 mid-span. RULE: no pivot-turns on slopes (sim_v2_turn).
6. Tighten everything (M12 80Nm + nyloc + paint marks), run-in 50m on flat, re-check sag + chain + all nuts.
7. Deck on rubber mounts + shims (pads x+-150 y+-100 z175), level check, lift eyes test.
Runtime guide (sim_battery_uc): flat 57 / 250kg-15deg 30 / 400kg-15deg 23 min per 48V20Ah; 2P for double.

## Deck interface (frozen UC side 2026-10-13)
- 4x M12 pads 80x80x10 on mid beams (x=+-150, y=+-100, top z=175), slotted +-3 + shim packs. Deck drills to THESE points (old brief coords superseded).
- 2x lift lugs at rear ties (x=-370, y=+-100). Pack bay stays low between tracks (y+-130, z<200, x -100..+200); motors/rails keep clear of it.
- Belt-plane keep-clear (deck drive side x297-339 equiv) re-checked at deck mating.
Sag/chain = 15 min. Bearing = puller + press, same checks. Track = slacken + slide (2-person). Sprocket every 2nd track. Keep 1x 6205, links, UCFL, M16 nuts as spares.
