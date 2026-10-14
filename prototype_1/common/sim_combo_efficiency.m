%% sim_combo_efficiency.m
% Energy-per-hectare ranking of blade combos C1..C4 for LIGHT grass.
% Shaft = specific-energy cutting + windage (scaled by blade count, drag,
% and rpm^3). Electrical via transmission + motor efficiency.
% Base MATLAB only. Run from the matlab folder.
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));
addpath(fullfile(thisdir,'specs'));

bS = blade_straight_mulcher();
bJ = blade_jtype_mulcher();
bH = blade_hammer();
M  = machine_500mm_tracked();
G  = grass_light_maintained();
m30 = motor_Mecwin_PMSM_3kW();

rpmW = 2200; v = 1.0; W = M.working_width_m;
Es = G.spec_energy_J_per_m2_nom;
wind_ref = M.windage_ref_W;   % @3000rpm, 10 straight blades

% name, total blades, drag factor, Es factor (recut penalty)
names = {'C1: J single (10)', 'C2: straight (10)', 'C3: hammer (8)', 'C5: mixed S/J (10)'};
nB    = [10 10 8 10];
drag  = [1.3 1.0 1.5 1.15];
esf   = [1.2 1.0 1.5 1.1];   % hammer 1.5x: blunt 1050 g impact edge smashes, not slices

fprintf('\n=== COMBO EFFICIENCY @%drpm, v=%.1fm/s, Es=%d J/m2 ===\n', rpmW, v, Es);
fprintf('%-20s Pcut  Pwind Pshaft Pelec  A/h   batt70Ah\n', 'combo');
Pshaft = zeros(1,4); Pelec = Pshaft;
for i = 1:4
    Pc = Es*esf(i)*W*v;
    Pw = wind_ref*(rpmW/3000)^3*(nB(i)/10)*drag(i);
    Pshaft(i) = Pc + Pw;
    Pelec(i)  = Pshaft(i)/(M.trans_eff*M.motor_eff);
    cov = W*v*3600/10000;                       % ha/h
    hrs = 72*70*0.8/Pelec(i);                   % 72V 70Ah pack, 80% usable
    fprintf('%-20s %3.0fW  %3.0fW  %3.0fW  %3.0fW  %.2f  %.1fh (%.2fha)\n', ...
        names{i}, Pc, Pw, Pshaft(i), Pelec(i), cov, hrs, hrs*cov);
end
cont30 = m30.rated_power_W*m30.cont_factor;
fprintf('\n3kW motor continuous ~%.0f W. Worst combo uses %.0f%% of it.\n', ...
    cont30, max(Pelec)/cont30*100);

%% Sensitivity: Es 500..1500 J/m2
Es_sweep = 500:100:1500;
figure('Name','Combo efficiency');
subplot(2,1,1);
hold on; grid on;
for i = 1:4
    Ps = Es_sweep*esf(i)*W*v + wind_ref*(rpmW/3000)^3*(nB(i)/10)*drag(i);
    plot(Es_sweep, Ps, 'o-', 'LineWidth', 1.5, 'DisplayName', names{i});
end
yline(cont30*(M.trans_eff*M.motor_eff),'r--','3kW cont (shaft)');
xlabel('specific energy J/m2'); ylabel('shaft power W');
title('Shaft power vs grass load'); legend('location','northwest');
subplot(2,1,2);
bar(Pshaft); grid on;
set(gca,'XTickLabel',{'C1','C2','C3','C4'});
ylabel('shaft watts'); title('Nominal shaft power by combo (light grass)');
[~,best] = min(Pshaft);
fprintf('Most efficient: %s (%.0f W shaft).\n', names{best}, Pshaft(best));
