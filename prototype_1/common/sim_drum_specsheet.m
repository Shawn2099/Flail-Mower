%% sim_drum_specsheet.m
% EXACT DRUM SPEC by constraint framework (Indian standard pipes only).
% Framework: requirements -> hard constraints -> candidate pipes (IS 1239)
% -> analysis per candidate -> winner -> full dimension sheet.
% Constraints: (1) tip>=35 m/s @2200 [blunt floor]  (2) wall>=tab/2 [weld]
% (3) sag<=0.05mm (4) critical>=6000rpm (5) lightest passes- all wins.
% Base MATLAB only. Run from the matlab folder.
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));
addpath(fullfile(thisdir,'specs'));

bS = blade_straight_mulcher();
M  = machine_500mm_tracked();
rpmW = 2200; rpmC = 2500; omW = rpmW*2*pi/60; omC = rpmC*2*pi/60;
stand = 0.020; tabT = 0.006; need_tip = 35; droop = 0.97;  % 3% governor droop under load

% IS 1239 ERW candidates: [NB label, ODmm, wallmm, class] (dealer-verified sizes)
P = {'40NB-H',48.3,4.05; '50NB-M',60.3,3.65; '50NB-H',60.3,5.40; ...
     '65NB-M',76.1,4.50; '65NB-H',76.1,5.40};
fprintf('\n=== CANDIDATE CHECK (10 straights, 500 drum) ===\n');
fprintf('pipe      Rcut tip2200 tipCap Fc@cap weld sag     crit    mass  verdict\n');
pass = false(size(P,1),1);
for i = 1:size(P,1)
    OD = P{i,2}/1000; wl = P{i,3}/1000; ID = OD-2*wl;
    pin_r = OD/2 + stand; Rcut = pin_r + bS.pivot_to_tip_m;
    Rcg = pin_r + bS.pivot_to_cg_m;
    Fc = bS.mass_kg*omC^2*Rcg;
    mrot = pi/4*(OD^2-ID^2)*0.5*7850 + 10*0.34 + 1.5 + 2.7;  % tube+blades+tabs+shaft
    I = pi/64*(OD^4-ID^4);
    sag = mrot*9.81*0.6^3/(48*200e9*I)*1000;
    ncr = (1/2/pi)*sqrt(9.81/(sag/1000))*60;
    c1 = omW*Rcut*droop>=need_tip; c2 = wl>=tabT/2; c3 = sag<=0.05; c4 = ncr>=6000;
    pass(i) = c1&&c2&&c3&&c4;
    if pass(i), vd='PASS'; else, vd='FAIL'; end
    if c2, wd='ok'; else, wd='THIN'; end
    fprintf('%-8s %3.0fmm %4.1f   %4.1f   %4.2fkN %s  %.3fmm %5.0f %4.1fkg %s\n', ...
        P{i,1}, Rcut*1000, omW*Rcut, omC*Rcut, Fc/1000, wd, sag, ncr, mrot, vd);
end
masses = zeros(size(P,1),1);
for i = 1:size(P,1)
    OD = P{i,2}/1000; wl = P{i,3}/1000; ID = OD-2*wl;
    masses(i) = pi/4*(OD^2-ID^2)*0.5*7850;
end
masses(~pass) = Inf;
[~,win] = min(masses);
fprintf('\nWINNER: %s (%.1f x %.1f mm). Lightest pipe passing all constraints.\n', ...
    P{win,1}, P{win,2}, P{win,3});

%% DIMENSION SHEET for winner (all mm)
OD = P{win,2}; wl = P{win,3}; IDd = OD-2*wl;
pin_r = OD/2 + 20; Rcut = pin_r + 108;   % mm
fprintf('\n=========== DRUM DIMENSION SHEET (%s) ===========\n', P{win,1});
fprintf('1. Tube      : %.1f OD x %.1f wall x %.0f ID x 500 LG, IS 1239 %s\n', OD, wl, IDd, P{win,1});
fprintf('2. End discs : 2x dia-%.0f x 8 thk MS (covers pin circle r=50 + margin), welded to tube ends\n', OD+80);
fprintf('3. Shaft     : dia-25 x 700 LG EN8 (500 drum + 2x100 bearing/drive overhang)\n');
fprintf('4. Bearings  : 2x UCP205, span 600 (50 overhang each end)\n');
fprintf('5. Stations  : 10x at x = 15 + k*52.2 mm (k=0..9) -> 15 ... 485 mm\n');
fprintf('6. Helix     : 36 deg steps (0,36,...,324), alternate hand each row\n');
fprintf('7. Tabs      : 10x MS flat 50W x 40H x 6T + 2 spacer washers/eye, hole dia-17.2 at 20 above tube\n');
fprintf('8. Bolts     : 10x turned shoulder dia-17 x 40 (M14 thread + nyloc), load arm <=14\n');
fprintf('   (dia-17 is non-std: lathe job. Drive pulley on dia-25 shaft via taper-lock bush.)\n');
fprintf('9. Blades    : 10x straight 340 g (5 left-hand + 5 right-hand rows)\n');
fprintf('10. Weld     : 4 mm fillet, full 50 mm both tab sides (E7018)\n');
fprintf('11. Housing  : inner width >=550; rotor centre to roof >=%.0f (Rcut %.0f + 60)\n', Rcut+60, Rcut);
fprintf('12. Balance  : static-balance assembly, trial weights on end discs\n');
fprintf('13. Rotation : UP-CUT at front (front-bottom blades travel UP, throw to rear).\n');
fprintf('    Wire motor for this direction; verify: clippings must exit the REAR flap.\n');
fprintf('14. Drive    : 2x SPZ 100x3-1610 1:1 (2 belts now, 3rd adds 5kW); electronic torque limit 12 Nm, belt slip backup.\n');
fprintf('15. Height   : full-width rear roller dia-114 (100NB-L stock) + skid shoes; cut height 40-80 mm.\n');
fprintf('    Front chain/rubber guard across full width (throw-out protection).\n');
fprintf('16. Blade fit: straights symmetric; J hooks face ROTATION direction (lip forward).\n');
fprintf('    Replace blades in opposite (180 deg) pairs to keep balance.\n');
fprintf('Cutting circle dia %.0f mm; tip %.1f m/s @2200, %.1f @cap 2500\n', ...
    2*Rcut, omW*Rcut/1000, omC*Rcut/1000);
fprintf('==================================================\n');
