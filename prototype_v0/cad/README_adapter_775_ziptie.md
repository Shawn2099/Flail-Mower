# 775 zip-tie cutter adapter (POC)
Parametric source: `gen_adapter_775_ziptie.py` (build123d, mm)

## Files
- `adapter_775_ziptie_hub.step` / `.stl` — D50 x 12 hub
- `adapter_775_ziptie_plate.step` / `.stl` — D50 x 3 clamp plate
- Stack on 5 mm shaft = 15 mm engagement

## Dimensions (mm)
- Head D50, bore 5.05 thru (5 mm shaft + clearance)
- 2x opposed top-loading slots, 180 deg apart, open to top + OD
  - strap channel W5.0 (4.8 tie + 0.2), radial r11..25.5, floor 2 thick
  - head pocket W8.6 x radial 6 (r11..17), same floor (tie head ~7.5 seats here)
- M4 grub radial at 90 deg from slots, mid-height (drill 3.3, tap M4)
- 2x M3 clamp screws PCD36 at (0,+/-18), tap 2.5 depth 8 in hub, clr 3.2 in plate

## Assembly
1. Print hub + plate in PETG/ABS, 4+ walls, 50%+ infill (or Al).
   Ream bore to 5.05, tap M4 + 2x M3.
2. Drop 2 zip ties (4.8 x ~200) tail-OUT, heads seated in pockets.
   Trim tails to 75 mm/side (hub D50 -> Rtip 100 mm -> 200 mm swath, per sim).
3. Clamp plate with 2x M3x12. Grub M4 onto shaft flat + Loctite.
4. Balance: equal tail lengths within 1 mm. Test spin guarded, no load first.

## Limits (from `../sim_775_trimmer_POC.m`)
- Light dry grass only, feed <=0.2 m/s, guard + glasses + 3 m perimeter.
- Zip ties are consumables: check heads every run, replace if whitened/cracked.
