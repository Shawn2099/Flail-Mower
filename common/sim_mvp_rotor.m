%% sim_mvp_rotor.m
% MASTER SIM - MVP rotor decision chain. Answers 5 questions in order and
% prints a BUILD SHEET. Base MATLAB only. Run from the matlab folder.
%
%   Q1 TIP SPEED  - does the drum+blade reach 35 m/s (blunt edge floor)?
%   Q2 POWER      - shaft/electrical power, torque, current; 3 kW enough?
%   Q3 PINS+TABS  - centrifugal load vs EN8 pin + E250 tab limits?
%   Q4 DRUM       - span stress, deflection, critical speed, bearings?
%   Q5 BATTERY    - runtime and area per charge on a 72V 70Ah pack?
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));
addpath(fullfile(thisdir,'specs'));

%% Locked MVP inputs (from PROJECT_INPUTS.md)
bS   = blade_straight_mulcher();   % C2: straight singles
drum = drum_50NB_medium();         % 60.3 OD x 3.65 wall x 500
pin  = pin_EN8(17);
M    = machine_500mm_tracked();
G    = grass_light_maintained();

nBlades  = 10;        % 2 helical rows of 5 (58 mm blades over 500 mm)
tabmm    = 6;   % 6mm tabs + 2 spacer washers for 8mm blade eye (lightened)
rpm_work = 2200;      % cutting rpm
rpm_cap  = 2500;      % controller hard cap = strength design point
v        = 1.0;        % m/s forward
W        = 0.500;      % m working width
Es       = G.spec_energy_J_per_m2_nom;   % 800, blunt impact cutting
Vpack = 72; Ahpack = 70; usable = 0.8;

omW = rpm_work*2*pi/60; omC = rpm_cap*2*pi/60;
pin_r = drum.OD_m/2 + 0.020;
Rcut  = pin_r + bS.pivot_to_tip_m;
Rcg   = pin_r + bS.pivot_to_cg_m;

%% Q1 - tip speed
tipW = omW*Rcut; tipC = omC*Rcut; tipMin = G.tip_speed_blunt_mps;
if tipW>=tipMin, v1='PASS'; else, v1='FAIL'; end
fprintf('\nQ1 TIP SPEED: %.1f m/s @%d (need >=%.0f) -> %s\n', tipW, rpm_work, tipMin, v1);
fprintf('   @cap %d: %.1f m/s. Do not run below %d rpm (%.1f m/s).\n', ...
    rpm_cap, tipC, ceil(tipMin/Rcut*60/2/pi), tipMin);

%% Q2 - power + motor
Pc = Es*W*v;
Pw = M.windage_ref_W*(rpm_work/3000)^3*(nBlades/10)*1.0;
Ps = Pc + Pw;
Pe = Ps/(M.trans_eff*M.motor_eff);
Tq = Ps/omW; Amps = Pe/Vpack;
m30 = motor_Mecwin_PMSM_3kW(); cont = m30.rated_power_W*m30.cont_factor;
fprintf('\nQ2 POWER: cut %.0f W + windage %.0f W = %.0f W shaft, %.0f W elec\n', Pc, Pw, Ps, Pe);
if Pe<cont, v2='3kW OK'; else, v2='TOO BIG'; end
fprintf('   torque %.2f Nm, current %.1f A @%dV. Uses %.0f%% of 3kW continuous -> %s\n', ...
    Tq, Amps, Vpack, Pe/cont*100, v2);

%% Q3 - pin + tab at the CAP rpm (worst case)
Fc = bS.mass_kg*omC^2*Rcg;
tau = Fc/pin.area_m2/1e6;
sig = Fc*0.012/pin.Z_m3/1e6;
brg = Fc/((tabmm/1000)*pin.dia_m)/1e6;
fprintf('\nQ3 PIN+TAB @cap: Fc %.2f kN/blade | shear %.0f/%.0f MPa | bend %.0f/%.0f MPa | hole-brg %.0f MPa\n', ...
    Fc/1000, tau, pin.shear_allow_MPa, sig, pin.bending_allow_MPa, brg);
ok3 = tau<pin.shear_allow_MPa && sig<pin.bending_allow_MPa;
if ok3, v3='PASS - dia-17 EN8, 6mm tabs'; else, v3='FAIL'; end
fprintf('   -> %s\n', v3);

%% Q4 - drum span, critical, bearings
m_tabs  = nBlades*0.05*0.04*(tabmm/1000)*7850;
m_discs = 2*pi/4*0.14^2*0.008*7850;
sb = shaft_bearing_25();
m_shaft = pi/4*sb.shaft_dia_m^2*sb.shaft_len_m*7850;
m_rot = drum.mass_kg + nBlades*bS.mass_kg + m_tabs + m_discs + m_shaft;
Wt = m_rot*9.81;
I_drum = pi/64*(drum.OD_m^4 - drum.ID_m^4);
sig_d = (Wt*sb.span_m/8)*(drum.OD_m/2)/I_drum/1e6;
dlt = Wt*sb.span_m^3/(48*drum.E_Pa*I_drum)*1000;
ncrit = (1/2/pi)*sqrt(9.81/(dlt/1000))*60;
if ncrit>6000, v4='PASS'; else, v4='FAIL'; end
fprintf('\nQ4 DRUM: rotor %.1f kg | tube %.2f MPa | sag %.4f mm | critical ~%.0f rpm | brg <%.1f kN vs %.0f -> %s\n', ...
    m_rot, sig_d, dlt, ncrit, (Wt/2+400)/1000, sb.C_dyn_kN, v4);

%% Q5 - battery
Wh = Vpack*Ahpack*usable;
hrs = Wh/Pe; ha = hrs*W*v*3600/10000;
fprintf('\nQ5 BATTERY (%dV %dAh, %.0f Wh usable): %.1f h mowing -> %.2f ha/charge\n', ...
    Vpack, Ahpack, Wh, hrs, ha);

%% BUILD SHEET
fprintf('\n=========== MVP BUILD SHEET ===========\n');
fprintf('Drum     : 50NB Medium pipe 60.3 OD x 3.65 wall x 500 (IS 1239)\n');
fprintf('Blades   : 10x straight mulcher 340 g, dia-17 hole (2 helical rows of 5)\n');
fprintf('Tabs     : %dmm MS flat 50mm wide, forked, dia-17.2 holes\n', tabmm);
fprintf('Pins     : dia-17 EN8 bright, R-clip, overhang <=12 mm\n');
fprintf('Shaft/brg: dia-25 EN8, UCP205 sealed, 600 span; 8mm end discs\n');
fprintf('Motor    : 3 kW PMSM, 72 V; controller cap %d rpm; work %d rpm\n', rpm_cap, rpm_work);
fprintf('Draw     : ~%.0f W elec in light grass (~%.0f A); %.2f ha per charge\n', Pe, Amps, ha);
fprintf('=======================================\n');

%% Plots
figure('Name','MVP rotor');
rpms = 1500:100:2600; om = rpms*2*pi/60;
subplot(2,1,1); plot(rpms, om*Rcut, 'o-','LineWidth',1.5); grid on;
yline(tipMin,'r--',sprintf('%.0f m/s blunt floor',tipMin)); xline(rpm_cap,'g--','cap');
xlabel('rpm'); ylabel('tip speed m/s'); title('Q1: tip speed (50NB + straight)');
subplot(2,1,2);
Pws = M.windage_ref_W*(rpms/3000).^3*(nBlades/10);
plot(rpms, Es*W*v + Pws, 'o-','LineWidth',1.5); grid on;
yline(cont*(M.trans_eff*M.motor_eff),'r--','3kW cont (shaft)');
xlabel('rpm'); ylabel('shaft W'); title('Q2: shaft power vs rpm');
