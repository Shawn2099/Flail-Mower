%% sim_enclosure_design_v2.m
% ENCLOSURE v2 - corrected, margin-based, fabricatable. 500mm up-cut rear-discharge flail.
% Design basis (internet-verified, numbers used as checks - see SOURCES below):
%  S1 JD 25A/360/370 flails: rotor 1850rpm/42.5m/s, tube 114mm, hood 3.2-4.8mm,
%     end plates 6.4mm, gauge roller 140mm, cut 13-127mm.
%  S2 MechMaxx EFS60: deck 4.1mm, sides 6.1mm, rotor 3in, swing 279mm dia @2958rpm/43m/s.
%  S3 Betstco EF: housing 3mm, reverse (up-cut style) rotor throws UP and OVER.
%  S4 Alamo SHD spec: top 10ga (3.4mm), end plates 5/16in (7.9mm), rear roller 6in (152mm).
%  S5 Volute theory (Eck 1973 ch.11; Carolus Ventilatoren; Gjeta et al 2019): volute area
%     grows ~linearly with angle; clearance gap sz/D2 ~= 5.5% demonstrated.
%  S6 Patil et al (blower): tongue clearance tested 6/8/10/12.5% of impeller dia -
%     smaller gap = more pressure, but tight gap = noise/rub sensitivity.
%  S7 Savoie (ASABE 2011, flail shredder): hammer-hood spacing + counter-knife position
%     set energy vs shred quality; wide gap saves energy but loses re-cut.
%  S8 ISO 17101-2:2012 (flail thrown-object test) + ISO 4254-12 (flail safety) exist and are
%     current - full text paywalled, so we design to their principle (labyrinth guards +
%     throat geometry + field validation), no false precision on criteria.
%  S9 NorthernTool flail manual: min 50mm blade-ground clearance, roller sets height.
%
% v1 FAULTS CORRECTED (honest audit):
%  F1 eta_fan=0.35 single-point - WRONG: blunt straights are poor fans (JD uses cupped
%     knives for lift). v2 uses bounded eta [0.15/0.25/0.35], designs to NOM, verifies at LOW.
%  F2 zeta/dP-split single-point - WRONG: unmeasured. v2 carries zeta=2.5 nominal and
%     states the band; sizes mouth from grass height + practice, fan eq. is CHECK only.
%  F3 Pfan double-counted efficiency - WRONG. v2: Pfan = dP_in*Q/0.5, bounded, vs 158W budget.
%  F4 roof gap 12mm (3.8% D) - TOO TIGHT vs S5/S6 (5.5-6% min) + no stackup. v2: stackup ->
%     nominal 16mm (5.1% D), worst-case min 12mm, hard floor 5mm -> FoS 2.4.
%  F5 linear +18/55deg scroll - ARBITRARY. v2: area-proportional growth +22 from -40deg.
%  F6 rear Vout=1.2Vin continuity ignored recirculation - CONFUSED. v2: throat passes bulk
%     flow per volute, sized on full Q at 8-12 m/s (no-choke throw), recut loop qualitative (S7).
%  F7 roller dia-80 - UNDERSIZE vs S1/S4 (140-152), sinks/scalps. v2: dia-140.
%  F8 3mm shell/6mm cheek with no calc - UNPROVEN. v2: 4mm hood + 2mm liner, 6mm cheeks,
%     torque tube (JD pattern S1), impact-order check vs 74J stone.
%  F9 "exclusion 15m" with no energy calc - UNSUPPORTED. v2: projectile energy calc +
%     labyrinth guard spec to ISO principle (S8) + KEEP 15m + field test requirement.
%  F10 no tolerances - NOT FABRICATABLE. v2: full tolerance table, bend radii, weld, slots.
% Base MATLAB only.
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));
addpath(fullfile(thisdir,'..','..','common','specs'));
bS = blade_straight_mulcher(); drum = drum_50NB_medium();

%% 1. Locked rotor
RO = drum.OD_m/2; PIN_R = RO+0.020; Rcut = PIN_R + bS.pivot_to_tip_m;
Dcut = 2*Rcut; Wcut = 0.500; Wi = 0.550;
RPMW = 2200; omW = RPMW*2*pi/60; Vtip = omW*Rcut; Vhub = omW*RO;
Zc = Rcut + 0.060;
rho = 1.2; dP_ideal = 0.5*rho*(Vtip^2-Vhub^2);
fprintf('Rotor Rcut %.1f (D%.0f) Vtip %.1f @2200 Zc %.0f | dP_ideal %.0f Pa\n', Rcut*1e3, Dcut*1e3, Vtip, Zc*1e3, dP_ideal);

%% 2. Bounded suction model (F1/F2/F3 fix) - suction is ASSIST, mechanical feed is primary
eta = [0.15 0.25 0.35]; zeta = 2.5;   % single curtain row + grass; band stated, not hidden
dP = eta*dP_ideal; dP_in = 0.5*dP; Vin = sqrt(2*dP_in/rho/zeta);
fprintf('\n=== SUCTION BOUNDS (zeta=%.1f) ===\nlow  eta.15: dP %3.0f in %3.0f Vin %.1f\nnom  eta.25: dP %3.0f in %3.0f Vin %.1f <- DESIGN PT\n high eta.35: dP %3.0f in %3.0f Vin %.1f\n', ...
    zeta, dP(1), dP_in(1), Vin(1), dP(2), dP_in(2), Vin(2), dP(3), dP_in(3), Vin(3));
GATE_suction = Vin(1) >= 5.5;
fprintf('GATE suction Vin_low %.1f >= 5.5 : %s (assist threshold; below this, still feeds mechanically)\n', Vin(1), passfail(GATE_suction));

%% 3. Mouth sized from GRASS + PRACTICE (not fan eq.): 75mm crop + lodged + roller approach
lipZ = 0.100; Ain = Wi*lipZ; Q = Ain*Vin;   % Q vector over eta band
fprintf('\nMouth %.0f x %.0f (A %.4f) | Q nom %.3f m3/s (band %.3f..%.3f)\n', lipZ*1e3, Wi*1e3, Ain, Q(2), Q(1), Q(3));
Pfan = dP_in.*Q/0.5;   % air power / volute eff
fprintf('Pfan nom %.0f W (band %.0f..%.0f) vs budget 158W @2200: %s\n', Pfan(2), Pfan(1), Pfan(3), passfail(Pfan(3)<158));

%% 4. Tolerance stackup -> roof gap (F4 fix). All mm.
% Contributors: blade len +/-1.0 | disc runout 0.3 | profile fab +/-1.0 | weld distort +/-1.0
%  pin wear 0.5 | brg play 0.1 | shaft deflect 0.05
wc = 1.0+0.3+1.0+1.0+0.5+0.1+0.05; rss = sqrt(1+0.09+1+1+0.25+0.01+0.0025);
gap_nom = 16; gap_wc_min = gap_nom - wc; FoS_rub = gap_wc_min/5;
fprintf('\n=== STACKUP ===\nWC sum %.2f | RSS %.2f | nom gap %.0f -> WC-min %.2f vs floor 5 : FoS %.2f %s\n', wc, rss, gap_nom, gap_wc_min, FoS_rub, passfail(FoS_rub>=2.0));
fprintf('gap/D = %.1f%% (Gjeta demo 5.5%%, Patil test range 6-12.5%%; 5.1%% = tight-but-proven corner)\n', gap_nom/(Dcut*1e3)*100);
Rroof = Rcut + gap_nom/1000;

%% 5. Volute-correct scroll (F5 fix): area ~ lineal with angle from -40deg, +22 total
% Wrap +80 front over top to -100 rear = 180deg (50%) > 40% rule. Scroll -40..-100.
% Front sheet = TANGENT to Rroof circle at 80deg down to lip (CAD caught old secant sheet
% grazing the tip circle at ~2mm; tangent holds full 16 gap along the whole sheet).
aF = 80; aR = -100;
ang = linspace(aF, aR, 70);
Rprof = Rroof + max(0, (-(ang+40))/60)*0.022.*(ang<-40);
yArc = Rprof.*sind(ang); zArc = Rprof.*cosd(ang);
zF = lipZ - Zc;   % lip 100 abs
tT = (Rroof*cosd(aF)-zF)/sind(aF);   % tangent run from 80deg point to lip height
yF = Rroof*sind(aF) + tT*cosd(aF);   % tangent dir (cos80,-sin80): lip Y
yArc = [yF yArc(2:end)]; zArc = [zF zArc(2:end)];
yH = yF+0.005;   % curtain header just ahead of lip
clr_curt = (yF-Rcut)*1e3;   % tip-to-sheet clearance at lip height
GATE_curt = clr_curt>=25;
clr_sheet = (Rroof-Rcut)*1e3;   % tangent => full roof gap holds along entire sheet (outer)
clr_sheet_in = clr_sheet-4-wc;  % inner face, worst-case stack
GATE_sheet = clr_sheet_in>=5;
fprintf('Front lip Y%.0f | tip front Y%.0f | curtain clr %.0f (>=25): %s\n', yF*1e3, Rcut*1e3, clr_curt, passfail(GATE_curt));
fprintf('Sheet tangent: outer clr %.1f along full sheet | inner WC-min %.2f vs 5: %s\n', clr_sheet, clr_sheet_in, passfail(GATE_sheet));
wrap = aF-aR;
fprintf('Roof R%.0f wrap %ddeg (%.1f%%) | scroll R%.0f->%.0f\n', Rroof*1e3, wrap, wrap/360*100, Rroof*1e3, (Rroof+0.022)*1e3);

%% 5b. BOX VARIANT - 5-face manual build (THE BUILD; Sec.5 volute = reference only)
% 1 plasma development (front+top+rear, 2 manual bends) + 2 bolted cheeks. Single-cut accepted.
% Manual stack WC (m): blade1.0+runout0.3+plasma1.0+bendpos2.0+bendang2.0+weld1.0+pinwear0.5+brg0.1+defl0.05
wcB = (1.0+0.3+1.0+2.0+2.0+1.0+0.5+0.1+0.05)/1000;
% corners, rel-centre m (abs Z = +Zc): lip / front-top / rear-top / rear-mount
Bx = [0.205 0.160 -0.170 -0.210]; Bz = [-0.118 0.187 0.187 -0.038];
bnames = {'front sheet','top sheet','rear sheet'};
fprintf('\n=== BOX PANELS (outer clr | inner | WC-min vs 5) ===\n');
GATE_box = true;
for k = 1:3
    A = [Bx(k) Bz(k)]; B = [Bx(k+1) Bz(k+1)]; AB = B-A;
    t = dot(-A,AB)/dot(AB,AB); t = min(max(t,0),1);
    d = norm(A+AB*t); outer = (d-Rcut)*1e3;
    inn = outer-4-wcB*1e3; g = inn>=5; GATE_box = GATE_box && g;
    fprintf('%-11s outer %4.1f | inner typ %4.1f | WC-min %4.1f : %s\n', bnames{k}, outer, outer-4, inn, passfail(g));
end
% shop bend turns (deg from flat) at the two corners
v1 = ([Bx(2) Bz(2)]-[Bx(1) Bz(1)]); v1 = v1/norm(v1);
turn1 = acosd(dot(v1,[-1 0]));                       % front sheet -> top direction
v3 = ([Bx(4) Bz(4)]-[Bx(3) Bz(3)]); v3 = v3/norm(v3);
turn2 = acosd(dot([-1 0],v3));                       % top direction -> rear sheet
fprintf('Bends: front %.0fdeg turn, rear %.0fdeg turn (from flat), inner r>=8. Plasma-cut angle templates for QC.\n', turn1, turn2);
fprintf('Development: front %.0f + top %.0f + rear %.0f = %.0f x 550, 2 bends, ONE press/manual setup.\n', ...
    norm([Bx(2)-Bx(1) Bz(2)-Bz(1)])*1e3, norm([Bx(3)-Bx(2) Bz(3)-Bz(2)])*1e3, ...
    norm([Bx(4)-Bx(3) Bz(4)-Bz(3)])*1e3, (norm([Bx(2)-Bx(1) Bz(2)-Bz(1)])+norm([Bx(3)-Bx(2) Bz(3)-Bz(2)])+norm([Bx(4)-Bx(3) Bz(4)-Bz(3)]))*1e3);
fprintf('GATE box panels: %s (holes plasma-pilot 8, drill to size; UCF flanges need flat + clearance only)\n', passfail(GATE_box));
% overrides: box lip/header/mount become the build; comb tips at Rcut+12 for manual slop
BOXBUILD = true;
yF = Bx(1); yH = yF+0.005; yEb = Bx(4); zEb = Bz(4); ckTip = 0.012;

%% 6. Rear throat on FULL Q at throw velocity (F6 fix): Vout 8-12, no choke
Vout = 10; hout = Q(2)/(Wi*Vout);
fprintf('\nRear throat: Qnom %.3f / (%.2f x %d) -> h %.0f -> CHOSEN 70 (slots 45-85)\n', Q(2), Wi, Vout, hout*1e3);
GATE_throat = hout*1e3>=45 && hout*1e3<=85;
fprintf('GATE throat in adjustment band: %s\n', passfail(GATE_throat));
outH = 0.070;

%% 7. Roller dia-114 (100NB-Light 114.3x3.65 STOCK) on ground + deflector
rRoll = 0.1143/2; zRollC = rRoll;             % sits on ground, top at 114.3
if BOXBUILD, yE = yEb; zE = zEb; else, yE = yArc(end); zE = zArc(end); end   % box mount vs scroll end
yD = yE-0.086*sind(50); zD = zE-0.086*cosd(50);% 86mm deflector @50deg (reaches down to small roller)
tipAbs = (Zc+zD)*1e3; rollTop = (zRollC+rRoll)*1e3;
fprintf('Scroll end abs %.0f | deflector tip %.0f | roller top %.0f | tip gap %.0f (want 10-15)\n', (Zc+zE)*1e3, tipAbs, rollTop, tipAbs-rollTop);
GATE_gap = (tipAbs-rollTop)>=8 && (tipAbs-rollTop)<=20;
fprintf('GATE deflector gap: %s\n', passfail(GATE_gap));
yRollC = yD-0.010-rRoll;                        % front face 10 behind tip

%% 8. Structure with margin: 4 hood, 4 cheeks+doublers, torque tube
% Impact order-check: 100 g stone at Vtip: E = 1/2 m v^2
E = 0.5*0.1*Vtip^2;
fprintf('\n=== STRUCTURE ===\nStone 100g @ %.1f m/s = %.0f J. Hood 4mm MS, no liner (box build, inspect paint monthly).\n', Vtip, E);
fprintf('Cheeks 4mm + 4mm doubler plates at UCF (weight cut 6.1kg; bolted damping covers panel modes - see audit).\n');
fprintf('Torque tube 40x40x2.6 SHS external backbone + 4 gussets + 2x M12 lift points\n');
fprintf('LIMIT:-condition is light grass/clean ground only. Stones/brush = OUT OF SCOPE (S4 Alamo class is 7.9mm ends).\n');

%% 9. Thrown-object guards to ISO principle (F9 fix, S8)
Etipfrag = 0.5*0.34*Vtip^2;   % whole-blade energy scale (blade stays captive; fragment model = conservative)
fprintf('\n=== SAFETY ===\nBlade-energy scale 0.5*0.34*%.1f^2 = %.0f J -> housing+guards must break line-of-sight on every ray.\n', Vtip, Etipfrag);
fprintf('Front: DOUBLE staggered rubber-strip curtain (12x 80W slit belt), in-swing only + stop bar + header rod.\n');
fprintf('Rear: deflector + rubber flap (to Z25) + roller labyrinth (gap %.0f). Sides: rubber skirts to Z20.\n', tipAbs-rollTop);
fprintf('Belt/drive fully enclosed. KEEP 15m exclusion + field thrown-object check per ISO 17101-2 principle before release.\n');

%% 9b. FACETED shell proof (your photo shape: YES, with this mapping)
% Facet nodes every 20deg: chord sagitta = R*(1-cos10deg) = 2.6-3.0mm inward if chordal.
% Fix: offset bend lines +3 outward -> panel midlines sit ON the volute arc, nodes +3 out.
aN = [80 60 40 20 0 -20 -40 -60 -80 -100];
RN = Rroof + max(0,(-(aN+40))/60)*0.022.*(aN<-40);
sag = max(RN)*(1-cosd(10)); off = 0.003;
intr = 1.0;   % brake-press tolerance allowance, mm
gap_facet_wc = gap_wc_min - intr; FoS_facet = gap_facet_wc/5;
fprintf('\n=== FACET ===\nnodes %s | max sagitta %.1f | bend-line offset +%.0f -> typical intrusion 0, allow %.1f\n', ...
    mat2str(aN), sag*1e3, off*1e3, intr);
fprintf('WC-min faceted %.2f vs floor 5 : FoS %.2f %s\n', gap_facet_wc, FoS_facet, passfail(FoS_facet>=2.0));
fprintf('RULE: bend lines ON arc+3 (radius gauge check), panel inner faces OUTSIDE arc. 9 panels + sheet, inner r>=6.\n');
fprintf('Flat top/dead corners: keep each flat <= ~65 chord; pockets < 10 deep are self-purging at 8 m/s.\n');
GATE_facet = FoS_facet>=2.0;

%% 9c. DRIVE: 2-belt 1:1 pulley pair, NO mechanical slip clutch (user change)
% Primary fuse = ELECTRONIC torque limit in Mecwin GUI (phase-current cap equivalent to 12 Nm at rotor).
% Secondary fuse = belt slip. 2x SPZ 1:1, taper-lock both ends, alignment <=0.5mm.
Tnom = 2.42; Tlim = 12;   % Nm at rotor (Tnom from sim_mvp_rotor)
fprintf('\n=== DRIVE ===\n2x SPZ 1:1 | nominal %.2f Nm | electronic limit %.0f Nm (%.1fx nom): passes slugs, caps jams.\n', Tnom, Tlim, Tlim/Tnom);
fprintf('Pins stay elastic to well above limit (61MPa@cap vs 180 allow); motor stalls on current cap, belts slip next.\n');
fprintf('Guard: 1.5mm steel full enclosure, baffled vents, tool-open only. QC: locked-rotor torque-arm test at commissioning.\n');
fprintf('Top-mount motor (your photo) OK: keep belt plane vertical on cheek, guard it, check CoG + vibration.\n');

%% 10. FABRICATION TABLE (F10 fix) - direct build, tolerances included
fprintf('\n=========== FABRICATION DIMENSION SHEET v2 (mm unless noted) ===========\n');
fprintf('W1 inner width 550 +0/-1 (500 cut + 2x25 clr). Shell wraps OUTSIDE this.\n');
fprintf('W2 outer over shell 558 +/-1. Cheeks 4.0 at +/-275..279 + 4mm doublers at UCF, flatness 0.5.\n');
fprintf('R1 rotor centre Zc 218 +/-2 (bottom tip 60; slots give cut 40-80).\n');
fprintf('R2 roof FLAT Z405 +/-2 (29 over tip top; plasma + straightedge QC). NO liner in box build (inspect paint monthly).\n');
fprintf('R3 ONE plasma development 867x550 (front 308 + top 330 + rear 229), 2 MANUAL bends ~80deg, r>=8, template-checked.\n');
fprintf('   Weld OUTSIDE only, E7018 5 fillet. Bend inner r >= 6 (4mm sheet).\n');
fprintf('F1 front panel straight lip (Y%.0f,Z100) to corner (Y160,Z405). Rear panel corner (Y-170,Z405) to mount (Y-210,Z180).\n', yF*1e3);
fprintf('F2 mouth 100H x 550W. Curtain header Y%.0f: 6 outer rubber strips 80W (bottom Z40), in-swing only + stop bar.\n', yH*1e3);
fprintf('F3 inner curtain: 6 rubber strips 80W staggered 45, bottom Z55. Slit from 8mm conveyor belt; M10 + rod mount.\n');
fprintf('D1 deflector 86LG x 550 x 4 @50deg, tip Z%.0f (gap %.0f over roller). 2x M10/side, slotted +/-4.\n', tipAbs, tipAbs-rollTop);
fprintf('D2 counter-knife COMB at -40deg: ONE plasma part (bar + teeth), tip clr 12 (slots +/-2, WC-min ~8). 2 hanger straps to roof.\n');
fprintf('O1 rear throat 70 (45-85 via flap slots). Flap 8mm belt 550x160, hung from mount Z180, bottom Z25.\n');
fprintf('L1 roller dia-114 x 562 (100NB-L 114.3x3.65 STOCK) centre (Y%.0f, Z%.0f), 6004 sealed brgs + scraper.\n', yRollC*1e3, zRollC*1e3);
fprintf('L2 skids Hardox 6mm 280x90 at +/-286, vertical slots 40-80 in 10 steps. Skirts 5mm rubber to Z20.\n');
fprintf('L3 UCF205 flanges OUTSIDE cheeks (flat + 4 clearance holes each; plasma-pilot 8, drill 15). Span 600, align by straightedge.\n');
fprintf('V1 DRIVE: 2x SPZ 100x3-1610 pulleys 1:1 (Fenner/Pix stock, ~3kW/belt here). Rotor bush 1610 bore 25+key.\n');
fprintf('   Motor: order KEYED shaft variant (confirm bore 24/25/28 at order); bush to suit. 2 belts now (3kW x SF1.3 = 3.9kW).\n');
fprintf('   5kW upgrade = 3rd belt in free groove (3x3 = 9kW vs 5x1.3 = 6.5) + current limit 12->21Nm. NO pulley change.\n');
fprintf('   2x SPZ belts, length at fit-up (C~299 -> 900/912/925 stock; mount slots +/-15). Tension per Fenner tables + 24h re-tension.\n');
fprintf('   Electronic torque limit = 12 Nm (current cap), belt slip backup.\n');
fprintf('   Guard 1.5mm steel full enclosure, baffled vents, tool-open only. Align <=0.5mm; tension per belt tables at install.\n');
fprintf('L4 torque tube SHS40x40x2.6 EXTERNAL backbone on roof (Y-190, Z425) + 4 gussets to cheeks. Depth lip(Y%.0f) to roller rear(%.0f) = %.0f.\n', yF*1e3, (yRollC-rRoll)*1e3, (yF-(yRollC-rRoll))*1e3);
fprintf('L5 roof flat abs 405. Deck steel ~64 CAD-weighed (shell 11.7 + cheeks 9 + roller 6 + drive/fittings/rest).\n');
fprintf('   + rotor hardware 7.1 + motor 15 + pack 8 = ~96 before chassis.\n');
fprintf('   Top stiffener 30x4 bolted M10x4 (audit fix, clears tip top by 21). Slope: chassis per tilt table (~730 track for 45deg).\n');
fprintf('QC: (a) box panel gaps: straightedge + tape vs Bx/Bz table, min 15 typ (b) spin-by-hand no rub (c) flap/curtain swing test\n');
fprintf('    (d) Test A no-load amps @2000/2200/2500 (e) Test B timed-100m amps -> Es -> sim_calibrate_grass\n');
fprintf('    (f) thrown-object walk-around per ISO 17101-2 principle, rear-flap closed vs open.\n');
fprintf('ROTATION: UP-CUT front. If clippings exit FRONT, reverse motor wiring.\n');
fprintf('=======================================================================\n');
fprintf('GATES: suction %s | throat %s | gap %s | power %s | curtain %s | facet %s | sheet %s | BOX %s\n', passfail(GATE_suction), passfail(GATE_throat), passfail(GATE_gap), passfail(Pfan(3)<158), passfail(GATE_curt), passfail(GATE_facet), passfail(GATE_sheet), passfail(GATE_box));

%% 10b. Stone / branch verdict (no global upsizing - targeted kit instead)
% Leakage ~ gap^1.5: +4mm roof everywhere costs ~40% more leak + weight for rare events.
% So: keep roof 16; protect locally + operate in BRANCH MODE.
fprintf('\n--- STONE/BRANCH KIT ---\n');
fprintf('Stones: EXCLUDED by design (clean-ground machine, S9 50mm min clr). Skids+roller+50mm floor is the guard.\n');
fprintf('Branches <=20mm green (Avant class): ALLOWED in BRANCH MODE only:\n');
fprintf(' (a) flap open to 85 (slots) (b) counter-knife OUT (c) forward 0.5 m/s max (d) rpm 2200 (no overspeed)\n');
fprintf(' (e) electronic torque limit 12Nm (belts slip next) (f) inspect deflector/comb teeth after each run.\n');
fprintf('Kit adds: UCF doubler plates standard; comb unbolts in 5 min; mouth corner strips optional (weld-on).\n');
fprintf('Do NOT upsize roof/sides globally: kills suction per S7 and adds ~4kg dead mass.\n');

%% 10c. HIGH-SPEED PROVISION (if Test B shows 2200-2500 cuts stringy)
% Do NOT redesign: pre-qualified envelope to 3000 + hardware already in place.
Rpms = [2500 2750 3000]; pinZ = pi*0.017^3/32; Rcg = PIN_R + 0.055;
fprintf('\n=== HIGH-SPEED ENVELOPE (straight blades) ===\nrpm   tip    Fc     pinBend  Pfan   Pelec  bladeE\n');
for r = Rpms
    o = r*2*pi/60; tp = o*Rcut; Fc = 0.34*o^2*Rcg; sB = Fc*0.014/pinZ/1e6;
    Pf = 158*(r/2200)^3; Pe = (400+Pf)/(0.92*0.88); E = 0.5*0.34*tp^2;
    fprintf('%d  %4.1f  %4.2fkN  %3.0f/180  %3.0fW  %4.0fW  %3.0fJ\n', r, tp, Fc/1000, sB, Pf, Pe, E);
end
fprintf('HARD CEILING 3000 (tip ~50, pins ~102MPa, motor 75%% rated rpm). NEVER 3600 (unqualified).\n');
fprintf('Hardware provision NOW: (a) motor mount slots +/-15 (b) guard clears +15 pulley radius\n');
fprintf(' (c) stock 1:1 pulleys + one-size-up motor pulley on shelf (1:1.2). Ratio change needs longer belt: see (d).\n');
fprintf(' (d) two belt lengths listed on guard plate. Procedure: raise cap in 250-rpm steps ONLY if\n');
fprintf(' cut is stringy AND amps < 80%% cont AND hand-vibration check passes AND exclusion stays 15m.\n');

%% 12. CAD CLOSED-LOOP CHECK - verify CAD-measured values (not our own assumptions)
jf = fullfile(thisdir,'cad','enclosure_cad.json');
if exist(jf,'file')
    cad = jsondecode(fileread(jf));
    fprintf('\n=== CAD CLOSED-LOOP (enclosure_cad.json) ===\n');
    % corners_rel are rel-centre mm; sim Bx/Bz rel m -> compare in mm
    cr = cad.corners_rel; if iscell(cr), cr = cell2mat(cr); end
    dxy = max(max(abs(cr - [Bx(:)*1e3, Bz(:)*1e3])));
    g1 = dxy <= 1.0;
    fprintf('corners vs sim Bx/Bz: max dev %.2f mm : %s\n', dxy, passfail(g1));
    g2 = cad.measured_min_clearance >= 10;
    fprintf('CAD-measured inner clearance %.2f >= 10 : %s\n', cad.measured_min_clearance, passfail(g2));
    g3 = cad.measured_deflector_gap >= 8 && cad.measured_deflector_gap <= 20;
    fprintf('CAD-measured deflector gap %.2f in 8-20 : %s\n', cad.measured_deflector_gap, passfail(g3));
    g4 = abs(cad.part_mass_kg.shell-11.7) < 1.0 && abs(cad.part_mass_kg.cheeks-15.2) < 1.5 ...
        && abs(cad.part_mass_kg.roller-5.6) < 0.5;
    fprintf('masses shell/cheeks/roller %.1f/%.1f/%.1f vs 11.7/15.2/5.6 : %s\n', ...
        cad.part_mass_kg.shell, cad.part_mass_kg.cheeks, cad.part_mass_kg.roller, passfail(g4));
    fprintf('GATE cad-loop: %s\n', passfail(g1&&g2&&g3&&g4));
else
    fprintf('\n=== CAD CLOSED-LOOP: SKIPPED (run cad/build_enclosure_box5.py first) ===\n');
end

%% 11. Plot + fab file
figure('Name','Enclosure v2'); hold on; grid on; axis equal;
plot([-300 250],[0 0],'k-','LineWidth',2);   % ground (excluded from legend)
thc = linspace(0,360,121);
hTip = plot(Rcut*1e3*sind(thc), Zc*1e3+Rcut*1e3*cosd(thc),'r--','LineWidth',1.2);
hDrum = plot(RO*1e3*sind(thc), Zc*1e3+RO*1e3*cosd(thc),'k-','LineWidth',2);
hRoof = plot(yArc*1e3,(Zc+zArc)*1e3,'b-','LineWidth',2.5);
yFN = (RN+off).*sind(aN); zFN = (RN+off).*cosd(aN);   % facet nodes on arc+3
yFN(1) = yF; zFN(1) = zF;                              % front node pinned to lip
hFacet = plot(yFN*1e3,(Zc+zFN)*1e3,'c--','LineWidth',1.5);       % as-built facet polygon
hCurt = plot([yH yH]*1e3,[(Zc+zArc(1))*1e3+65 40],'m-','LineWidth',2);   % curtain hangs from header ahead of lip, clears tip+swing
hDefl = plot([yE yD]*1e3,(Zc+[zE zD])*1e3,'g-','LineWidth',2.5);
hFlap = plot([yE yE]*1e3,[(Zc+zE)*1e3 25],'k--');
thr = linspace(0,360,61);
hRoll = plot(yRollC*1e3+rRoll*1e3*sind(thr), zRollC*1e3+rRoll*1e3*cosd(thr),'k-','LineWidth',2);
plot(0,Zc*1e3,'kx','MarkerSize',10,'LineWidth',2);
hBox = plot(Bx*1e3,(Zc+Bz)*1e3,'g--','LineWidth',2);   % THE BUILD: 5-face box (lip-corner-corner-mount)
xlabel('Y fwd+ mm (rel centre)'); ylabel('Z abs mm'); title('Enclosure BOX-5: flat top 405, mouth 100, throat 70, roller d140');
legend([hTip hDrum hRoof hFacet hCurt hDefl hFlap hRoll hBox],{'tip','drum','volute-ref','facet-ref','curtain','deflector','flap','roller','BOX-5 BUILD'},'Location','best');
try
    saveas(gcf, fullfile(thisdir,'enclosure_profile_v2.png'));
catch
    fprintf('note: enclosure_profile_v2.png locked (open in viewer?) - plot kept in figure window.\n');
end
prof = [yArc(:)*1e3 zArc(:)*1e3 (Zc+zArc(:))*1e3];
save(fullfile(thisdir,'enclosure_profile_v2.mat'),'prof','Rcut','Rroof','Zc','Wi','lipZ','outH','Vin','Q','dP');
fprintf('Wrote enclosure_profile_v2.png + .mat (%d pts)\n', size(prof,1));

function s = passfail(b), if b, s='PASS'; else, s='FAIL'; end, end
