# BOM LOCKED v2 (2026-10-13) — quantities per MACHINE (2 tracks)

## Laser (outsource; IS2062)
| File | T | Qty | Notes |
|---|---|---|---|
| side_plate.dxf | 6 | 4 | ONE P/N mirrored, etch labels |
| sprocket_72z9.dxf | 8 | 4 | 2/side pack, cut x2 per DXF |
| cheek_OD114_ID65_6mm.dxf | 6 | 24 | roller cheeks |
| ring_D200_ID150_8mm.dxf | 8 | 20 | idler rings 5/disc |
| hub76_ID42_8mm.dxf | 8 | 12 | sprocket hubs (keyway at outsource) |
| hub65_ID52_8mm.dxf | 8 | 80 | disc hubs 5/disc (Loctite, no machine) |
| gusset_100x70_6mm.dxf | 6 | 10 | 2/joint |
| guard_flat_1p5mm.dxf | 1.5 | 2 | bend at fit-up |

## Stock (steel stockist, cut list)
- 100NB-M pipe 114.3x4.5 x0.6m (12x drums w40) | 40NB pipe (spacers dia48? use 50NB 60.3 cut L200 x4 — NOTE: spacer dia48 vs pipe 60.3, recheck at build) | SHS40x40x3.2: L320 x5 + L300 x4 rails | 50x8 flat 0.5m (lugs) | M12 threaded rod 2m (tension rods + spare) | dia25 bright 2m (8 shafts L220) | dia40 bright 0.6m (2 axles L240 + keyway outsource)

## COTS (buy)
- 6205-2RS x16+4 spare | UCFL208 x4 (CONFIRM hole spacing vs plate slots) | R15 V4 chain sets x2 (48T adapt bore+key, chain cut ~58L) | plain 428-14T x2 (bore+key to motor) | Mecwin 1.2kW x2 + drivers | M12/M10/M14 hw + nylocs + washers | Loctite 638 50ml | rubber mounts M12 x4 | 48V20Ah pack (runtime NOTE below)

## Outsource (2 vendors)
1. Laser shop: 8 DXFs above. 2. Machine shop: 6 keyways (2 axle + 2 hub76 + 2 plain-14T) + 2x 48T bore adapt.

## Spares (stock day 1)
6205 x4, 428 links + split x4, UCFL208 x1, M12 nuts, track (1, after sample approval).

## Runtime NOTE (sim_battery_uc): 400kg/15deg ~23min, 250kg/15deg ~30min, flat ~57min on 48V20Ah. Double pack (2P) for longer duty.
