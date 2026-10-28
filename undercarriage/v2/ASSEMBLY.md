# ASSEMBLY v2 - plug-and-play order (weak crew, outside welders)

Envelope as drawn: **L1278 x W826 (UCFL) x H441**; mass **199.9 kg** incl tracks + motors.
Tools: tape, caliper, straightedge, 2x dummy dia25x400 bars, spanners, hand drill,
grinder + flap disc, chain tool, grease. No lathe/mill on site.

## Modules (build apart, on waist-high stands)
- M1/M2 side frames: plates + tabbed spacers + slider blocks. CHECK: dummy bars slide
  through all 3 roller seats by hand; diagonals diff <3 mm; twist <2 mm. If a bar
  sticks: file the slot/cheek, never force.
- M3 centre: rear tie + 2 mid beams + motor rails + deck mounts (tabbed) + front tie.
  CHECK: diagonals + rail spacing = motor feet + shims.
- Weld: stitch, alternate sides, comb jig clamped. Grind dross/chamfer plasma edges first.

## Running gear (bench)
- Discs: weld stack (rings/cheeks + hub), flap-disc high spots, press 6205 + circlip.
  CHECK: spin by hand, no grind/rock.
- Shafts/axles: cut, face, drill R-clip holes; keys fitted at outsource (mark timed
  positions with punch). Axle keyways at y=142..157 (48T) and 238..282 (72z hub).
- 48T wheel: tooth plate on y=140 plane, hub 142..157 butts the inner plate; D40 collar
  (OD60) at 126..138 traps it. 72z hub: 238..282, D40 collar at 282..294.

## Final (order matters)
1. Bolt M1/M2 to M3: **28x M12 total (14/side)** - mid beams 4/joint, rear tie 4/joint,
   front tie 2/joint; cross-pattern, big washers, 80 Nm + paint mark.
   CHECK: track-centre distance 520 +/-2 (tape).
2. Side axles + UCFL208 (loose), 48T wheels + keys; slide axle to centre the 72z pack on
   the track B-gap by eye. CHECK: 3.5/side play (caliper spot); axle end must reach
   y=410 into the 50 mm UCFL bore.
3. Rollers/idlers + clamp collars (do NOT fully tighten until track on). Shaft ends:
   D25 collar / washer / R-pin.
4. Motors + plain 14T (bore+key at outsource), **428 chains 60 links**, guards with vent
   slots. Align by straightedge (pinion plane = wheel plane 140 +/-1), tension via rail
   slots. CHECK: 10-15 mm mid-slack.
5. Tracks (2-person, 18 kg): screws fully back, walk teeth into windows by barring axle.
   CHECK: all teeth seat (torch + mirror), sag 20 mid-span. RULE: no pivot-turns on
   slopes (sim_v2_turn).
6. Tighten everything (M12 80 Nm + nyloc + paint marks), run-in 50 m on flat, re-check
   sag + chain + all nuts.
7. Deck on rubber mounts + shims (pads x +/-150, y +/-100, z 175), level check, lift eyes
   test. **Deck must clear the motors (top z=441) and the 826 overall width.**
Runtime guide (sim_battery_uc): flat 57 / 250 kg-15 deg 30 / 400 kg-15 deg 23 min per
48V20Ah; 2P for double.

## Deck interface (frozen UC side 2026-10-13)
- 4x M12 pads 80x80x10 on mid beams (x=+/-150, y=+/-100, top z=175), slotted +/-3 + shim
  packs. Deck drills to THESE points (old brief coords superseded).
- 2x lift lugs at rear tie (x=-370, y=+/-100).
- Pack bay stays low between tracks (y +/-130, z<200, x -100..+200); motors/rails keep
  clear of it.
- Belt-plane keep-clear (deck drive side x297-339 equiv) re-checked at deck mating.

Sag/chain = 15 min. Bearing = puller + press, same checks. Track = slacken + slide
(2-person). Sprocket every 2nd track. Keep 1x 6205, links, UCFL, M16 nuts as spares.
