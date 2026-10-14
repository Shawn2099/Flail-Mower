%% sim_feasibility_edge_cases.m
% FEASIBILITY from motor + blade data alone: can it cut grass? brush?
% What survives a rock? Derives drum spec, operating envelope, and the
% protection hardware the edge cases demand. Base MATLAB only.
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));
addpath(fullfile(thisdir,'specs'));

bS = blade_straight_mulcher();
drum = drum_50NB_medium();
M  = machine_500mm_tracked();
m30 = motor_Mecwin_PMSM_3kW();
W = 0.500; rpmW = 2200; omW = rpmW*2*pi/60;
pin_r = drum.OD_m/2 + 0.020;
Rcut = pin_r + bS.pivot_to_tip_m;
cont_elec = m30.rated_power_W*m30.cont_factor;   % 1950 W
cont_shaft = cont_elec*(M.trans_eff*M.motor_eff);
Pw = M.windage_ref_W*(rpmW/3000)^3;              % 10 straights

%% 1. GRASS feasibility (Es 500-1500, v 0.5-1.5)
fprintf('\n=== 1. GRASS: power needed vs 1950 W continuous ===\n');
fprintf('Es\\v    0.5m/s  1.0m/s  1.5m/s   (shaft W)\n');
for Es = [500 800 1500]
    Ps = Es*W*[0.5 1 1.5] + Pw;
    if max(Ps)<cont_shaft, yn='YES'; else, yn='NO'; end
    fprintf('%-5d %6.0fW  %6.0fW  %6.0fW   max %.0f%% of cont -> %s\n', ...
        Es, Ps, max(Ps)/cont_shaft*100, yn);
end

%% 2. BRUSH envelope: max cuttable Es vs forward speed
fprintf('\n=== 2. BRUSH: max specific energy vs speed (3kW cont) ===\n');
fprintf('v(m/s) Es_max  meaning\n');
vs = [0.3 0.5 0.75 1.0 1.5];
for v = vs
    Em = (cont_shaft - Pw)/(W*v);
    if Em>8000, tag='heavy brush OK'; elseif Em>3000, tag='light brush/saplings OK';
    elseif Em>1500, tag='dense tall grass only'; else, tag='-'; end
    fprintf('%.2f   %4.0f J/m2  %s\n', v, Em, tag);
end

%% 3. ROCK STRIKE: impulse on one straight blade
m = bS.mass_kg; vtip = omW*Rcut;
fprintf('\n=== 3. ROCK STRIKE (one 340 g blade @%.1f m/s) ===\n', vtip);
for tstop = [0.003 0.005 0.010]
    F = m*vtip/tstop; Tq = F*Rcut;
    fprintf('stop in %.0fms: blade force %.1f kN -> rotor torque spike %.0f Nm (nominal 2.4!)\n', ...
        tstop*1000, F/1000, Tq);
end
slip = 12;   % belt slip-clutch setting, Nm
fprintf('Motor sees only the %.0f Nm slip setting; the rest dies in belt slip.\n', slip);
fprintf('WITHOUT slip protection the spike reaches the motor spline -> shaft/spline failure.\n');

%% 4. Projectile energy (housing design input)
fprintf('\n=== 4. DEBRIS ENERGY ===\n');
fprintf('Tip energy per blade: %.0f J. A thrown stone at half tip speed: %.0f J.\n', ...
    0.5*m*vtip^2, 0.5*0.05*(vtip/2)^2);
fprintf('Housing: 3-4 mm steel + rubber rear flap; exclusion zone 15 m.\n');

%% 6. STEM-LEVEL CUT AUDIT: can one straight blade sever the grass in its path?
% Lawn ~10000 stems/m2; strip per blade pass = width x bite; stem budget 1 J
% (conservative; literature single-stem shear is ~0.01-0.1 J).
stems_m2 = 10000; v = 1.0;
bite = v*1000/(10*rpmW/60);   % mm per blade pass
strip = W*bite/1000;                             % m2 per blade pass
nstems = stems_m2*strip;
Etip = 0.5*bS.mass_kg*(omW*(pin_r+bS.pivot_to_tip_m))^2;
fprintf('\n=== 5. STEM AUDIT (straight blade, light lawn) ===\n');
fprintf('Bite %.1f mm/pass -> %.0f stems in the strip, need ~%.0f J worst-case.\n', ...
    bite, nstems, nstems*1.0);
fprintf('Blade carries %.0f J. Margin: %.0fx over worst-case stem budget.\n', Etip, Etip/(nstems*1.0));
fprintf('For reference: nylon trimmer line severs grass on speed alone with far less\n');
fprintf('energy per unit mass. A 340 g steel flail at 36 m/s cannot fail to sever 60 mm grass.\n');
fprintf('\n=== 6. DRUM SPEC FROM MOTOR+BLADES ===\n');
fprintf('Motor band 2000-2800 rpm x blade reach 108 mm -> drum 50-76 mm OD keeps\n');
fprintf('tip speed 35-46 m/s across grass AND brush modes. 50NB (60.3) chosen:\n');
fprintf('lightest standard pipe clearing 35 m/s at 2200 with weld room.\n');

figure('Name','Feasibility');
subplot(2,1,1);
vv = 0.3:0.05:1.5;
plot(vv, (cont_shaft-Pw)./(W*vv), 'LineWidth', 1.5); grid on;
yline(800,'g--','light grass'); yline(3000,'y--','light brush'); yline(8000,'r--','heavy brush');
xlabel('forward speed m/s'); ylabel('max cuttable Es J/m2');
title('Brush envelope (3kW continuous)'); ylim([0 12000]);
subplot(2,1,2);
bar([558 689 1739 1950]); grid on;
set(gca,'XTickLabel',{'grass shaft','grass elec','brush elec','3kW cont'});
ylabel('W'); title('Headroom illustration');
