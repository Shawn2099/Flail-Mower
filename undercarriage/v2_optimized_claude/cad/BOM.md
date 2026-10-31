# BOM v3 (simple spool) — quantities per MACHINE (2 tracks)

**2026-10-29:** roller and idler replaced with the approved simple spool:
two identical **pipe + backplate + welded bearing seat** drums per station,
one **loose spacer** between the bearing inner races, one Ø25 shaft.
**No Loctite. No ring stacks. No central weld.**

Envelope as drawn: **L1278 x W826 (UCFL flange) x H441**; plate envelope 726, track 700, axles 820.
Mass as drawn: **185.7 kg** incl tracks + motors (`MASS.md`).

## Laser (outsource; IS2062)
| File | T | Qty | Notes |
|---|---|---|---|
| side_plate.dxf | 6 | 4 | ONE P/N mirrored, etch labels |
| sprocket_72z9.dxf | 8 | 4 | 2/side pack |
| backplate_roller_OD1053_ID65_6mm.dxf | 6 | 12 | welded inside 100NB pipe, inner end |
| backplate_idler_OD190_ID65_6mm.dxf | 6 | 4 | welded inside 200 OD tube, inner end |
| hub76_ID42_8mm.dxf | 8 | 12 | sprocket hubs, 6 rings/hub x2 (keyway outsource) |
| flange_mid_140x70_8mm.dxf | 8 | 6 | beam flange MID+REAR |
| flange_front_50x70_8mm.dxf | 8 | 2 | beam flange FRONT |

## Turned / stock (steel stockist)
- **100NB pipe 114.3 x 4.5**, 12 x 40 long (roller drums); 0.55 m.
- **200 OD x 5 wall tube**, 4 x 40 long (idler drums); 0.2 m — confirm 200 OD availability (seamless or rolled).
- **65 mm bar** (or 65/52 tube), 16 x **bearing seat 65/52 x 22**, bore **52 H7** after welding; 0.4 m.
- **32NB pipe 42.4x3.2**, 8 x **109** loose spacers; 0.9 m.
- **dia25 bright EN8** 2.2 m (8 shafts L260; press fit at bearing seats).
- **dia40 bright EN8** 0.65 m (2 axles L300 + keyways).
- SHS40x40x3.2: L320 x4 fitted +1 spare + L300 x4 rails.
- 50x8 flat 0.5 m (lugs); M12 threaded rod 2 m.

## COTS (buy)
- **6205-2RS x16** (2/station; no circlips). Outer race press into 52 H7 seat; inner race press on Ø25 shaft.
- **Ø25 shaft collars ×16** (OD40) at the plates.
- **Ø40 collars OD60 ×4** (48T wheel + 72z hub stops).
- UCFL208 x4 (bolt spacing 120, plate slots 15x40 at z 73/193).
- 428 chain sets x2 (48T adapt bore+key, **chain 60 links** at C~170).
- plain 428-14T x2 (bore+key to motor).
- Mecwin 1.2 kW x2 + drivers.
- M12x40 + nuts + washers x28 total (mid 16, rear 8, front 4).
- R-pins dia6x40 x8 + washers OD50x26x4 x8.
- M6 grubs ×16 (Ø25 collars); Ø40 collar grubs ×4.
- TVS 8.8 M12/M10/M14 hw + nylocks + hardened washers. Press fits only.
- rubber mounts M12 x4; 48V20Ah pack.

## Outsource (2 vendors)
1. Laser shop: 7 DXFs above.
2. Machine shop: **16 bearing seats 65/52x22, bore 52 H7** (after weld); 8 keyways (4 axle + 2 hub76 + 2 plain-14T); 2x 48T bore adapt.

## Spares (stock day 1)
6205 x4, 428 links + split x4, UCFL208 x1, M12 nuts, track (1 after sample approval).

## Runtime (sim_battery_uc)
400 kg/15 deg ~23 min, 250 kg/15 deg ~30 min, flat ~57 min on 48V20Ah. Double pack (2P) for longer duty.

## V3 roller/idler rules
- Two identical drums per station at ±62; backplate/seat at the **inner** end; outer pipe end **open** (cap optional).
- Bearing at the **tread centre** (seat extends 22 into the pipe; bearing 12.5..27.5).
- **Press fits only**: outer race 52 H7 seat; inner race Ø25 k5 shaft.
- Spacer 42.4/35.5 x109 loose between the bearing inner races; no weld; passes through the backplate/seat bores.
- Horn clearance: roller 7.5 mm (spacer to horn tip); idler 49.6 mm (spacer) / 24.2 mm (pipe bore).
