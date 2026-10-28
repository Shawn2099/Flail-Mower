# V2 OPTIMIZE — max weight loss + easiest MFD/COTS (400kg worst, 20° max, 1.2kW/side)

> **2026-10-29 audit (as-built):** 199.9 kg incl tracks + motors, not ~165 kg. The 165
> estimate undercounted shafts/collars/idlers and assumed 5 mm plates + SHS32, which the
> trim study rejected for shop tolerance. Frozen build stays **6 mm plates / 8 mm
> sprockets / SHS40 (6-8-40)**. Corrections: axle L300 (was L240, only 17 mm in the UCFL
> bore), keyways at 142-157 / 238-282, chain 60 links (was 58), overall W826 not 732,
> chain plane 140 both sides. See AUDIT.md, MASS.md, drawings/.

Basis: v1 sims ALL PASS + MBS paper (tension peaks at sprocket, top run slack) +
FTS guides (debris wedge, sag 10-50, sprocket-with-2nd-track rule) + shop limits.
Note: v1 rollup double-counted tracks (246 incl 2x36); true v1 = **~210kg** incl tracks.

## 1. New envelope (MATLAB, sandy-loam interim, Rp=105.26)
| Case | Axle dem | G3 (71.2) | G3.43 14->48T (81.4) |
|---|---|---|---|
| 250/15° | 33.4 | PASS 113% | PASS |
| 250/20° | 44.2 | PASS 61% | PASS |
| 400/15° | 53.5 | PASS 33% | PASS |
| 400/20° worst | 70.7 | PASS 0.7% TOO THIN | PASS 15% |
| 250/30° burst | 64.6 | PASS 10% | PASS 26% |
vtop: G3 1.01 / G3.43 0.88 m/s (mow band 0.5-1.0 OK, transport slow accepted).
**Freeze: G=3.43 (14T->48T 428 Rolon, both catalogue sizes).**

## 2. Weight cuts v1 210 -> target ~150 (all with sim re-proof)
1. Idlers hollow (219x6 pipe + 2 cheeks + hub): 4x9.86 -> 4x3.5 = **-25**
2. Roller drums from 121x6 pipe + cheeks + hub (skim after weld): 12x3.54 -> 12x2.2 = **-16**
3. ONE 6205/disc (load <=1.7kN vs C14.8, L10>300Mrev, seals halved = less drag): 32 -> 16 brgs = **-2 + cost halved**
4. Plates 6 -> 5mm + bigger pockets + welded rib flats (no brake needed): **-12**
5. Beams: SHS50->40 rear, 40->32 mid + smaller gussets (re-proof weld/bolt): **-12**
6. Guards 2 -> 1.5mm, drilled rails, light chain covers: **-3**
7. Keep dia40 axles + UCFL208 (COTS beats 1.5kg saving).
Saves ~70 -> **~140 + tracks 36 = ~176? restated: UC ~104 + tracks 36 + motors/chain ~25 = ~165.** (Exact in v2 weigh.)
Efficiency bonus: half the seal drag, no top roller (MBS: top run slack — already none), chain ~95%.

## 3. MFD-effort cuts (fewer ops, common stock only)
- Pipe drums kill the biggest lathe hours (no deep boring/trepanning).
- Single bearing/disc halves press fits (32 -> 16).
- ONE plate DXF (mirror for L/R), ONE disc drawing x2 sizes, ONE shaft drawing x2 lengths.
- Keyways (6x) stay the single outsource (mill/slotter/broach) — unchanged, unavoidable at 80Nm.
- Bolted L/R/centre: modules built/tested apart, 8xM12 joints; track-off repair without cutting.
- COTS India: NBC/SKF 6205-2RS, Rolon 428 + 14T/48T, UCFL208, M16 rod+nuts, Jindal SHS40/50, IS2062 plate, EN8 bar, 72z9 sprocket (own DXF, any laser shop).

## 4. v2 build list (on your go)
1. sim_v2 (400kg/20° gates + L10 single-brg + hollow-drum weld check).
2. Builders: G3.43 chain, hollow drums, 5mm plates+bigger pockets, single-brg hubs, lighter beams, corrected mass rollup.
3. Rerun all sims + mesh + FreeCAD reload + weigh.
Say **build v2** and I start.
