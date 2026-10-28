# STOCK LIST — exact Indian sizes for v2 (buy, don't machine)

Rule: pipe OD used AS-IS (skim 0.5 true-up only). Laser does all profiles. Lathe only hubs/shafts/ends.

## 1. Pipe shells (IS 1239, YSt210/240, any dealer; confirm wall with caliper)
| Use | Stock | OD x wall (ID) | kg/m | Labour saved |
|---|---|---|---|---|
| Roller drums x12 (shell 28 + 2x6 cheeks = 40) | 100NB-Medium | 114.3 x 4.5 (105.3) | ~12.2 | No boring: shell IS the drum; weld cheeks, skim OD |
| Hub tubes (brg seats) | 65NB-Heavy or dia65 bar | bore to 52H7 | — | Short bores only (15-40 long), not full drums |
| Spacers between plates | 40NB/50NB offcuts | 48.3 / 60.3 | — | Cut + face, no turning |
| Slider sleeves (opt) | 32NB-M | 42.4 x 3.25 | ~3.1 | — |

Drum OD is now **114.3** (was 120) — roller_z 91.2, gaps 38/43. Idler is NOT pipe.

## 2. Laser sheet (IS 2062 E250Br, any laser shop <=8mm)
| Use | Sheet | Qty |
|---|---|---|
| Side plates | 6mm (most common, weld-forgiving, no ribs) | 4 (ONE dxf mirrored) |
| Sprocket 72z9 | 8mm | 4 (2/side pack) |
| Idler rings D200/ID150 | 8mm | 20 (5/disc x4) + 4 webs D200/ID65x6 |
| Roller cheeks (ring OD114/ID65) + hubs washers | 6mm | 24 + spares |
| Chain 48T | BOUGHT (R15 V4 donor, adapt bore+key) — no laser | 2 |
| Gussets, motor rails, guards 1.5-2mm | 5/6mm + 2mm | as BOM |

## 3. Bright bars (EN8/C45, any steel stockist)
dia25 x2.2 m (8 roller/idler shafts L260, cut+drill ends), dia40 x0.65 m
(2 side axles L300 h6 + 4 keyways OUTSOURCE: 142..157 / 238..282 each side),
dia65 (hub blanks, bore 52H7). No other turning stock needed.

## 4. Sections (Jindal/Tata, single sizes to reduce stock)
SHS 40x40x3.2 (rear motor beam, mid cross, front tie — ONE size),
50x8 MS flat, M12 threaded rod + nuts (tension pull-rods; M16 dropped — M12 ample at ~2kN preload).
(SHS32 dropped — patchy stock; single SHS40x40 size, re-proofed 110MPa < 150.)

## 5. COTS (bike + bearing shops, any town)
- Bearings: 16x 6205-2RS (NBC/SKF, ONE size) + 4x UCFL208 (flange, side axles; bolt spacing 120 mm)
- Chain: Yamaha R15 V4 donor sets 2x (14T/48T/428 O-ring 132L) — 48T adapted (bore+key), **cut to 60 links** (C~170); 14T = industrial plain-bore 428-14T (Diamond/Rolon stock, R15 front splined — unsuitable)
- Shaft collars: 16x D25 (OD40) + 4x D40 (OD60x12, 48T wheel/72z hub stops)
- Fasteners: M10/M12/M16 8.8 + nylocs (TVS/Unbrako), M12 rubber mounts (deck)
- Motors: 2x Mecwin 1.2kW (same keyway) + separate BLDC drivers

## 7. ZERO-precision-lathe program (v2 final — frozen 2026-10-13)
Every bore/seat converted to laser + Loctite + bolt-clamp. No H7, no deep bores, no OD turning.
| Old op | Replacement |
|---|---|
| Hub bore 52H7 (lathe) | Hollow bar 65x52 cut + face, OR laser ring stack ID52 + Loctite 638 (fills 0.15, rated for bearing seats) |
| Shaft seats 25H7 ream in plates | Laser dia26 clearance + shaft + nuts/washers both sides (bicycle-axle clamp) |
| Axle seats/bearing bores | UCFL208 bolted (laser M12 clearance holes only) |
| Sprocket boss turning | Laser ring stack OD76/ID42 + weld to pack |
| Shaft shoulders/grooves | COTS shaft collars + R-clips in hand-drilled holes |
| Slider blocks (mill) | 3x laser plates laminated + M16 rod stock |
| 48T wheel | Laser profile (DXF stage), 14T bought |
Lathe left: facing/chamfering bar ends + hand drilling (drill press). Only outsources: laser + 6 keyways.

## 8. Old labour map (superseded by §7, kept for reference)
1. Deep boring/trepanning drums -> GONE (pipe shell + laser cheeks).
2. Big-OD turning (D200) -> GONE (laser rings, flap-disc true only).
3. Lathe max job: NONE precision (was: hub dia65 + shafts + axle ends).
4. Press fits 32 -> 16 (single brg/disc).
5. Profiles: 3 DXFs total (plate, sprocket, rings/cheeks) — mirror/repeat, no new drawings.
6. Only outsource: laser cutting + 6 keyways (mill/slotter/broach).
