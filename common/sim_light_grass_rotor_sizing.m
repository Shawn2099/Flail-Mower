%% sim_light_grass_rotor_sizing.m
% Sizes the 500 mm flail rotor for LIGHT MAINTAINED GRASS (2-3 in, clean).
% Base MATLAB only. Run: add specs folder to path, then F5.
%   addpath('specs'); sim_light_grass_rotor_sizing
clear; clc; close all;

thisdir = fileparts(mfilename('fullpath'));
addpath(fullfile(thisdir,'specs'));

%% Load specs (each file = one component, edit values there)
bS = blade_straight_mulcher();
bJ = blade_jtype_mulcher();
bH = blade_hammer();
if isnan(bH.mass_kg)
    bH.mass_kg = bH.mass_est_kg;
    fprintf('NOTE: hammer mass not on datasheet, using estimate %.2f kg - WEIGH IT.\n', bH.mass_kg);
end
m12 = motor_Mecwin_BLDC_1p2kW();
m30 = motor_Mecwin_PMSM_3kW();
m45 = motor_Mecwin_PMSM_4p5kW();
M   = machine_500mm_tracked();
G   = grass_light_maintained();

%% Candidate matrix: 3 blades x 3 drum ODs x RPM sweep
blades = {bS, bJ, bH};
drums  = M.drum_OD_candidates_m;
rpms   = M.rotor_speed_sweep_rpm;
v      = M.forward_speed_mps_nom;
W      = M.working_width_m;
Es     = G.spec_energy_J_per_m2_nom;

fprintf('\n=== LIGHT GRASS CASE: %.0f mm swath @ %.1f m/s, Es=%d J/m2 ===\n', ...
    W*1000, v, Es);
fprintf('%-12s %-8s | tip(m/s) Fcent(kN/blade) Pcut(W) Pwind(W) Pshaft(W) Tq(Nm)\n', 'blade','drummm');
fprintf('%s\n', repmat('-',1,78));

results = [];
for bi = 1:numel(blades)
    b = blades{bi};
    for di = 1:numel(drums)
        pin_r  = drums(di)/2 + M.pin_standoff_m;   % pin-centre radius
        Rcut   = pin_r + b.pivot_to_tip_m;          % cutting radius
        Rcg    = pin_r + b.pivot_to_cg_m;           % blade CG radius
        for rpm = rpms
            om   = rpm*2*pi/60;
            tip  = om*Rcut;
            Fc   = b.mass_kg*om^2*Rcg;
            Pc   = Es*W*v;
            Pw   = M.windage_ref_W*(rpm/M.windage_ref_rpm)^3;
            Ps   = Pc + Pw;
            Tq   = Ps/om;
            results = [results; bi di rpm tip Fc Pc Pw Ps Tq Rcut]; %#ok<AGROW>
            if rpm==3000 || rpm==2500
                fprintf('%-12s %-8.0f | %6.1f   %6.2f          %4.0f   %4.0f    %4.0f      %4.1f\n', ...
                    b.type, drums(di)*1000, tip, Fc/1000, Pc, Pw, Ps, Tq);
            end
        end
    end
end

%% Motor check at nominal 3000 rpm, 76.2mm drum, straight blade
Pn  = Es*W*v + M.windage_ref_W;          % shaft W
Tn  = Pn/(3000*2*pi/60);
Pe  = Pn/(M.trans_eff*M.motor_eff);      % electrical W
fprintf('\n--- Nominal point (straight, 76.2mm drum, 3000rpm) ---\n');
fprintf('Shaft: %.0f W (cut %.0f + windage %.0f), torque %.1f Nm\n', Pn, Es*W*v, M.windage_ref_W, Tn);
fprintf('Electrical in: ~%.0f W\n', Pe);
motors = {m12 m30 m45};
for k = 1:numel(motors)
    m = motors{k};
    cont = m.rated_power_W*m.cont_factor;
    if cont > Pe*1.2, flag = 'OK'; else, flag = 'TIGHT/OVER'; end
    fprintf('  %s: cont~%.0f W -> margin %.0f%% %s\n', m.name, cont, ...
        (cont-Pe)/Pe*100, flag);
end

%% Plots
figure('Name','Light-grass rotor sizing');
Rcut76 = 0.0762/2 + M.pin_standoff_m + bS.pivot_to_tip_m;
tipS = rpms*2*pi/60*Rcut76;
subplot(3,1,1); plot(rpms, tipS, 'o-','LineWidth',1.5); grid on;
yline(30,'r--','30 m/s min'); yline(40,'r--','40 m/s'); 
xlabel('Rotor rpm'); ylabel('Tip speed m/s'); title('Tip speed (straight, 76.2mm drum)');
subplot(3,1,2);
PwS = M.windage_ref_W*(rpms/M.windage_ref_rpm).^3;
plot(rpms, Es*W*v + PwS, 'o-','LineWidth',1.5); grid on;
yline(m30.rated_power_W*m30.cont_factor,'g--','3kW cont');
yline(m45.rated_power_W*m45.cont_factor,'m--','4.5kW cont');
xlabel('Rotor rpm'); ylabel('Shaft power W'); title('Shaft power vs rpm (light grass)');
subplot(3,1,3);
omS = rpms*2*pi/60;
FcS = bS.mass_kg*omS.^2*(0.0762/2 + M.pin_standoff_m + bS.pivot_to_cg_m);
plot(rpms, FcS/1000, 'o-','LineWidth',1.5); grid on;
xlabel('Rotor rpm'); ylabel('Centrifugal kN / blade'); title('Pin load per blade (straight)');
