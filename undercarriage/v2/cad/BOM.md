# BOM LOCKED v2 (2026-10-13; audit corrections 2026-10-29) — quantities per MACHINE (2 tracks)

Envelope as drawn: **L1278 x W826 (UCFL flange) x H441**; plate envelope 726, track 700, axles 820.
Mass as drawn: **199.9 kg** incl tracks + motors (`MASS.md`, `AUDIT.md`).

## Laser (outsource; IS2062)
| File | T | Qty | Notes |
|---|---|---|---|
| side_plate.dxf | 6 | 4 | ONE P/N mirrored, etch labels |
| sprocket_72z9.dxf | 8 | 4 | 2/side pack, cut x2 per DXF |
| cheek_OD114_ID65_6mm.dxf | 6 | 24 | roller cheeks |
| ring_D200_ID150_8mm.dxf | 8 | 20 | idler tread rings 5/disc |
| web_D200_ID65_6mm.dxf | 6 | 4 | idler web 1/disc (connects tread to hub) |
| hub76_ID42_8mm.dxf | 8 | 12 | sprocket hubs, 6 rings/hub x2 (keyway at outsource) |
| hub65_ID52_8mm.dxf | 8 | 80 | disc hubs 5/disc (Loctite, no machine) |
| flange_mid_140x70_8mm.dxf | 8 | 6 | beam flange MID+REAR, weld to SHS40 end |
| flange_front_50x70_8mm.dxf | 8 | 2 | beam flange FRONT, weld to SHS40 end |
| guard_flat_1p5mm.dxf | 1.5 | 2 | bend at fit-up |

## Stock (steel stockist, cut list)
- 100NB-M pipe 114.3x4.5 x0.4m MS-ERW YST210/E250 (12x drums: shell cut 28 + 2x6 cheeks = 40 overall; cheeks are STRUCTURAL ring-stiffeners) | SHS40x40x3.2: L320 x4 fitted +1 spare + L300 x4 rails | 50x8 flat 0.5m (lugs) | M12 threaded rod 2m (tension rods + spare) | dia25 bright 2.2m (8 shafts L260; 2.08m used) | dia40 bright 0.65m (2 axles L300; keyway outsource)

## COTS (buy)
- 6205-2RS x16+4 spare | UCFL208 x4 (bolt spacing 120mm, plate slots 60 long at 90 nominal -> fits at z 43/163, CONFIRMED vs ref STEP) | R15 V4 chain sets x2 (48T adapt bore+key, **chain 60 links** at C~170) | plain 428-14T x2 (bore+key to motor) | Mecwin 1.2kW x2 + drivers | M12x40 + nuts + washers x28 total (mid 4/joint x4 =16, rear 4/joint x2 =8, front 2/joint x2 =4) + R-pins dia6x40 x8 + washers OD50x26x4 x8 (shaft ends, cross-drill dia6 at build) + M6 grubs x16 (D25 collars) + **D40 collars OD60x12 x4** (48T wheel + 72z hub stops, M6 grub each) + TVS 8.8 M12/M10/M14 hw + TVS nylocks + hardened washers everywhere STRUCTURAL (adjuster screws keep plain + jam nuts - nylock wears under repeated adjustment, 5 reuses max) | Loctite 638 50ml | rubber mounts M12 x4 | 48V20Ah pack (runtime NOTE below)
- FASTENER RULE: TVS 8.8 only, buy authorised (check 8.8 + TVS head marks); nylock = anti-loosen, NOT a substitute for torque — still torque flange M12s to 80Nm + paint-mark.

## Outsource (2 vendors)
1. Laser shop: 10 DXFs above. 2. Machine shop: **8 keyways** (4 axle: 142..157 + 238..282 both sides; 2 hub76; 2 plain-14T) + 2x 48T bore adapt.

## Spares (stock day 1)
6205 x4, 428 links + split x4, UCFL208 x1, M12 nuts, track (1, after sample approval).

## Runtime NOTE (sim_battery_uc): 400kg/15deg ~23min, 250kg/15deg ~30min, flat ~57min on 48V20Ah. Double pack (2P) for longer duty.
