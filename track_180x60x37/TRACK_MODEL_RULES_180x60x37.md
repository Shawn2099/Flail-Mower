# TRACK MODEL RULES — 180x60x37 (PDF-exact + carried-over + researched curvature)

E = 22 mm CARRIED OVER from 1st track (180x72x37, frozen by user Oct 2026).
All other silent dims stay parametric (belt 12 / horn-len 32 / horn-top 16 / lug 50x78 / core 58x20x6).

## 1. PDF data (dimensional authority)
- File: `ACETRAX - Construction Tracks (5).pdf`, Mini-Excavator table.
- Row used: `180 60 24 62 25 24.5` → W=180, pitch=60, IGB(B)=24, OGB(A)=62, C=25, D=24.5 (mm).
- 1st-track row for reference: `180 72 23 66 28.5 28.5`.
- E (outer lug height) is NOT in the pdf → carried over E=22, same as 1st track, per user.
- N=37 from size code 180x60x37 (count of steel inserts / pitches).
- Ld = P x N = 60 x 37 = 2220 mm on the steel-cord pitch line (closure error 0 by construction).

## 2. What changed vs 180x72x37
| Item | 180x72x37 | 180x60x37 |
|---|---|---|
| W / P / N / Ld | 180 / 72 / 37 / 2664 | 180 / 60 / 37 / 2220 |
| B / A / horn width each (A-B)/2 | 23 / 66 / 21.5 | 24 / 62 / 19.0 |
| C / D | 28.5 / 28.5 | 25.0 / 24.5 |
| E (lug) | 22 frozen | 22 carried over |
| R pitch default / Ls / contact | 100 / 1017.8 | 100 / 795.8 |
| Overall L / H (R=100, belt 12, lug 22) | 1273.8 / 256.0 | 1051.8 / 256.0 |
| Along-track gaps (P-32 horn / P-50 lug / P-20 core) | 40 / 22 / 52 | 28 / 10 / 40 |
| Mass (analytic, rubber 1200 / steel 7850) | 18.5 kg | ~17.1 kg (builder prints exact) |

## 3. Curvature / radius — researched, not assumed
Default R = 100 mm is PARAMETRIC (pass `--R` to refit). Kept at 100 so the
undercarriage/sprocket interface stays comparable with the 1st track and with
`motor_traction_geared` (sprocket r=0.10). Justification per source:

1. Sprocket pitch law (ISO 606 / chain practice / Fedotkin rubber-track method):
   PD = P / sin(pi/z). For P=60:
   z8=156.8, z9=175.4, z10=194.2, z11=213.0, z12=231.8 mm
   (R_pitch = PD/2: 78.4 / 87.7 / 97.1 / 106.5 / 115.9).
   R=100 sits between z10 and z11 — i.e. a 10/11-tooth sprocket class,
   same family as the 1st track (P=72: z9 PD=210.5, R_pitch=105.2).
   Builder prints the full candidate table every run.
2. Broken-line bending (Fedotkin 2017, rubber-reinforced tracks): the belt bends
   as chords between conditional joints, engagement on the insert spool + cord
   lay; kinematic pitch-circle radius depends on the joint variant. Our CAD is the
   geometric twin of that: 37 discrete 60 mm chord elements with one steel insert
   each on the cord line, mitered (exact transverse-plane) joints → zero gap/overlap
   on arcs by construction.
3. Polygonal (chordal) effect: dv = 1-cos(pi/z).
   z8=7.6%, z9=6.0%, z10=4.9%, z11=4.1%, z12=3.4%.
   Rubber crawler sprockets run 8-12 teeth (supplier/undercarriage practice +
   Fedotkin); chain-drive ">=17 teeth" rules do NOT transfer. Prefer z=10-11 for
   smoother running; confirm tooth count against the bought track + sprocket sample.
4. Insert/horn clearance on the arc (checked, not assumed):
   bend angle per pitch = P/R = 0.60 rad (34.4°).
   Horn-tip circle radius ≈ R - belt/2 - C = 100-6-25 = 69 mm.
   Tip arc spacing ≈ 69 x 0.60 = 41.4 mm > horn_len 32 → ~9.4 mm clearance, no clash.
   Base gap on straights = P - horn_len = 28 mm. Lug gap = 60-50 = 10 mm
   (tighter than 1st track's 22 mm but positive; gap GROWS on outer-arc, so no overlap).
5. Why conveyor steel-cord pulley minimums do NOT apply: conveyor belts
   (ISO 3684 / Fenner-Dunlop / Metso tables: 400-630 mm minimum pulleys) are thick,
   high-tension, continuous-cord belts. Crawler tracks are thin-carcass + discrete
   steel inserts designed to wrap ~175-230 mm PD sprockets — proven by the ACETRAX
   mini-excavator application itself, by patents US6588862 (link shaping for small
   bend radius) / US7413268 (Dr<=r<=2Dr gap-closure rule, Dr=2*pi*h/n), and by the
   MBS literature (Chamorro Coneo et al., Sci Rep 15:24829 (2025): sprocket+idler+
   rollers with polygonal contact, belt tension to ~7.5 kN; Susceptibility Modeling
   of Rubber Track, Appl Sci 13:10533 (2023): angular kx/cx + kb/cb bushing joints).
   Belt outer-fiber strain at R=100 ≈ 6/100 = 6%, within rubber capability; steel
   cord fatigue is handled by the insert/cord construction, not by conveyor rules.
6. Tensioner travel + preload stay in the undercarriage model (MBS/UST checklist),
   not in this rigid CAD — same split as the 1st track.

## 4. Rule audit (same 16-rule frame as 180x72x37)
| # | Rule (source) | Status 180x60x37 |
|---|---|---|
| 1 | Size = W x P x N; P insert-centre, inside; N = insert count (FTS/UST) | PASS: 180x60x37 |
| 2 | Lengths on insert/cord line: Ld = P x N, closed loop 0 error (FTS/MBS) | PASS: 2220.0 / 0.0 |
| 3 | One steel insert per pitch on the cord line (supplier+MBS+FEM) | PASS: 37 bars 58x20x6 embedded |
| 4 | W/A/B/C/D exact per ACETRAX row (supplier) | PASS: 180/24/62/25/24.5, DXF+STL measured |
| 5 | Horns inward, staggered lug pairs outward; tread separate from links (FTS) | PASS: same code path as 1st track |
| 6 | Belt bends continuously: mitered joints, no gap/overlap on arcs | PASS: end-plane joints |
| 7 | Roots embedded, tips exact | PASS: 1.5 mm embed, horn tip C=25, lug tip E=22 |
| 8 | Width on rubber base, lugs inside W envelope (FTS) | GUARD: bbox Y assert <= W+0.05 every build |
| 9 | Sprocket pitch = track pitch; PD = P/sin(180/z) (fitment+MBS+Fedotkin) | TABLE: §3.1 (prefer z10-11, confirm z on sample) |
| 10 | Tooth fits horn window (60-32=28 long) and C height; centre rib < B=24 | FLAG: supplier-side check (window SHORTER than 1st track's 40) |
| 11 | Guide profile vs roller/flange style; near-flat path (UST checklist) | PASS flat-ish; C=25 vs D=24.5 (0.5 crown — keep, per pdf) |
| 12 | Tensioner travel + preload in undercarriage model (MBS/UST) | FLAG: chassis-side |
| 13 | Tread schematic only, per terrain (UST); E carried over | DOCUMENTED: chevron, E=22 same as 1st track |
| 14 | Rigid-rubber CAD; bbox residual is clearance, not error | DOCUMENTED: analytic 1051.8/256.0 vs STL bbox 1059.3/262.8 (lugs on arcs) |
| 15 | Units/origin/axes + counts in file | PASS: mm, centre, 37/74/37/37 |
| 16 | Undercarriage fit: Ls=795.8 (vs 1017.8 before); soil/slip in sims (MBS) | FLAG: chassis-side (frame SHORTENS ~222 mm) |

## 5. Open / unclear — NOT assumed, needs sample measurement
- E, belt_thk, horn_len, horn_top, lug plan, core bar: carried over, NOT in pdf → caliper/weigh on delivered sample, then re-cut.
- Sprocket tooth count z + tooth thickness/head radius + width (Fedotkin boundary conditions) → confirm against bought sprocket; measure pitch over 10 spans on the delivered track before cutting sprockets (FTS rule).
- C vs D: pdf gives 25 vs 24.5 (0.5 mm crown, unlike 1st track's flat C=D) → kept exact; roller-path machining to follow sample.
- Link count 37 with P=60 shortens the loop 444 mm vs 1st track → undercarriage frame, tensioner travel, and ground contact (~796 vs ~1018 mm) must be re-checked chassis-side.
- Dynamics (tension oscillation — Fukushima; stiffness/damping kx/cx/kb/cb — MBS papers) stay in sims, not in this CAD.

## 6. Reproduce
```
py track_180x60x37/cad/build_track_180x60x37.py
py track_180x60x37/cad/build_track_180x60x37.py --R 97.1   :: fit z10 PD exactly
py track_180x60x37/cad/build_track_180x60x37.py --R 106.5  :: fit z11 PD exactly
```
Outputs land next to the builder: `track_180x60x37.stl / _section.dxf / .json`.
Cross-check: `specs/track_180x60x37.m` holds the same numbers for MATLAB sims.
