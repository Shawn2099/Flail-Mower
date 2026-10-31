# Weld and joint schedule - v2_optimized_claude cad_v4 (draft for shop; verify with the fabricator)

Material: IS 2062 E250 plate / tube, MIG (ER70S-6 class wire). Fillet size = leg. Throat = 0.7 x leg. No stress relief.
Allowable weld shear used in sim_uc_v4.m: 110 MPa. Torque case: design torque 156 Nm (x2 on the 78 Nm turn peak).

| # | Joint | Weld | Why / check |
|---|---|---|---|
| 1 | Sprocket hub (OD76 x 44, turned from OD90 EN8) to the 2 x 8 mm laminate | 5 mm fillet, both faces, all round (alternate sides to limit distortion) | sim: ~2.5 MPa shear at 156 Nm. The laminate bore is OD76 so the hub spigots in; the key (12x8x40) takes the shaft torque. |
| 2 | Chain-wheel HUB: flange (OD120 x 8) to boss (OD60 x 33) | 5 mm fillet both faces | The chain wheel itself is a BOUGHT sprocket bolted to the flange with 6 x M8 on PCD 100 (tapped flange); do NOT weld a bought hardened sprocket. Key 12x8x36 runs through flange + boss (36 mm). Hub material: mild steel (E250/C20), NOT EN8, to avoid preheat. |
| 3 | Roller / idler pipe to backplate | 4 mm fillet, outside, all round | low load; seal against mud |
| 4 | Roller seat ring to backplate | 4 mm fillet, both faces | bore the 52 M7 seat AFTER welding (one lathe setup) |
| 5 | Idler hub tube (OD65 x 150) to its two annular backplates (4 mm, recessed 2 mm) | 4 mm fillet both faces each | machine in TWO setups after welding: bore 46 through, then counterbore each end 52 x 22 deep (bearing enters from the END, shoulder inboard) and cut the DIN 472-52 groove 2.15 wide near each end. Seats open OUTWARD; a 6205 cannot pass the 46 bore. |
| 6 | Beam SHS40x3.2 to end flange (70x70x6) | 4 mm fillet all round | flange holes M12 clearance 13 |
| 7 | Tapped pad (70x70x8) to inboard plate face | 4 mm fillet all four sides; AFTER welding drill 10.2 THROUGH pad + plate in one pass, then tap M12 (14 mm thread) | laser tap holes in two separate pieces will not line up after welding; bolts go in from the centre bay, tips end 2.5 mm past the plate |
| 8 | Tension anchor lug (8 x 30 x 44) to plate face | 5 mm fillet both long sides | carries M16 rod tension |
| 9 | Plate edges / holes | laser cut, deburr; no welds | |

Distortion control: clamp plates flat, tack, weld in short alternating runs; check flatness <= 1 mm per 300 mm before boring.
Fit sequence for the roller/idler spool: weld -> skim OD (run-out <= 0.5 TIR) and bore seats in one setup -> fit bearings -> clamp stack with M24 nuts at about 100 N.m (draft, from review).
Status: DRAFT - sizes follow the engineering checks in sim_uc_v4.m, not a code-certified weld procedure.

Sprocket hub (item 1): turn from mild steel too, or specify preheat 150 C if EN8 is used. Axle (EN8) is not welded.
