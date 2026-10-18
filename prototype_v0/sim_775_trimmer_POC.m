%% sim_775_trimmer_POC.m
% POC DISPLAY UNIT - 775 DC motor + 1.6 mm Blue Round Nylon trimmer line
% Question: can it cut LIGHT maintained grass?
% Base MATLAB only. Run from anywhere (self-locating): prototype_v0/sim_775_trimmer_POC.m
%
% Method (conservative, physics-based):
%   Q1 TIP SPEED  - Vtip = omega*R  vs 35 m/s blunt floor and 50 m/s nylon-clean floor
%   Q2 LINE STRENGTH - centrifugal stress vs PA6 UTS with margin
%   Q3 POWER/TORQUE - Pcut (Es*W*v) + Paero (rotating-cylinder drag integral)
%                     vs 775 continuous / peak shaft capability at 12V and 24V
%   Q4 OPERATING POINT - intersection of motor torque-speed line with fan-type load
%   Q5 THERMAL/BATTERY - current, duty, runtime estimate for display demo
%
% References used:
%   - repo spec: common/specs/grass_light_maintained.m  Es=800 J/m2 nom [500 1500]
%   - 775 datasheets: 12V n0~6000 rpm / 24V n0~8300-12000 rpm,
%     stall 0.6-0.72 Nm, rated shaft ~80 W @12V / ~150 W @24V, eta ~0.6-0.68
%     (RobotShop RS775SM-4445-F, Handsontec 775-Motor.pdf, generic 775 12-24V)
%   - Commercial 1.6 mm-line trimmers: 250-500 W, 230-300 mm swath, 7000-9000 rpm
%     (Bosch 280 W/230 mm, Jadever 20V 8200 rpm/300 mm/1.6 mm)
%   - Nylon PA6: rho~1140 kg/m3, UTS ~70-80 MPa virgin (~40 MPa aged/wet/knotted)
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));
addpath(fullfile(thisdir,'specs'));

fprintf('\n============================================================\n');
fprintf(' 775 + 1.6 mm NYLON TRIMMER POC - GRASS CUT FEASIBILITY\n');
fprintf('============================================================\n');

%% ---------- 1. INPUTS (edit these for your head) ----------
% Trimmer line + head geometry (canonical: specs/nylon_line_1p6.m)
ln = nylon_line_1p6();
d_line   = ln.d_line_m;
rho_nylon= ln.rho_kg_m3;
UTS_new  = ln.UTS_new_Pa;
UTS_used = ln.UTS_design_Pa;
A_line   = ln.A_line_m2;
m_per_m  = ln.m_per_m_kg;
D_hub    = ln.D_hub_m;
r0       = ln.r0_m;
L_line   = ln.L_line_m;
R_tip    = ln.R_tip_m;
D_cut    = ln.D_cut_m;
n_lines  = ln.n_lines;

% Grass + job (light maintained grass, clean ground, from grass_light_maintained.m)
Es_nom = 800;              % J/m2, nominal
Es_rng = [500 1500];       % J/m2, sensitivity range
W_swath= D_cut;            % m, effective working width = swath diameter
v_fwd  = 0.15;             % m/s, slow hand-push/display feed (range 0.10-0.30 below)
tip_need_blunt = 35;       % m/s, blunt-edge floor (repo spec)
tip_need_nylon = 50;       % m/s, nylon-line clean-cut floor (commercial practice)

% Air
rho_air = 1.225; Cd_cyl = 1.1; % cylinder in cross-flow, Re~1e3-1e4

% 775 motor capability (canonical: specs/motor_775_DC.m)
mot = motor_775_DC();

fprintf('\n--- INPUTS ---\n');
fprintf('Line: 1.6 mm round PA6, %.2f g/m, %d x %.0f mm exposed\n', m_per_m*1000, n_lines, L_line*1000);
fprintf('Head: hub %.0f mm -> Rtip %.0f mm -> swath D=%.0f mm\n', D_hub*1000, R_tip*1000, D_cut*1000);
fprintf('Grass: light maintained, Es=%d J/m2 [%.0f-%.0f], W=%.2f m, v=%.2f m/s\n', Es_nom, Es_rng(1), Es_rng(2), W_swath, v_fwd);

%% ---------- 2. Q1 TIP SPEED ----------
rpms = 2000:250:12000;
om   = rpms*2*pi/60;
Vtip = om*R_tip;
fprintf('\nQ1 TIP SPEED (Rtip=%.0f mm):\n', R_tip*1000);
for r = [4000 5000 6000 6500 8000 9000 11000]
    v_ = r*2*pi/60*R_tip;
    if v_>=tip_need_nylon, s='CLEAN (>=50)'; elseif v_>=tip_need_blunt, s='TEARS (>=35, ragged)'; else, s='FAIL (<35, folds grass)'; end
    fprintf('  %5d rpm -> Vtip %5.1f m/s  %s\n', r, v_, s);
end
% Minimum rpm for each threshold
rpm_35 = tip_need_blunt/R_tip*60/2/pi;
rpm_50 = tip_need_nylon/R_tip*60/2/pi;
fprintf('  Need >=%.0f rpm for 35 m/s, >=%.0f rpm for 50 m/s.\n', ceil(rpm_35), ceil(rpm_50));

%% ---------- 3. Q2 LINE STRESS (centrifugal) ----------
% T = rho*A*om^2*(R^2-r0^2)/2 ; sig = T/A = rho*om^2*(R^2-r0^2)/2
sig = rho_nylon*om.^2*(R_tip^2-r0^2)/2;
Tline = sig*A_line;
m_line_one = m_per_m*L_line;
fprintf('\nQ2 LINE TENSION/STRESS (per line, mass %.2f g):\n', m_line_one*1000);
for r = [5000 6500 9000 11000]
    o=r*2*pi/60; sg=rho_nylon*o^2*(R_tip^2-r0^2)/2; Tl=sg*A_line;
    fprintf('  %5d rpm -> T=%5.1f N, sig=%5.1f MPa (vs aged-allow ~%.0f MPa)\n', r, Tl, sg/1e6, UTS_used/1e6);
end
% Safety factor at 6500 and 9000 rpm vs aged strength
o65=6500*2*pi/60; s65=rho_nylon*o65^2*(R_tip^2-r0^2)/2;
o90=9000*2*pi/60; s90=rho_nylon*o90^2*(R_tip^2-r0^2)/2;
fprintf('  SF vs aged 40 MPa: %.1f @6500 rpm, %.1f @9000 rpm (want >=2.0)\n', UTS_used/s65, UTS_used/s90);
fprintf('  SF vs virgin 75 MPa: %.1f @6500, %.1f @9000\n', UTS_new/s65, UTS_new/s90);

%% ---------- 4. Q3 POWER MODEL ----------
% Pcut = Es*W*v  (forward-motion cutting energy)
% Paero_one = rho*Cd*d*om^3*(R^4-r0^4)/8 ; P_aero = n_lines * that
% Derivation: dF=1/2 rho Cd d (om r)^2 dr, dP=dF*om r, integrate r0..R.
Kgeo = rho_air*Cd_cyl*d_line*(R_tip^4-r0^4)/8; % P_one = Kgeo*om^3
Paero = n_lines*Kgeo*om.^3;
Pcut_nom = Es_nom*W_swath*v_fwd;
Pcut_lo  = Es_rng(1)*W_swath*v_fwd;
Pcut_hi  = Es_rng(2)*W_swath*v_fwd;
Pshaft_nom = Pcut_nom + Paero;
Pshaft_hi  = Pcut_hi + Paero;
Tload_nom  = Pshaft_nom./om; % Nm (add ~0.01 Nm hub friction below in table)

fprintf('\nQ3 POWER (W=%.2f m, v=%.2f m/s):\n', W_swath, v_fwd);
fprintf('  Pcut: %.1f W nominal (Es=800), [%.1f - %.1f] W for Es 500-1500\n', Pcut_nom, Pcut_lo, Pcut_hi);
fprintf('  rpm  | Paero(W) | Pshaft nom(W) | Pshaft heavy(W) | Tload nom(Nm)\n');
for r = [4000 5000 6000 6500 8000 9000 11000]
    o=r*2*pi/60; pa=n_lines*Kgeo*o^3;
    fprintf('  %5d | %7.1f  | %10.1f    | %11.1f     | %5.3f\n', r, pa, Pcut_nom+pa, Pcut_hi+pa, (Pcut_nom+pa)/o);
end

%% ---------- 5. Q4 MOTOR MATCH (operating point) ----------
fprintf('\nQ4 MOTOR MATCH (motor torque-speed line vs load):\n');
fprintf('  Motor assumed linear: T_avail = Tstall*(1 - rpm/n0). Load: T=(Pcut+Paero)/om.\n');
for m = 1:numel(mot)
    fprintf('\n  ** %s: n0=%d rpm, Tstall=%.2f Nm, Tcont=%.2f Nm, Pcont~%.0f W shaft **\n', ...
        mot(m).name, mot(m).n0, mot(m).Tstall, mot(m).Tcont, mot(m).Pcont);
    fprintf('  rpm  | Tavail | Tload-nom | Tload-heavy | Pshaft-nom | verdict\n');
    for r = [4000 5000 6000 6500 8000 9000]
        if r>=mot(m).n0, continue; end
        o=r*2*pi/60; pa=n_lines*Kgeo*o^3;
        Tl_n=(Pcut_nom+pa)/o; Tl_h=(Pcut_hi+pa)/o;
        Ta=mot(m).Tstall*(1-r/mot(m).n0);
        Ps_n=Pcut_nom+pa;
        if Tl_h<Ta && Ps_n<mot(m).Pcont, v_='OK (cont)';
        elseif Tl_n<Ta && Ps_n<mot(m).Ppeak, v_='MARGINAL (peak/duty)';
        else, v_='OVERLOAD (stall/rpm drop)';
        end
        fprintf('  %5d | %6.3f  | %7.3f    | %7.3f      | %7.1f     | %s\n', r, Ta, Tl_n, Tl_h, Ps_n, v_);
    end
    % Solve operating rpm: find rpm where Tavail(rpm)=Tload_nom(rpm)
    f = @(rr) mot(m).Tstall*(1-rr/mot(m).n0) - (Pcut_nom+n_lines*Kgeo*(rr*2*pi/60)^3)/(rr*2*pi/60);
    r_try = 1000:100:mot(m).n0-200;
    vals = arrayfun(f, r_try);
    idx = find(vals<0, 1, 'first'); % motor can no longer supply above crossing? actually stable point is highest rpm crossing
    % stable no-load droop: search from top down for first vals>0
    op = NaN;
    for k = numel(r_try):-1:1
        if vals(k)>0, op=r_try(k); break; end
    end
    if ~isnan(op)
        oo=op*2*pi/60; pa=n_lines*Kgeo*oo^3; ps=Pcut_nom+pa; vt=oo*R_tip;
        pe=ps/mot(m).eta; amps=pe/mot(m).V;
        fprintf('  -> predicted operating point (nominal grass): ~%d rpm, Vtip %.0f m/s, Pshaft %.0f W, Pelec %.0f W, I %.1f A @%dV\n', ...
            op, vt, ps, pe, amps, mot(m).V);
    else
        fprintf('  -> motor cannot hold speed even lightly loaded (check n0).\n');
    end
end

%% ---------- 6. Q5 CURRENT / BATTERY / DUTY ----------
fprintf('\nQ5 CURRENT + DUTY (display-unit guidance):\n');
for m = 1:numel(mot)
    o=6500*2*pi/60; pa=n_lines*Kgeo*o^3;
    ps_n=Pcut_nom+pa; ps_h=Pcut_hi+pa;
    for ps = [ps_n ps_h]
        pe=ps/mot(m).eta; amps=pe/mot(m).V;
        if ps<=mot(m).Pcont, d='continuous OK'; elseif ps<=mot(m).Ppeak, d='short-duty only (1-3 min + cool)'; else, d='OVERLOAD - will stall/burn'; end
        fprintf('  %s Pshaft %.0f W -> Pelec %.0f W -> %.1f A @%dV : %s\n', mot(m).name, ps, pe, amps, mot(m).V, d);
    end
end
% Runtime example: 12V 12Ah pack (144 Wh), 80% usable
Wh = 12*12*0.8;
o=6500*2*pi/60; ps=Pcut_nom+n_lines*Kgeo*o^3; pe=ps/mot(1).eta;
fprintf('  Example: 12V 12Ah pack (~%.0f Wh usable) at ~%.0f W elec -> ~%.1f h demo / ~%.0f m2 per charge (W=%.2f m, v=%.2f m/s)\n', ...
    Wh, pe, Wh/pe, (Wh/pe)*3600*W_swath*v_fwd, W_swath, v_fwd);

%% ---------- 7. SENSITIVITY: feed rate + line length ----------
fprintf('\nSENSITIVITY (shaft W at 6500 rpm, Rtip varied by line length):\n');
fprintf('  v(m/s) | Es=500 | Es=800 | Es=1500 || note\n');
o65=6500*2*pi/60;
for v_=[0.10 0.15 0.25 0.40]
    pa=n_lines*Kgeo*o65^3;
    fprintf('  %.2f   | %6.1f | %6.1f | %6.1f  || ', v_, Es_rng(1)*W_swath*v_+pa, Es_nom*W_swath*v_+pa, Es_rng(2)*W_swath*v_+pa);
    if Es_rng(2)*W_swath*v_+pa>150
        fprintf('heavy grass + fast push OVERLOADS 12V\n');
    elseif Es_nom*W_swath*v_+pa>80
        fprintf('nominal OK at 24V, duty-limited at 12V\n');
    else
        fprintf('OK\n');
    end
end
fprintf('\n  Line length effect (Paero ~ R^4!):\n');
for L=[50 70 90 110]*1e-3
    Rt=r0+L; Kg=rho_air*Cd_cyl*d_line*(Rt^4-r0^4)/8;
    pa2=n_lines*Kg*o65^3; vt2=o65*Rt;
    fprintf('  L=%3.0f mm (D=%3.0f mm): Paero=%5.1f W, Vtip=%4.0f m/s\n', L*1000, 2*Rt*1000, pa2, vt2);
end

%% ---------- 8. VERDICT ----------
% Recompute key numbers for verdict
o65=6500*2*pi/60; pa65=n_lines*Kgeo*o65^3; ps65=Pcut_nom+pa65; vt65=o65*R_tip;
sig65=rho_nylon*o65^2*(R_tip^2-r0^2)/2;
fprintf('\n============================================================\n');
fprintf(' VERDICT for POC DISPLAY UNIT (%.0f mm swath, %.0f mm line, 775 motor)\n', D_cut*1000, L_line*1000);
fprintf('============================================================\n');
fprintf(' At 6500 rpm: Vtip=%.0f m/s, Paero=%.0f W, Pcut=%.0f W, Pshaft=%.0f W, line %.1f MPa (SF %.1f vs aged)\n', ...
    vt65, pa65, Pcut_nom, ps65, sig65/1e6, UTS_used/sig65);
if vt65>=tip_need_nylon, q1='PASS - clean cut expected'; elseif vt65>=tip_need_blunt, q1='MARGINAL - will tear light grass, ragged finish'; else, q1='FAIL - too slow'; end
if UTS_used/sig65>=2.0, q2='PASS'; else, q2='MARGINAL - use fresh line, short length'; end
if ps65<=80, q3='PASS @12V continuous'; elseif ps65<=150, q3='PASS @24V continuous, DUTY-LIMITED @12V'; else, q3='FAIL - overload'; end
fprintf('  Q1 tip speed : %s\n  Q2 line     : %s\n  Q3 power     : %s\n', q1, q2, q3);
fprintf('\n>>> ANSWER: ');
if vt65>=tip_need_blunt && ps65<=150 && UTS_used/sig65>=1.5
    fprintf('YES - POSSIBLE for LIGHT maintained grass demo (short, dry, sparse lawn grass).\n');
else
    fprintf('NO - not with these settings (see limits below).\n');
end
fprintf(['  Conditions for YES: (1) keep swath ~200 mm (our D50 hub + 75 mm/side),\n' ...
    '  (2) run 6000-8000+ rpm (12V marginal, 18-24V comfortable),\n' ...
    '  (3) slow feed <=0.15-0.20 m/s, light grass only (Es<=800),\n' ...
    '  (4) fresh 1.6 mm round line, eye protection + guard + 1-3 min duty at 12V.\n']);
fprintf(['  It will NOT do: tall/dense/wet weeds, brush, woody stems, fast push,\n' ...
    '  long line (>90 mm/side), or continuous 12V trudging - expect rpm droop,\n' ...
    '  stalling, melted line tip, brushed-motor overheat.\n']);
fprintf('  Recommended POC wiring: 775 on 18V (or 24V w/ PWM), 20A fuse, ammeter,\n');
fprintf('  tachometer, perforated guard, printed D50 hub, trim line to 75 mm/side.\n');
fprintf('============================================================\n');

%% ---------- 9. PLOTS ----------
figure('Name','775+1.6mm POC - tip speed + power + motor match + stress');
subplot(2,2,1);
plot(rpms, Vtip, 'b-', 'LineWidth', 1.8); grid on; hold on;
yline(tip_need_blunt,'r--','35 m/s blunt floor');
yline(tip_need_nylon,'m--','50 m/s nylon-clean');
xline(rpm_35,'r:'); xline(rpm_50,'m:');
xlabel('rpm'); ylabel('tip speed m/s');
title(sprintf('Q1 tip speed (Rtip=%.0f mm)', R_tip*1000));
legend('Vtip','Location','southeast');

subplot(2,2,2);
plot(rpms, Pcut_nom+Paero, 'b-', 'LineWidth', 1.8); grid on; hold on;
plot(rpms, Pcut_hi+Paero, 'r--', 'LineWidth', 1.2);
yline(mot(1).Pcont,'g--','775@12V cont 80W');
yline(mot(3).Pcont,'m--','775@24V cont 150W');
xlabel('rpm'); ylabel('shaft power W');
title(sprintf('Q3 shaft power (W=%.2f m, v=%.2f m/s)', W_swath, v_fwd));
legend('nominal Es=800','heavy Es=1500','Location','northwest');

subplot(2,2,3); hold on; grid on;
cols = {'g','b','m'};
for m = 1:numel(mot)
    Tav = mot(m).Tstall*(1-rpms/mot(m).n0); Tav(rpms>=mot(m).n0)=NaN;
    plot(rpms, Tav, '-', 'LineWidth', 1.6, 'Color', cols{m}, 'DisplayName', char(mot(m).name));
end
plot(rpms, Tload_nom, 'k-', 'LineWidth', 1.8, 'DisplayName', 'load nominal');
plot(rpms, Pshaft_hi./om, 'k--', 'LineWidth', 1.1, 'DisplayName', 'load heavy');
xlabel('rpm'); ylabel('torque Nm'); title('Q4 motor vs load torque');
legend('Location','northeast');

subplot(2,2,4);
plot(rpms, sig/1e6, 'b-', 'LineWidth', 1.8); grid on; hold on;
yline(UTS_used/1e6,'r--','aged 40 MPa');
yline(UTS_new/1e6,'g--','virgin 75 MPa');
xlabel('rpm'); ylabel('line root stress MPa');
title('Q2 nylon line centrifugal stress');
