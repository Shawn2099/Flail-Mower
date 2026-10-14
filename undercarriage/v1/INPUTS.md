# Undercarriage Inputs — frozen 2026-10-13 (user-supplied)

> User answers from 2026-10-13 review. Authority over earlier docs for undercarriage scope.
> Earlier docs (CHASSIS_BRIEF, motor_traction_geared, sim_track_compare) remain for analysis, not for envelope freeze.

## 1. Duty (revised 2026-10-13)
- Max slope seen: **15 deg**. Burst case: **30 deg**.
- Terrain: **coffee plantations, India — mowed light green grass, soft/mid thickness, walkable/cuttable, no hard stems/rocks**. Soil mostly **solid/hard, not mushy or muddy** (frozen 2026-10-13) — sinkage negligible, traction friction-dominated; sandy-loam mineral params kept as conservative sim case.
- Mass: **200+ kg allowed** (no 200 cap) — size frame/axle for 250-class + margin.
- Loop end radius R: **free variable** — refit by sim/research/proof (rule Ls=(Ld-2πR)/2, drive end → Rp=105.26).
- Priority order: **ease of fab > effectiveness > light weight (no strength compromise)**.

## 2. Track (frozen)
- **180x72x37 ACETRAX** (W=180, P=72, N=37, B=23, A=66, C=28.5, D=28.5, E=22 frozen).
- Ld = 2664 on cord line. R=100 parametric (Ls ~1018).
- Status: **not yet purchased**. Cross-section CAD verified exact vs PDF row (see §8).
- Open: weigh + measure pitch-over-10-spans on delivered sample before cutting sprockets.

## 3. Sprocket (done, needs track rev)
- **72z9**: z=9, P=72, PD=210.51, Rp=105.26, tip at pitch line, h=25, tip22/root30, pack 16 = 2x8mm MS IS2062, bore dia40 H7 + 12x8 key JS9, 6xM12 BCD110.
- Mesh PASS **only with windowed belt**. Current track STL is solid-belt -> teeth clash. Track rev must cut drive windows (insert-to-insert ~52) exposing insert flanks.

## 4. Drive layout (user idea, to detail)
- **Rear drive** preferred, **1 motor per side** (2x total, independent skid-steer — frozen 2026-10-13).
- Each side: motor -> 14T->42T 428 chain -> **own side axle** (dia40, simply supported by its 2 module plates, UCFL flanges) carrying its 72z9 sprocket. NO shared through-axle.
- Motors 1.2 kW frozen (burst margin 10%; 1 kW only 1.4% — too thin) mount on centre section, one per side, chain runs vertical to side-axle inboard end.
- Nameplate stall 23/25Nm @250rpm taken as **gearbox-output**; chain second stage G=3.43 fits 15deg cont + 30deg burst (sim_v2 ALL PASS). vmax ~0.88 m/s (mow-duty OK, transport slow — accepted). Separate BLDC drivers (not the 300A mower unit).
- Chain set: Yamaha R15 V4 donor (14T/48T/428 O-ring 132L, frozen 2026-10-13) — 48T bored+keyed to side axle, chain cut to ~58-link span (rest = spares); 14T uses industrial plain-bore 428-14T (R15 front is splined, unsuitable). Adapt ops at keyway outsource shop.

## 5. Rollers / idler (fab; PAIRED discs — frozen 2026-10-13)
- Centre single roller/idler CLASHES horns (horn band A66 vs 60 tread) -> each station = **2 discs on side bands** (belt 170-227 / 293-350), discs D120x40 (rollers) / D200x40 (idler) at track centre +-62, 2x 6205-2RS each.
- Side-module plates sit OUTBOARD of track (track centre +-100), shafts simply supported across both plates. Horns/lugs clear plates by ~10.
- No bought mini-excavator rollers/idlers sourced. Design must be **shop-fabbed from common stock** or very common sizes (easy swap, e.g. std deep-groove bearings 6204/6205/6208, pipe/disc stock).
- Bottom rollers 3-4/side + front idler to design. Top roller only if needed.

## 6. Tensioner
- **Tensioner** (ref-photo style): lug welded on each plate outboard face BEHIND idler (x440) + M12 threaded rod from idler shaft end back through lug + nuts both sides (front nut tensions, rear jam-locks). 4x assemblies. No front anchor, no slider blocks.

## 7. Shop capability
- Laser MS **<=8 mm only**. Rest manual: arc + TIG + MIG, drilling/reaming, lathe (turned boss, rollers, shafts), no press brake assumed (flat + weld).
- Sprocket rule carries over: one DXF cut twice, <=8 stack, ream bore/keyway, weld boss.

## 8. Section re-verify 2026-10-13 (CAD vs PDF)
- PDF row used: `180 72 23 66 28.5 28.5`. Diagram key W/A/B/C/D/E.
- `common/cad/track_180x72x37_section.dxf` measured: W -90..+90=180, B -11.5..+11.5=23, A -33..+33=66, horn 0..28.5=C, belt 0..-12, lug -12..-34 (E=22). **PDF dims PASS exact.**
- Carried over (not in PDF): belt 12, horn_len 32, horn_top 16, lug 50x78, core 58x20x6, E=22 frozen. Confirm on sample.
- **Window issue persists**: belt ring is solid full-width in STL; sprocket teeth need open windows. Not a section-profile error, a missing feature for next rev.
- Window dims (no PDF value — realistic assumption frozen 2026-10-13): belt drive window **52 long (72-20 core) x 20 wide (16 pack + 2/side) x 12 through**, one per pitch on centreline between inserts, corners R3; horn gap 40 (72-32) straddles pack with 3.5/side. Confirm on sample; builder rev to cut these.

## 9. Envelope / frame
- **Not frozen** — size from need (old 750 outer / 1150 L / belly>=100 unfrozen for now).
- Rigid welded frame, no suspension.
- Deck interface from CHASSIS_BRIEF (4xM12 rubber, 2x lift, belt-plane keep-clear x>290) to re-check once frame sized.
- Mass target: as light as possible without strength loss.

## 10. Next sim
- Traction sim to pick **1 vs 1.2 kW + chain ratio** for 15 deg work / 30 deg burst on light grass at 200 kg-class mass, v>=1.5 m/s top.
