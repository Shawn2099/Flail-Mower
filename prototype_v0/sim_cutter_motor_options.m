%% sim_cutter_motor_options.m
% UPGRADING THE CUTTER MOTOR - what the job needs, and how each motor class fits.
% Baseline = standard 775 (see specs/motor_775_DC.m). Head = printed D50 hub
% (specs/nylon_line_1p6.m). Base MATLAB only. Self-locating.
%
% Part A - DUTY REQUIREMENT: shaft power + torque the head demands, vs swath,
%          grass density and feed rate.
% Part B - SPEED SIZING: what motor Kv gives a good cutter speed on the 36 V bus.
% Part C - HEADROOM WALL: where aero drag makes a wide head uneconomic.
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath')); addpath(fullfile(thisdir,'specs'));

ln = nylon_line_1p6();
r0 = ln.r0_m; d = ln.d_line_m; nL = ln.n_lines;
hm = motor_775_DC();

rho_air = 1.225; Cd = 1.1;
rpm_op  = 6500;  om = rpm_op*2*pi/60;
tip_min = 50;                       % m/s for a clean cut (repo convention)
V_bus   = 36;                       % drive bus (10S Li-ion) - nominal

fprintf('\n============================================================\n');
fprintf(' CUTTER MOTOR UPGRADE - REQUIREMENT + OPTIONS\n');
fprintf('============================================================\n');

%% ---------------- PART A: DUTY REQUIREMENT ----------------
fprintf('\nA. DUTY REQUIREMENT (at %d rpm, hub D50, %d x 1.6 mm lines)\n', rpm_op, nL);
fprintf('   Motor must hold this speed under load without stalling.\n\n');
fprintf('  swath | Rtip | line | min rpm |  P_shaft (W) @6500 rpm      | T (Nm)\n');
fprintf('   (mm) | (mm) | (mm) | (clean) | light | heavy | light-2 |  heavy\n');
swaths = [200 250 300 350 400];
for W_mm = swaths
    R  = (W_mm/1000)/2; W = W_mm/1000;
    Kg = rho_air*Cd*d*(R^4 - r0^4)/8;
    pa = nL*Kg*om^3;
    % light  = Es 800, v 0.15 (design case); heavy = Es 1500, v 0.25
    p_light  = 800*W*0.15 + pa;
    p_heavy  = 1500*W*0.25 + pa;
    p_light2 = 800*W*0.30 + pa;         % light grass, faster push
    rpm_min  = tip_min/R*60/(2*pi);
    fprintf('  %4.0f  | %4.0f | %4.0f | %6.0f  | %5.0f | %5.0f | %6.0f  | %5.2f\n', ...
        W_mm, R*1000, (R-r0)*1000, rpm_min, p_light, p_heavy, p_light2, p_heavy/om);
end
fprintf('\n  775 for reference: 80 W cont @12V / 150 W cont @24V, 0.72 Nm stall.\n');
fprintf('  Aero drag grows as R^4 - it, not cut load, is what kills wide heads.\n');

%% ---------------- PART B: SPEED SIZING ON 36 V ----------------
fprintf('\nB. SPEED SIZING ON THE %d V BUS (rpm_noload = Kv*V; ~20%% droop loaded)\n', V_bus);
fprintf('  Kv(rpm/V) | no-load rpm | loaded rpm | clean cut? (>=4775 rpm at 200 mm)\n');
for Kv = [140 160 180 200 220 250 300]
    n0 = Kv*V_bus; nl = 0.8*n0;
    if nl >= 4775, v_='yes'; else, v_='too slow'; end
    fprintf('    %4.0f    |  %7.0f   |  %7.0f   | %s\n', Kv, n0, nl, v_);
end
fprintf('  -> target Kv ~180-220 rpm/V for a ~6500 rpm head on 36 V (no step-down).\n');

%% ---------------- PART C: WHAT IT UNLOCKS ----------------
fprintf('\nC. KINDS OF UPGRADE vs THE DUTY ABOVE\n');
fprintf('  1. Bigger BRUSHED (895/997, 24 V): ~1.5-2x the 775. Same limits remain\n');
fprintf('     (brush wear, 1-3 min duty, poor speed holding), and still needs the\n');
fprintf('     36->24 V step-down. Cheapest, smallest gain.\n');
fprintf('  2. BLDC INRUNNER (~200 Kv, 36 V) + ESC/VESC: 5-10x the 775 power,\n');
fprintf('     runs straight off the 36 V bus (NO step-down), sensored = clean start,\n');
fprintf('     ESC gives throttle + current limit + rpm telemetry. Best overall fit.\n');
fprintf('  3. BLDC OUTRUNNER (6374 / 5065 ~190-270 Kv, 36 V): same story, more torque,\n');
fprintf('     hub bolts to the rotating bell - but the bell spins, so guarding and\n');
fprintf('     the mount need care.\n');
fprintf('  4. CORDLESS-TRIMMER BLDC + OEM board (36 V tool motor): purpose-built for\n');
fprintf('     grass, sealed, but proprietary mount and little spec data.\n');
fprintf('  5. THIRD HUB MOTOR + belt: reuses your drive part, but it is a ~800 rpm\n');
fprintf('     motor - needs ~8:1 belt up. Heavy and complex; not recommended.\n');

fprintf('\n  MECHANICAL CEILING: on the FROZEN 260 x 420 layout the line tips clear\n');
fprintf('  the wheels out to ~162 mm radius (corner 247 - wheel 85) -> swath up to\n');
fprintf('  ~325 mm is physically possible. The MOTOR is the limit, not the chassis.\n');
fprintf('  The guard must grow with the swath either way.\n');
fprintf('============================================================\n');
