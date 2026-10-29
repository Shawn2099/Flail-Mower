# UC-V2 DRAWING PACK (2026-10-29)

14 x A3 landscape sheets, third-angle projection, dimensions in mm.
Each sheet exists as `UCV2-*.pdf` + a **170 dpi PNG**.
**Review page:** open `review.html` to scroll every sheet at full resolution.
No combined PDF is generated until the PNG review is signed off.

| Sheet | Title | Scale |
|---|---|---|
| UCV2-GA-001 | General arrangement - side elevation | 1:4 |
| UCV2-GA-002 | General arrangement - plan & end view | 1:7 |
| UCV2-GA-003 | Section A-A - roller station (v3 simple spool) | NTS |
| UCV2-GA-004 | Section B-B - drive station | 1:1.5 |
| UCV2-P-001 | Side plate - flat pattern + hole table | 1:4 |
| UCV2-P-002 | Roller station v3 - simple spool | NTS |
| UCV2-P-003 | Idler station v3 - simple spool | NTS |
| UCV2-P-004 | Shaft D25x260 & axle D40x300 | 1:2 |
| UCV2-P-005 | Sprocket 72z9 & hub 76/42 | 1:2 / 1:1 |
| UCV2-P-006 | Chain drive 14T/48T & guard | 1:2 |
| UCV2-P-007 | Frame sections, flanges & bolt schedule | 1:1 / 1:2 |
| UCV2-P-008 | Deck interface & lift lugs | 1:1 / 1:10 |
| UCV2-P-009 | Tensioner & small parts | 1:1 |
| UCV2-P-010 | Parts list / BOM (as drawn, 186.9 kg) | - |

**P-002 / P-003 / GA-003** are v3 review sheets: NTS, all dimensions/parts called out. The rest are vector A3. Vectorise the three after sign-off.

## What the drawings are built from

- `../cad/plate_holes.json` - plate outline, holes, slots, pockets.
- `../cad/*.dxf` - plate, sprocket, rings, web, cheeks, hubs, flanges, guard.
- `../cad/*.step` - measured solids for the turned/machined parts.
- `../cad/mass_audit.json` - per-part mass used by the BOM sheet and `sim_v2`.
- `../cad/freecad_build.py` - canonical assembly placements (rebuilt 2026-10-29).

Regenerate geometry first, then the drawings:

```
python ../cad/build_v2_axle.py        # axle L300 + D40 collars
python ../cad/build_v2_idler.py       # idler web + 5-ring disc + DXF
python ../cad/mass_audit.py           # mass_audit.json + MASS.md
python ../cad/build_v3_simple.py      # v3 spool STEP/STL + section PNGs
python gen_drawings.py                # all 14 sheets
# python make_pack.py                 # ONLY after PNG sign-off; no combined PDF yet
```

(FDXF/STEP are gitignored; the scripts above regenerate them.)

## Key as-drawn numbers

- Track 180x72x37, 37 links, R105.26, C1001.3; loop closure 0.
- Overall **L1268** track / 1240 frame x **W826** over UCFL208 x **H441**.
- Track centres 520; plate gauge 200; discs at +/-62, w40.
- 48T/14T 428 chain, 60 links, C168.66, plane y=+/-140.
- Axle D40x300, keyways 142..157 / 238..282; UCFL bore 47 mm engaged.
- Mass **199.9 kg** incl tracks + motors (target 165 kg; see `../AUDIT.md`).

## Notes / open items

1. Width 826 is set by the UCFL208 housings. If a 750 mm transport limit is
   imposed, mount the UCFLs on the inboard face of the outer plates (~760) -
   decision needed before paint.
2. 48T donor wheel hub width is assumed 15 mm (142..157); confirm against the
   sample before boring/keying.
3. Motor mount bolt size/grade is not frozen; sheet P-007 note only.
4. The track STL in the FreeCAD file is a visual seed; the drawings use the
   analytical loop (37 x 72, R105.26).
