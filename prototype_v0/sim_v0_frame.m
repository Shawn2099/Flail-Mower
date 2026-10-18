%% sim_v0_frame.m
% PROTOTYPE V0 - layout sheet: geometry, mass, tank turn, stability, ground
% pressure, tube check, turning envelope. Fixed free-rotating front wheels
% (no casters) -> skid steer that pivots about its own centre.
% Mass scales with size (frame ~ perimeter, lid ~ deck area), so shrinking the
% machine ALSO lightens it and eases the tank turn.
% Base MATLAB only. Run from anywhere (self-locating).
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));
addpath(fullfile(thisdir,'specs'));

hm = motor_hub_6p5in_350W();
g  = 9.81; fails = 0;

%% ---------------- CHOSEN LAYOUT (mm) ----------------
L_wb    = 0.260;   % wheelbase: front axle to rear axle (NIMBLE)
W_track = 0.420;   % track: wheel centre to wheel centre (NIMBLE)
D_wheel = hm.tyre_OD_mm/1000;   % 0.170 - all 4 wheels SAME OD so the deck sits level
R       = D_wheel/2;
W_wheel = 0.045;   % tyre width [EST]
rail_h  = 0.025;   % SHS 25x25 rail height
rail_t  = 0.0016;  % 1.6 mm wall
rail_z0 = 0.104;   % frame tube UNDERSIDE above ground - the frame is lifted
                   % clear of the hub motors' O16 x 57 axle stubs, their nuts
                   % (27.8 across corners) and their washers (O30). 104 leaves
                   % 4 mm under the washer; see cad/build_v0_frame.py.
deck_h  = 0.0175;  % lid standoff above the rail top (the 4 deck posts)

%% ---------------- MASS MODEL (scales with size) ----------------
% Calibrated on the 300 x 550 reference build: frame 4.0 kg (SHS perimeter),
% lid 3.2 kg at 1.5 mm. The deck is now 1.6 mm (sim_v0_structure.m Q2), so
% k_lid carries the 1.6/1.5 thickness ratio. The deck spans BETWEEN the wheels:
% (L+90) x (B-65). See Q1 - the wheels poke above the deck, so the lid cannot
% run over them. 65 = tyre width 45 + 2 x 10 mm running clearance to the tyre.
% m_misc is the balancing allowance: the k_frame / k_lid terms above are a coarse
% scaling model that also carries the brackets, carrier, guard and fasteners, so
% m_misc is set to land the total on the CAD's MEASURED mass. After the MfD pass
% (4 identical corner brackets, no notched axle, solid tapped deck posts, frame
% lifted clear of the hub axles) cad/freecad_mass_check.py measures 5.64 kg of
% fabricated steel and 20.53 kg all-up, so m_misc drops 0.70 -> 0.30 kg.
% m_handle is 2.2 kg, not 1.5: 1.58 m of 25x25x1.6 legs plus a brace is 2.2 kg
% of tube before grips and throttles. The old allowance was under-counted.
k_frame   = 4.0/1700;                  % kg per mm of frame perimeter (2*(L+B))
deck_w_of = @(Bm) Bm - 65;             % deck stays inboard of the wheels
deck_l_of = @(Lm) Lm + 90;
k_lid     = 3.2/((300+90)*(550-65))*(1.6/1.5);   % kg per mm2 of deck area
m_fixed   = 4.6 + 3.0 + 2.5 + 1.5 + 1.0 + 2.2 + 0.30;  % hubs fronts batt cutter ctrl handle misc
mass_of   = @(Lm,Bm) m_fixed + k_frame*2*(Lm+Bm) + k_lid*deck_l_of(Lm)*deck_w_of(Bm);

%% ---------------- Q1 FOOTPRINT ----------------
L_over = L_wb + D_wheel;                 % over tyres, no overhang
W_over = W_track + W_wheel;
H_deck = rail_z0 + rail_h + deck_h;      % ground -> lid top (0.1465 m)
fprintf('\n============================================================\n');
fprintf(' PROTOTYPE V0 - RECOMMENDED LAYOUT (SMALL + NIMBLE)\n');
fprintf('============================================================\n');
fprintf('\nQ1 FOOTPRINT (mm):\n');
fprintf('  wheelbase %.0f | track %.0f | wheel OD %.0f (x4, all same)\n', L_wb*1000, W_track*1000, D_wheel*1000);
fprintf('  over tyres: %.0f L x %.0f W | deck height ~%.0f (+handle to ~900)\n', L_over*1000, W_over*1000, H_deck*1000);
fprintf('  deck lid  : %.0f L x %.0f W mm, sitting BETWEEN the wheels.\n', deck_l_of(L_wb*1000), deck_w_of(W_track*1000));
fprintf('              Wheels are 170 OD (top ~170 mm) so they poke ~%.0f mm above the %.0f mm deck.\n', ...
    D_wheel*1000 - H_deck*1000, H_deck*1000);
fprintf('              -> the wheels stay EXPOSED at the 4 corners (or notch a wider deck).\n');

%% ---------------- Q2 MASS ROLLUP ----------------
m_hub   = 2*hm.mass_kg;
m_front = 2*1.5;
m_frame = k_frame*2*(L_wb*1000 + W_track*1000);
m_lid   = k_lid*deck_l_of(L_wb*1000)*deck_w_of(W_track*1000);
m_batt  = 2.5; m_cut = 1.5; m_ctrl = 1.0; m_handle = 2.2; m_misc = 0.30;
m_total = m_hub+m_front+m_frame+m_lid+m_batt+m_cut+m_ctrl+m_handle+m_misc;
fprintf('\nQ2 MASS: hubs %.1f + fronts %.1f + frame %.1f + lid %.1f + batt %.1f\n', m_hub,m_front,m_frame,m_lid,m_batt);
fprintf('         + cutter %.1f + ctrl %.1f + handle %.1f + misc %.1f = %.1f kg (design %.0f)\n', ...
    m_cut,m_ctrl,m_handle,m_misc,m_total,ceil(m_total));
m_design = ceil(m_total);

%% ---------------- Q3 TANK TURN (fixed fronts scrub) ----------------
mu_side = 0.60;
b = W_track/2;
M_scrub = mu_side*m_design*g*(L_wb/2);
T_pivot = M_scrub/(2*b)*R;
fprintf('\nQ3 TANK TURN (%.0f kg design, mu %.2f, L_wb %.0f, track %.0f):\n', m_design, mu_side, L_wb*1000, W_track*1000);
fprintf('  scrub moment %.1f Nm -> %.2f Nm/wheel (cont %.2f / peak %.2f)\n', ...
    M_scrub, T_pivot, hm.T_cont_Nm, hm.T_peak_Nm);
if T_pivot <= hm.T_cont_Nm
    fprintf('  -> PASS: pivot within continuous torque (no current-limit needed).\n');
elseif T_pivot <= hm.T_peak_Nm
    fails=fails+1; fprintf('  -> MARGINAL: brief current-limited pivots only.\n');
else
    fails=fails+1; fprintf('  -> FAIL: too much scrub torque.\n');
end

%% ---------------- Q4 STABILITY (tip angles) ----------------
% cg_h/cg_off are the CAD mass model's numbers (cad/freecad_mass_check.py):
% 0.155 m high, 0.046 m BEHIND the axle midpoint - the hub motors (2.3 kg each
% at the rear) and the 2.2 kg handle put the CG back there, so the REAR tip
% angle is the worst one. The MfD pass deleted the 1.04 kg front axle and put
% the front wheels on short stubs, so cg_off moved 43 -> 46 mm back; lifting
% the frame onto the raised rails then carried the tubes 19 mm up and the CG
% with them (153 -> 155 mm).
% The earlier hand estimate was 160 / 37 mm.
cg_h   = 0.155;   % m CG height above ground (CAD says 0.155)
cg_off = 0.046;   % m CG behind the axle midpoint (CAD says 0.046, rear-biased)
tip_lat  = atand((W_track/2)/cg_h);
tip_fwd  = atand((L_wb/2 + cg_off)/cg_h);
tip_back = atand((L_wb/2 - cg_off)/cg_h);
tip_long = min(tip_fwd, tip_back);
fprintf('\nQ4 STABILITY (CG height %.0f mm, %.0f mm BEHIND centre):\n', cg_h*1000, cg_off*1000);
fprintf('  tip angle lateral %.0f deg | longitudinal fwd %.0f / rear %.0f deg\n', ...
    tip_lat, tip_fwd, tip_back);
fprintf('  worst case is REARWARD at %.0f deg (static; working grade is 5 deg)\n', tip_long);
if min(tip_lat,tip_long) >= 25
    fprintf('  -> PASS: stable on the working grade (5 deg) with margin.\n');
    fprintf('     Rear margin is the thin one - move the battery forward to even it up.\n');
else
    fails=fails+1; fprintf('  -> FAIL: raise track/length, move mass forward, or lower CG.\n');
end

%% ---------------- Q5 GROUND PRESSURE ----------------
% Contact patch width, not the tyre section width (spec contact_w_mm).
A_w = hm.contact_w_mm/1000*0.05;
gp  = m_design*g/(4*A_w);
fprintf('\nQ5 GROUND PRESSURE: %.1f kPa (4 wheels, %.0fx50 mm patch) - turf-safe <50 kPa\n', gp/1000, hm.contact_w_mm);

%% ---------------- Q6 TUBE CHECK ----------------
P = m_design*g/2; L_span = W_track;
M = P*L_span/4;
I = (rail_h^4 - (rail_h-2*rail_t)^4)/12;
Wsec = I/(rail_h/2);
sig = M/Wsec; allow = 165e6;
fprintf('\nQ6 TUBE (SHS %.0fx%.0fx%.1f midspan cross member):\n', rail_h*1000, rail_h*1000, rail_t*1000);
fprintf('  M %.1f Nm, Z %.0f mm3 -> sig %.1f MPa vs allow %.0f -> SF %.0f\n', M, Wsec*1e9, sig/1e6, allow/1e6, allow/sig);
if sig < allow
    fprintf('  -> PASS: 25x25x1.6 is ample.\n');
else
    fails=fails+1; fprintf('  -> FAIL: upsize the tube.\n');
end

%% ---------------- Q7 TURNING ENVELOPE ----------------
R_corner = sqrt((L_wb/2)^2 + (W_track/2)^2);
R_sweep  = R_corner + R;
fprintf('\nQ7 TURNING ENVELOPE (skid steer pivots about its own centre):\n');
fprintf('  corner radius %.0f mm -> swept circle ~%.0f mm dia (needs ~%.1f m clear to spin)\n', ...
    R_corner*1000, 2*R_sweep*1000, 2*R_sweep);
fprintf('  This is the tightest turn a 4-wheel machine can make (zero radius at the centre).\n');

%% ---------------- Q8 SIZE / MASS OPTIONS ----------------
fprintf('\nQ8 SIZE OPTIONS (tank turn vs cont %.2f / peak %.2f Nm):\n', ...
    hm.T_cont_Nm, hm.T_peak_Nm);
fprintf('  mass scales with size and is the MODELLED mass, so the chosen row lands a\n');
fprintf('  little under Q3 (which carries the 21 kg design budget, not 20.5).\n');
fprintf('  Lwb  track |  footprint LxW  |  mass | T_pivot | verdict\n');
opts = [300 550; 280 440; 260 420; 250 400; 240 380];
for k = 1:size(opts,1)
    Ls = opts(k,1); Bs = opts(k,2);
    m  = mass_of(Ls,Bs);
    Tp = mu_side*m*g*(Ls/1000)*R/(2*(Bs/1000));
    Lf = Ls+D_wheel*1000; Wf = Bs+W_wheel*1000;
    if Tp <= hm.T_cont_Nm
        v = 'PASS (continuous)';
    elseif Tp <= hm.T_peak_Nm
        v = 'ok (brief pivot)';
    else
        v = 'TOO HEAVY';
    end
    mark = '';
    if abs(Ls-L_wb*1000)<1e-9 && abs(Bs-W_track*1000)<1e-9
        mark = '  <== chosen';
    end
    fprintf('  %3.0f  %3.0f  |  %4.0f x %4.0f  | %5.1f |  %5.2f  | %s%s\n', ...
        Ls,Bs,Lf,Wf,m,Tp,v,mark);
end

%% ---------------- LAYOUT SHEET ----------------
fprintf('\n============================================================\n');
fprintf(' FINAL SIZE (v0) - FROZEN (small + nimble)\n');
fprintf('============================================================\n');
fprintf(' Wheels    : 6.5in airless OD 170 mm, FOUR the same (rear = hub motors)\n');
fprintf(' Wheelbase : %.0f mm (front axle to rear axle)\n', L_wb*1000);
fprintf(' Track     : %.0f mm (wheel centre to centre)\n', W_track*1000);
fprintf(' Footprint : ~%.0f L x ~%.0f W mm over tyres\n', L_over*1000, W_over*1000);
fprintf(' Frame     : MS square tube %.0fx%.0fx%.1f mm\n', rail_h*1000, rail_h*1000, rail_t*1000);
fprintf(' Deck lid  : 1.6 mm MS/CRCA sheet (16 gauge, India stock), %.0f L x %.0f W mm between the wheels, ~%.0f mm above rails\n', ...
    deck_l_of(L_wb*1000), deck_w_of(W_track*1000), deck_h*1000);
fprintf(' Cutter    : 775 + 200 mm head at frame centre, cut height 25-60 mm (adjustable)\n');
fprintf(' Deck top  : ~%.0f mm | handle to ~900 mm | mass ~%.0f kg (design %.0f)\n', H_deck*1000, m_total, m_design);
if fails==0
    fprintf(' RESULT    : all gates PASS -> this size is buildable as drawn.\n');
else
    fprintf(' RESULT    : %d gate(s) need attention.\n', fails);
end
fprintf('============================================================\n');
