%% sim_battery_speed.m
% Battery + forward-speed sweep for the MVP (20-30 min runtime target).
% Rotor-only power + traction allowance; 48V vs 72V packs; checks whether
% 48V can still spin the rotor to the 2500 rpm cap (PMSM speed ~ voltage).
% Base MATLAB only. Run from the matlab folder.
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));
addpath(fullfile(thisdir,'specs'));

M  = machine_500mm_tracked();
G  = grass_light_maintained();
W  = 0.500; Es = G.spec_energy_J_per_m2_nom;
rpmW = 2200; rpm_cap = 2500;
nBlades = 10; drag = 1.0;

Pw = M.windage_ref_W*(rpmW/3000)^3*(nBlades/10)*drag;  % windage @2200, rpm fixed
P_traction_W = 200;    % allowance: tracks + steering on flat clean ground

% candidate packs: [voltage, Ah]
packs = [48 15; 48 20; 72 10; 72 15];
usable = 0.8;

fprintf('\n=== BATTERY + SPEED SWEEP (rotor + %dW traction, 30-min target) ===\n', P_traction_W);
vs = 0.5:0.25:1.5;
fprintf('v(m/s) Prot  Ptot  I@48V I@72V | ');
for p = 1:size(packs,1), fprintf('%dV%dAh-min ', packs(p,1), packs(p,2)); end
fprintf('| ha/30min\n');
RUNTIME = zeros(numel(vs), size(packs,1));
for k = 1:numel(vs)
    v = vs(k);
    Prot = (Es*W*v + Pw)/(M.trans_eff*M.motor_eff);
    Pt = Prot + P_traction_W;
    RUNTIME(k,:) = packs(:,1).*packs(:,2)*usable/Pt*60;
    fprintf('%.2f   %3.0fW %4.0fW %4.1fA %4.1fA | ', v, Prot, Pt, Pt/48, Pt/72);
    for p = 1:size(packs,1), fprintf('%5.0f ', RUNTIME(k,p)); end
    fprintf('| %.3f\n', W*v*1800/10000);
end

%% 48V rpm-headroom check
fprintf('\n=== VOLTAGE vs RPM CHECK ===\n');
fprintf('Rotor cap needs %d rpm. PMSM speed scales ~ with voltage.\n', rpm_cap);
fprintf('If 4000 rpm max is quoted at 72V, 48V gives roughly %d rpm max.\n', round(4000*48/72));
fprintf('That leaves almost no headroom over the %d cap under load.\n', rpm_cap);
fprintf('RECOMMENDATION: confirm with Mecwin that the 3kW unit holds %d rpm on 48V;\n', rpm_cap);
fprintf('otherwise run 60V or 72V. Controller already supports all three.\n');

%% Recommendation for 30 min + margin
fprintf('\n=== PICK (30 min mowing + reserve) ===\n');
fprintf('48V 20Ah (960 Wh): lightest/cheapest, IF Mecwin confirms 48V rpm. Else 72V 15Ah.\n');
fprintf('Either way one pack runs rotor + traction for the MVP; split packs later.\n');

%% Plot
figure('Name','Battery vs speed');
hold on; grid on;
for p = 1:size(packs,1)
    plot(vs, RUNTIME(:,p), 'o-', 'LineWidth', 1.5, ...
        'DisplayName', sprintf('%dV %dAh', packs(p,1), packs(p,2)));
end
yline(30,'r--','30-min target');
xlabel('forward speed m/s'); ylabel('runtime minutes (rotor+traction)');
title('MVP runtime vs speed'); legend('location','northeast');
