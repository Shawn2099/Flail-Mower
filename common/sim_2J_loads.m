%% sim_2J_loads.m — LOADS, POWER, BATTERY for the 2J program (20 J singles).
% Per-blade checks at work/cap rpm + rotor mass + runtime. Base MATLAB only.
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));
addpath(fullfile(thisdir,'specs'));

C = config_2J_opposing();
bJ = blade_jtype_mulcher();
M  = machine_500mm_tracked();
W = 0.500; Es = 800; eff = M.trans_eff*M.motor_eff;
pin_r = 0.03015 + 0.020; Rcg = pin_r + bJ.pivot_to_cg_m;

fprintf('\n=== 2J LOADS (per blade, single-bolt mount, 14 mm arm) ===\n');
fprintf('rpm   Fc(kN) shear bend holeBrg\n');
for rpm = [C.rpm_work C.rpm_cap]
    om = rpm*2*pi/60;
    Fc = bJ.mass_kg*om^2*Rcg;
    tau = Fc/(pi*0.017^2/4)/1e6;
    sig = Fc*0.014/(pi*0.017^3/32)/1e6;
    brg = Fc/((8/1000)*0.017)/1e6;
    if tau<150 && sig<180, v='PASS'; else, v='CHECK'; end
    fprintf('%d  %.2f   %3.0f   %3.0f   %3.0f     %s\n', rpm, Fc/1000, tau, sig, brg, v);
end

%% Power + battery (rotor + 200 W traction), 48V20Ah usable 768 Wh
fprintf('\n=== 2J POWER vs SPEED (J @2300, Es 960 with hook penalty) ===\n');
fprintf('v(m/s) Pshaft Pelec  runtime48V20Ah\n');
for v = [0.5 0.75 1.0 1.25]
    Pc = Es*1.2*W*v;
    Pw = M.windage_ref_W*(C.rpm_work/3000)^3*(20/10)*1.3;
    Pe = (Pc+Pw)/eff + 200;
    fprintf('%.2f   %3.0fW   %4.0fW  %.0f min\n', v, Pc+Pw, Pe, 768/Pe*60);
end

%% Rotor mass + spin-up
mrot = 3.65 + 1.93 + 2.70 + 20*0.132 + 20*0.075 + 20*bJ.mass_kg;
I = 20*bJ.mass_kg*Rcg^2 + 0.001;
KE = 0.5*I*(C.rpm_cap*2*pi/60)^2;
fprintf('\nRotor ~%.1f kg (MVP 14.1). Spin-up %.1f kJ -> %.1f s at 3 kW.\n', ...
    mrot, KE/1000, KE/(3000*0.8));
fprintf('Motor load @1 m/s: %.0f%% of continuous. J hooks face rotation (lip forward).\n', ...
    (((Es*1.2*W*1.0 + M.windage_ref_W*(C.rpm_work/3000)^3*2*1.3)/eff)/1950*100));
