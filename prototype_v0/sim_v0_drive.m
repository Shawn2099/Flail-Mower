%% sim_v0_drive.m
% PROTOTYPE V0 - traction drive sizing for 2x 6.5in 36V 350W hub motors (tank turn).
% Q1 SPEED BAND  - wheel rpm at mow speed vs the 26 km/h top end (throttle cap).
% Q2 TRACTION    - rolling + grade torque per wheel vs hub capability.
% Q3 TANK TURN   - pivot scrub torque (the real stress case) vs hub peak torque.
% Q4 BATTERY     - drive + cutter current, pack size, runtime.
% Q5 GROUND PRESSURE.
% Base MATLAB only. Run from anywhere (self-locating).
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));
addpath(fullfile(thisdir,'specs'));

hm = motor_hub_6p5in_350W();   % per-motor hub specs
g  = 9.81;
fails = 0;

fprintf('\n============================================================\n');
fprintf(' PROTOTYPE V0 - DRIVE SIZING (2x 6.5in hub motors, tank turn)\n');
fprintf('============================================================\n');

%% ---------------- INPUTS (FROZEN v0: 260 x 420, design mass 21 kg) -------
% Geometry + mass are the frozen v0 values from sim_v0_frame.m; if either
% changes, change it HERE too or the two sims disagree on the tank turn.
m_machine = 21;        % kg all-up (frozen design mass, sim_v0_frame.m Q2)
Crr       = 0.08;      % rolling resistance, small wheels on grass
grade_deg = 5;         % work grade
v_mow     = 0.35;      % m/s walkable mow feed (cutter band 0.2-0.6)
v_slow    = 0.15;      % m/s the cutter was actually sized at (POC sim)
v_cap     = 0.60;      % m/s we impose as the machine's max (walk-behind)
mu_side   = 0.60;      % lateral scrub coefficient, rubber on grass
L_wb      = 0.26;      % m wheelbase  (FROZEN)
W_track   = 0.42;      % m track, wheel centre to wheel centre (FROZEN)
cutter_Pelec = 58;     % W at the 775 cutter (from sim_775_trimmer_POC @6500 rpm)

R = hm.wheel_R_m; C = hm.circ_m;
fprintf('\nWheel: OD %d mm, R %.3f m, circumference %.3f m, mass %.2f kg ea\n', ...
    hm.tyre_OD_mm, R, C, hm.mass_kg);

%% ---------------- Q1 SPEED BAND ----------------
rpm_for = @(v) v/C*60;
v_topspeed = hm.max_speed_kmh/3.6;
fprintf('\nQ1 SPEED BAND (no gearbox - throttle only):\n');
fprintf('  mow feed %.2f m/s -> %.1f rpm ; band 0.2-0.6 m/s -> %.0f-%.0f rpm\n', ...
    v_mow, rpm_for(v_mow), rpm_for(0.2), rpm_for(0.6));
fprintf('  motor top end %.1f km/h = %.1f m/s = %.0f rpm  (%.0fx the mow feed)\n', ...
    hm.max_speed_kmh, v_topspeed, rpm_for(v_topspeed), v_topspeed/v_mow);
if rpm_for(v_cap)/rpm_for(v_topspeed) < 0.10
    fprintf('  -> PASS: mow speed is <10%% of top speed; the drive must be CURRENT-LIMITED\n');
    fprintf('     (torque mode), not voltage-throttled. A speed-based throttle will be twitchy.\n');
else
    fails = fails + 1; fprintf('  -> CHECK throttle resolution.\n');
end

%% ---------------- Q2 TRACTION (rolling + grade) ----------------
F_roll  = Crr*m_machine*g;
F_grade = m_machine*g*sind(grade_deg);
F_tot   = F_roll + F_grade;
T_wheel = F_tot/2*R;                 % per hub, 2 driven wheels
fprintf('\nQ2 TRACTION (%.0f kg, %.0f deg, Crr %.2f):\n', m_machine, grade_deg, Crr);
fprintf('  F_roll %.1f N + F_grade %.1f N = F_tot %.1f N ; per-wheel torque %.2f Nm\n', ...
    F_roll, F_grade, F_tot, T_wheel);
if T_wheel <= hm.T_cont_Nm
    fprintf('  -> PASS: %.2f <= T_cont %.2f Nm (flat/grade cruising is trivial)\n', T_wheel, hm.T_cont_Nm);
elseif T_wheel <= hm.T_peak_Nm
    fprintf('  -> MARGINAL: needs peak torque %.2f <= %.2f Nm\n', T_wheel, hm.T_peak_Nm);
else
    fails = fails + 1; fprintf('  -> FAIL: %.2f > T_peak %.2f Nm\n', T_wheel, hm.T_peak_Nm);
end

%% ---------------- Q3 TANK TURN (pivot scrub) ----------------
% Resisting moment ~ mu_side * W * (L_wb/2) about the centre (front wheels scrub
% sideways). Each hub thrusts F at half-track b -> moment 2*F*b.
b = W_track/2;
M_scrub = mu_side*m_machine*g*(L_wb/2);
F_wheel = M_scrub/(2*b);
T_pivot = F_wheel*R;
fprintf('\nQ3 TANK TURN (pivot in place, front wheels fixed/idle):\n');
fprintf('  scrub moment %.1f Nm ; thrust %.1f N/wheel ; torque %.2f Nm/wheel\n', ...
    M_scrub, F_wheel, T_pivot);
if T_pivot <= hm.T_cont_Nm
    fprintf('  -> PASS: pivot within continuous torque.\n');
elseif T_pivot <= hm.T_peak_Nm
    fprintf('  -> MARGINAL: pivot needs peak torque (%.2f <= %.2f Nm) - short bursts only.\n', ...
        T_pivot, hm.T_peak_Nm);
else
    fails = fails + 1; fprintf('  -> FAIL: pivot needs %.2f > T_peak %.2f Nm. Reduce mu_side\n', T_pivot, hm.T_peak_Nm);
    fprintf('     (rounder/harder front wheels) or add casters / shorten wheelbase.\n');
end
% Caster comparison (only rear scrubs against pivot -> use half the resisting width)
M_cast = mu_side*m_machine*g*(L_wb/2)*0.5;
fprintf('  casters instead of fixed fronts: torque %.2f Nm/wheel (halves the scrub)\n', M_cast/(2*b)*R);

%% ---------------- Q4 BATTERY ----------------
P_drive = F_tot*v_mow/hm.eff;              % elec, both motors
P_total = P_drive + cutter_Pelec;          % + 775 cutter
I_drive = P_drive/hm.V_nom;
I_tot   = P_total/hm.V_nom;
% 10S Li-ion ~36 V nominal; a 10 Ah pack = 360 Wh
Wh_pack = 36*10; usable = 0.8;
fprintf('\nQ4 BATTERY (36 V bus):\n');
fprintf('  at mow: drive %.1f W (%.1f A) + cutter %.0f W = %.1f W (%.1f A)\n', ...
    P_drive, I_drive, cutter_Pelec, P_total, I_tot);
fprintf('  36V 10Ah pack (%.0f Wh, %.0f%% usable) -> %.1f h mow / ~%.0f m2 per charge\n', ...
    Wh_pack, usable*100, Wh_pack*usable/P_total, Wh_pack*usable/P_total*3600*v_mow*0.2);
fprintf('  at the cutter-sizing feed (%.2f m/s) it is ~%.0f m2 per charge\n', ...
    v_slow, Wh_pack*usable/P_total*3600*v_slow*0.2);
fprintf('  -> feed the 775 cutter from 36 V via a step-down to 24 V (one battery).\n');

%% ---------------- Q5 GROUND PRESSURE ----------------
% Use the CONTACT patch (spec contact_w_mm), not the tyre section width.
A_wheel = (hm.contact_w_mm/1000)*(0.05);   % contact patch ~ width x 50 mm [EST]
gp = m_machine*g/(4*A_wheel);
fprintf('\nQ5 GROUND PRESSURE: %.1f kPa (4 wheels, patch %.0fx50 mm) - turf limit ~<50 kPa\n', ...
    gp/1000, hm.contact_w_mm);

%% ---------------- VERDICT ----------------
fprintf('\n============================================================\n');
if fails==0
    fprintf(' VERDICT: hub drive is FEASIBLE. Dominant issue = low-speed control, not power.\n');
else
    fprintf(' VERDICT: %d gate(s) FAILED - see above (tank turn is the critical case).\n', fails);
end
fprintf(' Drive needs a DUAL controller (one per hub) wired for tank turn;\n');
fprintf(' current-limit to protect the 350 W motors; measure Kv + phase R to lock [EST] values.\n');
fprintf('============================================================\n');
