# TRACK MODEL RULES — 180x72x37 (researched framework + compliance)

E = 22 mm FROZEN by user (Oct 2026). All other silent dims stay parametric.

## 1. Sources read (Oct 2026)
Supplier (dimensional authority):
- `ACETRAX - Construction Tracks (5).pdf` p.2: section diagram (W/A/B/C/D/E) +
  Mini-Excavator row 180/72/23/66/28.5/28.5. ONLY source for A/B/C/D.
- https://www.aceventura-ind.com/mini-x-and-ctl-tracks/ : continuous steel-cord
  + steel-bar + cut/chunk-compound construction. No E published.
Industry sizing/fitment guides (measurement + compatibility rules):
- https://www.ftstracks.com/en/blog/how-to-measure-rubber-track-size : size =
  Width x Pitch x Links; width across travel on rubber base (not lugs); pitch =
  insert-centre distance on the INSIDE, measured over 10 spans; link = one steel
  insert (not one tread lug); Ld = pitch x links on the insert line; never round
  52.5/72.5; 180x72 catalogue link range 30-45 (our 37 inside it).
- https://unitedskidtracks.com/track-fitment-measurement-guide/ : pitch+links must
  match sprocket exactly (pitch controls indexing); width is clearance/floatation
  only; verify guide profile vs roller/flange, tread per terrain, leave adjuster
  range for tensioning, replace in pairs.
Peer-reviewed modeling framework:
- Chamorro Coneo et al., Sci Rep 15:24829 (2025),
  https://pmc.ncbi.nlm.nih.gov/articles/PMC12246062/ : rubber track as discrete
  segments joined by bushing elements (linear kx/cx belt stiffness + angular
  kb/cb bending stiffness); undercarriage = drive sprocket + idler + bottom/top
  rollers + longitudinal tension-spring preload; polygonal contact sprocket/idler/
  rollers-vs-track; soil via sinkage/shear/slip; belt tension to ~7.5 kN.
  Our CAD is the geometric twin of one such segment chain (37 x 72 mm elements
  with steel insert each); dynamics remain in `machine_500mm_tracked` + sims.
- Tolstov et al., FEM stress-strain of rubber-reinforced crawler tracks
  (titles via search; paywalled): confirms inserts + cords as the load path -
  hence rule 6 below. Fukushima et al.: track tension oscillation vs drive
  performance - hence tensioner-travel rule 14.
No track-design textbook was obtainable through available tools; rules below cite
the sources above per rule.

## 2. Rule audit (model as rebuilt Oct 2026)
| # | Rule (source) | Status |
|---|---|---|
| 1 | Size = W x P x N; P insert-centre, inside; N = insert count (FTS/UST) | PASS: 180x72x37 |
| 2 | Lengths on insert/cord line: Ld = P x N, closed loop 0 error (FTS/MBS) | PASS: 2664.0 / 0.0 |
| 3 | One steel insert per pitch on the cord line (supplier+MBS+FEM) | PASS: 37 bars 58x20x6 embedded |
| 4 | W/A/B/C/D exact per ACETRAX row (supplier) | PASS: 180/23/66/28.5/28.5, DXF+STL measured |
| 5 | Horns inward, staggered lug pairs outward; tread separate from links (FTS) | PASS: tips -65.5 in / -128 out, 74 blocks, width held |
| 6 | Belt bends continuously: mitered joints, no gap/overlap on arcs | PASS: end-plane joints |
| 7 | Roots embedded, tips exact (watertight union practice) | PASS: 1.5 mm embed |
| 8 | Width on rubber base, lugs inside W envelope (FTS) | PASS: bbox Y 180.0 |
| 9 | Sprocket pitch = track pitch; PD = P/sin(180/z) (fitment+MBS) | FLAG: R100 ~ z9 PD210.5, confirm z |
| 10 | Tooth fits horn window (72-32=40 long) and C height; centre rib < B=23 | FLAG: supplier-side check |
| 11 | Guide profile vs roller/flange style; flat path (C=D) (UST checklist) | PASS flat; roller widths supplier-side |
| 12 | Tensioner travel + preload in undercarriage model (MBS/UST) | FLAG: chassis-side |
| 13 | Tread schematic only, per terrain (UST); E frozen | DOCUMENTED: chevron, E=22 |
| 14 | Rigid-rubber CAD; bbox residual is clearance, not error | DOCUMENTED: 1283.0/261.9 vs 1273.8/256 |
| 15 | Units/origin/axes + counts in file (twin-model practice) | PASS: mm, centre, 37/74/37/37 |
| 16 | Undercarriage fit: Ls=1017.8 vs 750 target; soil/slip in sims (MBS) | FLAG: chassis-side |

## 3. Fitment recheck from guides
Pitch+links exact (sprocket indexing), width = clearance only, guide vs
roller/flange to verify on sample, 37 within 180x72 catalogue range 30-45.
Measure pitch over 10 spans on the delivered track before cutting sprockets.
