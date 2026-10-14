# Drive Sprocket 72z9 — design notes (researched)

## Final tooth size (all mm, `cad/sprocket_72z9.dxf` = ONE laminate, cut TWICE)
z=9, P=72, PD=210.51, Rp=105.26, tip Ø210.51 (pitch line), root Ø160.51,
tooth h=25, tip width 22, root width 30, tip chamfer 3, root fillet R3.
Pack 16 = 2×8mm MS IS2062 E250Br (any ≤8 stack: 7+7/6+6 allowed, recheck play),
bore Ø40 H7 + 12×8 Form A key, 6×M12-8.8 nyloc 80Nm, hub turned boss OD76×44
(from dia90 bar). Mass 3.79 kg. Centre-drive in B=23 gap (3.5/side).

## Research basis (not assumed)
- Fedotkin pin-engagement method: PD=P/sin(pi/z); tooth form/width/head-radius
  boundary conditions; straight flanks acceptable at crawl speed.
- US7425044: guide gorge slightly wider than horns (ours 3.5/side, within the
  patent's 1.5-5 practice); sprocket facet pitch 0-1% OVER track pitch so a new
  track beds in (ours nominal-exact; verify seating on sample).
- US7413268: inter-link shear dispersion (our inserts lack sharing protrusions -
  only 2 teeth share load in sim; track-side improvement, not a sprocket fail).
- US6588862/US8191976: link shaping + bias cords for small bend radius (track side).
- Chamorro Coneo MBS (Sci Rep 15:24829): polygonal contact; belt tension peaks at
  sprocket (axle/bearing sizing); Fukushima tension oscillation = watch item.
- Shigley (Lewis/cantilever, keys, bolted joints) + DIN6885-1/ISO773 key tables
  (Engivon refetch): 12×8 key correct for dia40 (t1=5.0 shaft, t2=3.3 hub);
  keyway JS9 (sprocket/transmission class), bore H7 + shaft h6 (easy assembly,
  key takes torque); tooth 6.0 MPa (SF41); key 55/15 MPa; bolts 485 N each.
- MFD for 8mm limit: ONE 2D DXF cut twice (nest 2-up), any ≤8 stack (7+7/6+6);
  6×M12 clamp the pack (Nord-lock/niloc 80Nm); turned boss + 5mm fillets both
  sides, weld alternate clamped flat; tolerance text baked into the DXF.
- Chain background (ISO606): small-sprocket >=17T applies to CHAIN drives, not
  track sprockets (z9 here is correct regime, like-for-like with minis).
- Shop practice: laser kerf ~0.3 (R1 capable); plasma kerf 1.5-2, min hole ~=
  thickness.

## Issues found by sim, fixed in CAD
1. Tip/belt clash (tip at Rp vs belt inner Rp-6) -> tip AT pitch line + drive
   through windows; REQUIRES windowed belt (track-builder rev still open).
2. Mistimed-mesh artifact (pins on teeth, 308 false clashes) -> seating-solve
   + correct track advance (P per tooth-pass, not Rp*phi).
3. Entry/exit tip interference -> 3 mm tip-relief chamfers (gear practice).
4. Tight mesh (0.5 rigid) -> root 40>32>30, tip 30>26>24>22; final centred
   clearance 7.9, zero penetrations, MESH PASS.

## Open / shop notes
- Track rev: cut drive windows exposing insert flanks (else teeth hit belt).
- Plasma: drill/ream bore + bolt holes (13.5 ~= 14 thickness); laser cuts all.
- Confirm z=9 + seating + wear-in on sample before the 60-pitch sprocket.
- Shared axle: size for ~90 Nm + belt tension; bearings UCP/6208 class; guard chain.
- Loop ends must refit (sprocket PD 210.5 vs R100 loop) + wrap >=150 deg.
