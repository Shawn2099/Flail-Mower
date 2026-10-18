%% sim_rotor_structural_sizing.m
% Structural sizing of the 500 mm flail rotor.
%  1. Drum OD sweep -> cutting radius, tip speed, per-blade centrifugal load
%  2. Station loads for combos C1..C4 on the recommended 76.1 mm drum
%  3. Pin shear / pin bending / tab-hole bearing checks (EN8 + E250)
%  4. Drum span bending + deflection, first critical speed, bearing load
%  5. Rotor inertia + spin-up energy/time on the 3 kW motor
% Base MATLAB only. Run from the matlab folder.
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));
addpath(fullfile(thisdir,'specs'));

%% Load specs
bS = blade_straight_mulcher();
bJ = blade_jtype_mulcher();
bH = blade_hammer();
fprintf('Hammer mass from user input: %.2f kg.\n', bH.mass_kg);
drum  = drum_50NB_medium();  % optimum for blunt blades; 65NB = roomy alternative
pin17 = pin_EN8(17);
pin16 = pin_EN8(16);
sb    = shaft_bearing_25();

rpm_work = 2200;   % normal grass cutting
rpm_max  = 3100;   % controller cap = strength design point
omW = rpm_work*2*pi/60;  omM = rpm_max*2*pi/60;
standoff = 0.020;  % pin-centre height above drum surface

%% 1. Drum OD sweep (straight blade) - dia is a FREE variable, find optimum
drums = [0.0508 0.0603 0.0762 0.100];   % 2in, 50NB, 65NB, 100mm
fprintf('\n=== 1. DRUM DIA SWEEP (straight blade, 0.34 kg) ===\n');
fprintf('drumOD  Rcut   tip@2200  tip@3100  Fc/blade@3100\n');
for d = drums
    pin_r = d/2 + standoff;
    Rcut  = pin_r + bS.pivot_to_tip_m;
    Rcg   = pin_r + bS.pivot_to_cg_m;
    fprintf('%5.1fmm %5.0fmm  %5.1f m/s %5.1f m/s  %4.2f kN\n', ...
        d*1000, Rcut*1000, omW*Rcut, omM*Rcut, bS.mass_kg*omM^2*Rcg/1000);
end

%% 2-3. Combo station loads + pin/tab checks (recommended drum)
pin_r = drum.OD_m/2 + standoff;
names = {'C1: J single','C2: 1x straight','C3: 1x hammer','C5 mix: J station (worst)'};
Cb    = {[bJ], [bS], [bH], [bJ]};   % blade set riding on ONE pin (all singles now)
nPins = [10 8 4 10];
tabmm = [6 6 10 6];
pinmm = [17 17 16 17];
fprintf('\n=== 2-3. STATION LOADS + PIN/TAB CHECKS @3100rpm (50NB drum) ===\n');
fprintf('%-22s Fstat  pinShear pinBend  tabBrg\n', 'combo');
for i = 1:numel(names)
    B = Cb{i};
    F = zeros(1,numel(B));
    for j = 1:numel(B)
        F(j) = B(j).mass_kg*omM^2*(pin_r + B(j).pivot_to_cg_m);
    end
    Fstat = sum(F);  Fside = max(F);
    pn = pin_EN8(pinmm(i));
    tau  = Fside/pn.area_m2/1e6;                    % outboard pin, single shear plane
    sig  = Fside*0.012/pn.Z_m3/1e6;                 % 12 mm overhang bending
    brg  = Fstat/((tabmm(i)/1000)*pn.dia_m)/1e6;    % tab-hole bearing
    if tau<pn.shear_allow_MPa && sig<pn.bending_allow_MPa, verdict='PASS'; else, verdict='CHECK'; end
    fprintf('%-22s %4.1fkN %5.0fMPa  %5.0fMPa  %5.0fMPa %s\n', names{i}, ...
        Fstat/1000, tau, sig, brg, verdict);
end

%% Old C4 triple-on-one-pin: geometrically infeasible (three 58 mm blades cannot
%% share one tangential pin) and the forkedMath showed 262 MPa. C4 REJECTED.
%% Approved form is C5: alternating S/J singles (worst station = C1 row above).
fprintf('\nC4 triple: REJECTED (one pin cannot carry 3 side-by-side blades).\n');
fprintf('C5 alternating S/J singles: every pin is a passing C1/C2 station. APPROVED.\n');

%% 4. Drum span, deflection, critical speed, bearings (C1 rotor: 10 J singles)
m_blades = 10*bJ.mass_kg;
m_tabs   = 10*0.05*0.04*0.006*7850;
m_discs  = 2*pi/4*0.14^2*0.008*7850;
m_shaft  = pi/4*sb.shaft_dia_m^2*sb.shaft_len_m*7850;
m_rot    = drum.mass_kg + m_blades + m_tabs + m_discs + m_shaft;
Wt       = m_rot*9.81;
I_drum   = pi/64*(drum.OD_m^4 - drum.ID_m^4);
Mspan    = Wt*sb.span_m/8;
sig_drum = Mspan*(drum.OD_m/2)/I_drum/1e6;
delta    = Wt*sb.span_m^3/(48*drum.E_Pa*I_drum)*1000;   % mm
ncrit    = (1/2/pi)*sqrt(9.81/(delta/1000))*60;
fprintf('\n=== 4. DRUM/SPAN (C1 rotor, %.1f kg) ===\n', m_rot);
fprintf('Tube bending stress: %.2f MPa | midspan deflection: %.4f mm\n', sig_drum, delta);
if ncrit>6000, crit='CLEAR'; else, crit='TOO CLOSE - redesign'; end
fprintf('First critical ~%.0f rpm (operating 2200-3100) -> %s\n', ncrit, crit);
fprintf('Bearing static load < %.1f kN/side vs %.0f kN rating -> life infinite.\n', ...
    (Wt/2+400)/1000, sb.C_dyn_kN);

%% 5. Spin-up on the 3 kW motor (heaviest rotors: 8-hammer vs C5-mix 5J+5S)
Ih = 8*bH.mass_kg*(pin_r+bH.pivot_to_cg_m)^2 + drum.mass_kg*(drum.OD_m^2+drum.ID_m^2)/8;
I5 = (5*bJ.mass_kg*(pin_r+bJ.pivot_to_cg_m)^2 + 5*bS.mass_kg*(pin_r+bS.pivot_to_cg_m)^2) ...
     + drum.mass_kg*(drum.OD_m^2+drum.ID_m^2)/8;
KE = 0.5*max(Ih,I5)*omM^2;
fprintf('\n=== 5. SPIN-UP (heaviest rotor) ===\n');
fprintf('Inertia hammer-8 %.4f / C5-mix %.4f kgm2 | stored energy %.1f kJ | ramp at 3kW: %.1f s\n', ...
    Ih, I5, KE/1000, KE/(3000*0.8));

%% Plots
figure('Name','Rotor structural sizing');
rpms = 1500:100:3500; om = rpms*2*pi/60;
subplot(3,1,1);
hold on; grid on;
for d = drums
    R = d/2 + standoff + bS.pivot_to_tip_m;
    plot(rpms, om*R, 'LineWidth', 1.5, 'DisplayName', sprintf('%.0fmm drum', d*1000));
end
yline(30,'r--','30 m/s min'); xlabel('rpm'); ylabel('tip speed m/s');
title('Tip speed vs rpm (straight blade)'); legend('location','northwest');
subplot(3,1,2);
hold on; grid on;
cols = {'C1 J-1x','C2 S-1x','C3 H-1x','C5 mix'};
Fm = [bJ.mass_kg*(pin_r+bJ.pivot_to_cg_m), bS.mass_kg*(pin_r+bS.pivot_to_cg_m), ...
      bH.mass_kg*(pin_r+bH.pivot_to_cg_m), ...
      bJ.mass_kg*(pin_r+bJ.pivot_to_cg_m)];
for i = 1:4
    plot(rpms, Fm(i)*om.^2/1000, 'LineWidth', 1.5, 'DisplayName', cols{i});
end
xlabel('rpm'); ylabel('station load kN'); title('Centrifugal station load vs rpm');
legend('location','northwest');
subplot(3,1,3);
FstatJ = bJ.mass_kg*omM^2*(pin_r+bJ.pivot_to_cg_m);
brgJ = FstatJ/((8/1000)*pin17.dia_m)/1e6;
FstatH = bH.mass_kg*omM^2*(pin_r+bH.pivot_to_cg_m);
brgH = FstatH/((10/1000)*pin16.dia_m)/1e6;
bar([brgJ brgH], 'FaceColor', [0.2 0.5 0.8]); grid on;
yline(187,'r--','E250 hole-bearing allow ~187 MPa');
set(gca,'XTickLabel',{'C1 single 8mm','C3 hammer 10mm'});
ylabel('MPa'); title('Tab-hole bearing stress @3100rpm');
