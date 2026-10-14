%% sim_enclosure_design.m
% Flail-mower ENCLOSURE (housing/deck) design for 500 mm up-cut rear-discharge rotor.
% Goal: exact shape/size/dimensions that maximise suction lift + clean entry/exit,
%  using all of the rotor's properties (Rcut, tip speed, throw-over-top).
% Theory base: flail housings work as a partial centrifugal-fan volute:
%  tight concentric roof (Rcut+10..15) over >40% wrap -> pressure rise,
%  tall-but-sealed front mouth (chain curtain) -> inlet velocity lifts grass,
%  expanding rear scroll + deflector + flap/roller -> re-cut + lay-down discharge.
% Rotation: UP-CUT at front (front-bottom blades travel UP), throw OVER rotor to REAR.
% Coord: X = rotor axis, Y = travel (+Y = forward/front), Z = up, origin at ground
%  under rotor centre. Rotor centre C = (Y0=0, Zc).
% Base MATLAB only. Run from matlab folder.
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));
addpath(fullfile(thisdir,'..','..','common','specs'));

bS = blade_straight_mulcher();
drum = drum_50NB_medium();
M = machine_500mm_tracked();

%% 1. Locked rotor inputs (from sim_drum_specsheet / MVP_ROTOR)
RO    = drum.OD_m/2;                 % 0.03015 tube outer radius
PIN_R = RO + 0.020;                  % pin circle radius
Rcut  = PIN_R + bS.pivot_to_tip_m;   % 0.15815 cutting radius
Dcut  = 2*Rcut;
Wcut  = 0.500;                       % swath
Wi    = 0.550;                       % housing inner width (500 + 2x25 side clr)
RPMW  = 2200; RPMC = 2500;           % work / cap
omW   = RPMW*2*pi/60;
Vtip  = omW*Rcut;                    % 36.4 m/s
Vhub  = omW*RO;                      % drum surface speed
Zc    = Rcut + 0.060;                % rotor centre height: bottom tip 60mm off ground (mid 40-80 cut band)
fprintf('Rotor: Rcut %.1f mm (D %.0f), Vtip %.1f m/s @2200, centre Zc %.0f mm (60 tip clearance)\n', Rcut*1000, Dcut*1000, Vtip, Zc*1000);

%% 2. Fan-physics model (why the enclosure matters)
% Ideal centrifugal pressure rise dP_ideal = rho/2*(Vtip^2 - Vhub^2).
% Real housing with leakage/seals achieves eta_fan ~ 0.30-0.40.
rho = 1.2; eta_fan = 0.35;
dP_ideal = 0.5*rho*(Vtip^2 - Vhub^2);
dP = eta_fan*dP_ideal;
fprintf('Fan: dP_ideal %.0f Pa, usable suction ~%.0f Pa (eta %.2f)\n', dP_ideal, dP, eta_fan);
% Inlet: front mouth area Ain = Wi*h_lip (h_lip = lip height above ground).
% Inlet velocity Vin = sqrt(2*dP_in/rho/zeta), dP_in ~ 0.6*dP (rest drives recirculation).
% Target Vin 8-12 m/s: lifts 50-75mm grass upright without ingesting soil.
% Outlet: rear gap Aout sized so Vout ~ 0.7*Vin (slight expansion = grass lays down, no blow-out).
zeta_in = 3.0;   % entry loss (chain curtain + lip + grass)
dP_in = 0.5*dP;

%% 3. Sweep front-lip height (entry vs seal trade-off)
fprintf('\n=== FRONT-LIP SWEEP (Wi=550, dP_in=%.0f Pa) ===\n', dP_in);
fprintf('lipZ  mouthA  Vin    Q      seal?\n');
lips = [0.070 0.090 0.110 0.130];
for h = lips
    Ain = Wi*h; Vin = sqrt(2*dP_in/rho/zeta_in); Q = Ain*Vin;
    if h<=0.095, seal='good (curtain seals)'; elseif h<=0.115, seal='ok'; else, seal='LEAKY - vacuum lost'; end
    fprintf('%.0fmm %.4fm2 %4.1fm/s %.3fm3/s  %s\n', h*1000, Ain, Vin, Q, seal);
end
lipZ = 0.090;   % CHOSEN: 90mm lip -> admits 75mm + lodged grass, keeps seal
Ain = Wi*lipZ; Vin = sqrt(2*dP_in/rho/zeta_in); Qin = Ain*Vin;
fprintf('CHOSEN lip 90mm: Ain %.4f m2, Vin %.1f m/s, Q %.3f m3/s\n', Ain, Vin, Qin);

%% 4. Sweep roof gap (rub vs recirculation trade-off)
fprintf('\n=== ROOF-GAP SWEEP (concentric roof radius = Rcut+gap) ===\n');
fprintf('gap  Rroof  wrap%%  leak  verdict\n');
gaps = [0.008 0.010 0.012 0.015 0.020];
for g = gaps
    % leakage ~ gap^1.5 (labyrinth); rub risk below 8mm with 0.3 disc runout + blade swing
    if g<0.010, v='RUB RISK (runout+swing)'; elseif g<=0.015, v='OK'; else, v='LOSSY (recut drops)'; end
    fprintf('%.0fmm %3.0fmm  ~45%%  ~%.0f%%  %s\n', g*1000, (Rcut+g)*1000, (g/0.012)^1.5*100, v);
end
gap_roof = 0.012; Rroof = Rcut + gap_roof;   % CHOSEN 12mm
fprintf('CHOSEN roof gap 12mm -> Rroof %.0f mm\n', Rroof*1000);

%% 5. Rear outlet sizing (exit without blow-out or choking)
% Rear throat between deflector tip and roller top acts as a throw nozzle:
% flow accelerates here (Vout ~ 1.2*Vin), then expands over the roller and lays down.
Vout_target = 1.2*Vin; Aout = Qin/Vout_target; hout = Aout/Wi;
fprintf('\nRear: Vout target %.1f m/s -> Aout %.4f m2 -> outlet height %.0f mm\n', Vout_target, Aout, hout*1000);
outH = 0.070;   % CHOSEN 70mm (round to fab; adjustable flap +/-20 takes 50-90)
fprintf('CHOSEN rear gap 70mm (flap-adjustable 50-90)\n');

%% 6. Fan-power sanity (must fit inside measured windage budget ~158W @2200)
Pfan = dP_in*Qin/0.5;   % air power through mouth / volute eff
fprintf('Air pumping power ~%.0f W (windage budget ~158W @2200 incl bearings) -> ', Pfan);
if Pfan < 160, fprintf('PASS (remainder is bearing+blade drag)\n'); else, fprintf('CHECK (housing too open?)\n'); end

%% 7. FINAL PROFILE (side view, Y fwd+, Z up, mm rel rotor centre)
% Wrap: front sheet from lip (-Y side) up over roof to rear scroll, then deflector down.
% Angles measured from +Z (top), + = toward rear (-Y? we use Y fwd+, so front = +Y).
%Front lip point F, roof arc centre C=(0,Zc), rear scroll expands +8/+18mm, deflector D, flap line to roller.
Ylip = -(0.0);  % computed below in centre-relative coords
% centre-relative coords (y = Y - 0, z = Z - Zc), metres:
yF = Rroof*sind(58) + 0.015;   % front sheet stands ~15mm proud of roof circle (anti-plaster)
zF = -Rroof*cosd(58) - 0.038;  % drops to lip 90 above ground: Zc-90 = 128 below centre
% check lip height:
lip_check = (Zc+zF)*1000;
% roof arc: from front angle 58deg (front-up) over top (0) to rear -125deg, radius Rroof,
% then scroll: radius grows linearly Rroof -> Rroof+0.018 over last 55deg (volute expansion).
% deflector tip: at rear angle -125deg, radius Rroof+0.018, then short straight lip angled 45deg down.
ang1 = linspace(58, -125, 60);           % deg, +front -> -rear through top
Rprof = Rroof + max(0, (-(ang1+70))/55)*0.018 .* (ang1<-70);
yArc = Rprof.*sind(ang1); zArc = Rprof.*cosd(ang1);
% force front end to lip point (sheet is straight below tangent point y~+0.10):
yArc(1) = yF; zArc(1) = zF;
% rear deflector straight: 30mm long at 50deg down-aft from scroll end
% (sized so tip sits ~10 above roller top, roller sits ON ground: centre Z=40)
yE = yArc(end); zE = zArc(end);
yD = yE - 0.030*sind(50); zD = zE - 0.030*cosd(50);
% roller: dia-80, top 15 below deflector tip, centre ~40 abs (touches ground)
rRoll = 0.040; gapDR = 0.015;
zRollC = 0.040;   % abs: sits on ground
% enforce deflector tip 15 above roller top (adjust print only if drifted):
% tip abs = Zc+zD should equal zRollC+rRoll+gapDR = 95; nudge report if off
yRollC = yD - 0.005;        % just aft of tip
% front curtain: chain guard hanging from header (y = yF+0.005) down to 30 above ground
yCurtain = yF + 0.005; zCurtainTop = zF + 0.075; zCurtainBot = 0.030 - Zc;  % centre-rel
fprintf('\n=== GEOMETRY CHECK ===\n');
fprintf('lip abs Z %.0f mm (target 90) | roller centre abs (Y %.0f, Z %.0f) | deflector tip abs Z %.0f\n', ...
    lip_check, yRollC*1000, zRollC*1000, (Zc+zD)*1000);

%% 8. Print fabrication dimension sheet
fprintf('\n=========== ENCLOSURE DIMENSION SHEET (500 swath, Rcut %.0f) ===========\n', Rcut*1000);
fprintf('INNER WIDTH  : 550 (500 cut + 2x25 side clearance). Outer 556 with 3mm shell.\n');
fprintf('SIDE PLATES  : 2x 6mm MS, inner faces at +/-275. Blade tip to plate 25/side.\n');
fprintf('             : bearing seats OUTSIDE cheeks (UCP205), shaft holes dia-52, span 600.\n');
fprintf('ROTOR CENTRE : Zc %.0f above ground (bottom tip 60 above ground = cut 40-80 band).\n', Zc*1000);
fprintf('ROOF         : concentric R %.0f (Rcut %.0f + 12 gap), wrap front+58deg over top to rear-70deg.\n', Rroof*1000, Rcut*1000);
fprintf('SCROLL       : involute R %.0f -> %.0f over rear 55deg (last 55deg grows +18). Acts as fan volute + anvil.\n', Rroof*1000, (Rroof+0.018)*1000);
fprintf('WRAP TOTAL   : ~183deg (51%% of circle) - exceeds 40%% rule, drives re-cut.\n');
fprintf('FRONT SHEET  : straight tangent from roof (y +%.0f) down to lip (Y +%.0f rel centre, Z 90 abs).\n', yArc(2)*1000, yF*1000);
fprintf('FRONT MOUTH  : 90 high (ground to lip) x 550 wide. Inlet Vel ~%.1f m/s, Q ~%.2f m3/s.\n', Vin, Qin);
fprintf('CHAIN CURTAIN: full-width 6mm chain strips on 25 pitch, hung from Y +%.0f, 30..165 abs Z.\n', yCurtain*1000);
fprintf('             : swings IN only (stop bar inside) - admits grass, blocks forward throw.\n');
fprintf('DEFLECTOR    : 30 long x 550 wide x 4mm HARDOX lip at 50deg down-aft from scroll end.\n');
fprintf('             : tip ~91 abs Z, ~11 above roller top (re-cut anvil). Replaceable, 2x M10/side.\n');
fprintf('REAR OUTLET  : 70 high (deflector tip to roller top), full 550 width. Vout ~%.1f m/s.\n', Vout_target);
fprintf('REAR FLAP    : rubber 8mm (conveyor belt) 550 x 160, hung from scroll end, bottom 25 abs Z.\n');
fprintf('             : adjustable slots +/-20 (closes to 50 for mulch, opens to 90 for wet/heavy).\n');
fprintf('ROLLER       : dia-80 x 560 (full width + in cheeks), wall 4, sealed 6004 brgs, scraper bar.\n');
fprintf('             : centre Y %.0f aft of rotor, Z %.0f abs. Sets cut height with skids.\n', yRollC*1000, zRollC*1000);
fprintf('SKIDS        : 2x 6mm Hardox 300 x 80, outer faces at +/-285, slot-adjust 40-80 cut.\n');
fprintf('SKIRTS       : side rubber skirts 5mm inside cheeks, bottom 20 abs Z (dust/throw seal).\n');
fprintf('WEAR LINER   : 2mm replaceable MS arc spot-welded inside roof (front 120deg), M8 plug welds.\n');
fprintf('COUNTER-KNIFE: 1x row HARDOX teeth (10 x 40W x 60H x 8T) on scroll start, 5 off tip circle.\n');
fprintf('             : forces 2nd cut on recirculating stems - unbolt for pure finish mowing.\n');
fprintf('SHEET        : 3mm MS, 2 bends (front tangent + scroll start). All seams continuous weld outside.\n');
fprintf('DEPTH (Y)    : front lip +%.0f to roller rear %.0f = ~%.0f overall (+flap). Height roof %.0f abs.\n', ...
    yF*1000, (yRollC+rRoll)*1000, (yRollC+rRoll-yF)*1000*-1, (Zc+Rroof)*1000);
fprintf('THROW SAFETY : front curtain + side skirts + rear flap/roller labyrinth; exclusion 15m per feasibility sim.\n');
fprintf('ROTATION     : UP-CUT front (front blades go UP). Reverse wiring if clippings exit FRONT.\n');
fprintf('=======================================================================\n');

%% 9. Reference-STP verdict (do NOT copy)
fprintf('\n--- medium.stp REFERENCE VERDICT (outer boxes, mm) ---\n');
fprintf('#578/#579 end boxes 850 x 230 x 400; #598 envelope 1000 x 750 x 495.\n');
fprintf('Ours needs inner 550 W x ~450 D x 436 H (roof 388 abs + flap/roller).\n');
fprintf('Reference is 300 WIDER (850 vs 556 outer) and only 230 DEEP per box -\n');
fprintf('about half the needed fore-aft depth for roof+scroll+roller. Likely a\n');
fprintf('generic chassis/tub, not a suction volute: no concentric roof, no scroll,\n');
fprintf('no deflector/anvil, no curtain/flap/roller labyrinth. Borrow only the\n');
fprintf('idea of bolt-on end boxes for bearings/drive; ignore its proportions.\n');

%% 10. Plot side profile (Y fwd+, Z abs mm)
figure('Name','Enclosure profile');
hold on; grid on; axis equal;
% ground
plot([-250 250],[0 0],'k-','LineWidth',2);
% tip circle + drum
thc = linspace(0,360,121);
plot(Rcut*1000*sind(thc), Zc*1000+Rcut*1000*cosd(thc),'r--','LineWidth',1.2);
plot(RO*1000*sind(thc), Zc*1000+RO*1000*cosd(thc),'k-','LineWidth',2);
% housing roof+scroll (centre-rel -> abs)
plot(yArc*1000, (Zc+zArc)*1000, 'b-','LineWidth',2.5);
% front sheet extension to lip (already at lip) + curtain
plot([yArc(1) yArc(1)]*1000, [(Zc+zArc(1)) 30], 'm-','LineWidth',2);  % curtain line (schematic)
% deflector
plot([yE yD]*1000, (Zc+[zE zD])*1000, 'g-','LineWidth',2.5);
% rear flap (vertical schematic from scroll end down)
plot([yE yE]*1000, [(Zc+zE)*1000 25], 'k--');
% roller circle
thr = linspace(0,360,61);
plot(yRollC*1000+rRoll*1000*sind(thr), zRollC*1000+rRoll*1000*cosd(thr),'k-','LineWidth',2);
% centre + labels
plot(0,Zc*1000,'kx','MarkerSize',10,'LineWidth',2);
text(yF*1000, 95, 'front lip 90'); text(yE*1000,(Zc+zE)*1000+10,'scroll end');
text(yRollC*1000, zRollC*1000, 'roller d80'); text(0, Zc*1000+15, 'rotor C');
xlabel('Y fwd+ mm (rel rotor centre)'); ylabel('Z abs mm (ground=0)');
title(sprintf('500 flail enclosure: Rcut %.0f, roof R %.0f+scroll, mouth 90 / outlet 70', Rcut*1000, Rroof*1000));
legend('tip circle','drum','roof+scroll','curtain','deflector','flap','roller','Location','best');
saveas(gcf, fullfile(thisdir,'enclosure_profile.png'));
fprintf('Wrote enclosure_profile.png\n');

%% 11. Save profile coordinates for fab (centre-rel mm: y, z + abs Z)
prof = [(yArc(:))*1000, (zArc(:))*1000, (Zc+zArc(:))*1000];
save(fullfile(thisdir,'enclosure_profile.mat'),'prof','Rcut','Rroof','Zc','Wi','lipZ','outH','Vin','Qin','dP');
fprintf('Wrote enclosure_profile.mat (roof/scroll polyline, %d pts)\n', size(prof,1));
