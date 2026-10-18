%% sim_775_swath.m
% WHY IS THE CUTTER 200 mm? Trade study: swath diameter vs the 775 power budget.
% Swath D = 2*(hub_radius + line_length). Working width = swath.
% Drag grows ~ (R^4 - r0^4), so swath is limited by motor power, not by mechanics.
% Base MATLAB only. Run from anywhere (self-locating).
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath')); addpath(fullfile(thisdir,'specs'));

ln = nylon_line_1p6();
d = ln.d_line_m; rho = ln.rho_kg_m3; nL = ln.n_lines; r0 = ln.r0_m;

rho_air = 1.225; Cd = 1.1;
rpm = 6500; om = rpm*2*pi/60;
Es = 800; v = 0.15;          % light grass, slow mow feed

fprintf('\n=== SWATH TRADE (hub %.0f mm dia, %d x 1.6 mm lines, %d rpm, Es=%d, v=%.2f m/s) ===\n', ...
    2*r0*1000, nL, rpm, Es, v);
fprintf('  line  swath |  Vtip | Pcut | Paero | Pshaft | vs 12V(80W) / 24V(150W)\n');
for Lmm = [50 60 70 75 80 90 100 110 130]
    L = Lmm/1000; R = r0 + L; W = 2*R;
    Kg = rho_air*Cd*d*(R^4 - r0^4)/8;
    pa = nL*Kg*om^3;
    pc = Es*W*v;
    ps = pc + pa;
    vt = om*R;
    if ps <= 80
        a = 'OK  ';
    elseif ps <= 150
        a = 'DUTY';
    else
        a = 'OVER';
    end
    if ps <= 150
        b = 'OK';
    else
        b = 'OVER';
    end
    mark = '';
    if abs(W*1000 - 200) < 1e-9
        mark = '   <== chosen (D50 hub + 75 mm line)';
    end
    fprintf('  %4d  %4.0f  | %5.0f | %4.0f | %5.1f | %6.1f | %-5s / %-4s%s\n', ...
        Lmm, W*1000, vt, pc, pa, ps, a, b, mark);
end

fprintf('\n  Tip speed at 6500 rpm: 200 mm -> %.0f m/s, 280 mm -> %.0f m/s (clean cut needs >=50)\n', ...
    6500*2*pi/60*(r0+0.075), 6500*2*pi/60*(r0+0.110));
fprintf('  Chosen head = our printed D50 hub: swath = 2 x (25 mm hub radius + line per side).\n');
fprintf('   - the line length is the free input; swath = 50 mm + 2 x line.\n');
fprintf('   - the ~15-20 %% power per +20 mm of line is the real constraint.\n');
fprintf('  Wider head -> more aero drag + more cut power -> the 775 must run 18-24 V or in duty.\n');
