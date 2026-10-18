%% sim_v0_structure.m
% PROTOTYPE V0 - MATERIAL + THICKNESS SIZING, using stock you can actually buy
% in India.
%
% sim_v0_frame.m already shows the chassis is nowhere near its stress limit
% (tube SF ~17). So thicknesses here are NOT picked by stress. Each part is
% sized by whichever constraint really binds on a small welded machine, and the
% sim prints which one it was:
%   (a) INDIAN SHOP STOCK  - real sizes/gauges, not invented ones
%   (b) A JOINT / MFG NEED - one tube size covers frame + handle; the deck bolts
%                            down onto tapped SOLID posts, not a welded thin box
%   (c) THREAD ENGAGEMENT  - M5/M6 clamp bolts need ~5 mm of plate
%   (d) IMPACT ENERGY      - the guard band vs a thrown stone. The only
%                            genuinely strength-driven thickness on the machine
%   (e) A PLATFORM LOAD    - the deck under the battery + an accidental press
%   (f) OPERATOR PUSH/PULL - the handle: bending is not what limits it, TIPPING is
%
% Method: closed-form beam / plate / shear-plug checks. MS, E = 200 GPa.
% Everything is rounded UP to real stock and the mass delta is reported.
%
% Base MATLAB only. Run from anywhere (self-locating).
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));   % self-locate (repo convention)
addpath(fullfile(thisdir, 'specs'));
fails = 0;

%% ================================================================ CONSTANTS
g     = 9.81;
E_ms  = 200e9;      % MS Young's modulus, Pa
rho   = 7850;       % MS density, kg/m3
fy    = 250e6;      % IS 2062 E250 mild steel yield, Pa
UTS   = 400e6;      % MS ultimate, Pa
allow = 0.66*fy;    % 165 MPa static allowable (0.66 fy)
tau_u = 0.60*UTS;   % 240 MPa ultimate shear, for the impact plug model

% ------- frozen layout + specs (same sources as the other sims) ------------
mot    = motor_775_DC();  mot = mot(1);   % the 18 V option (6500 rpm)
line   = nylon_line_1p6();
mh     = motor_hub_6p5in_350W();

L_wb   = 0.260;                 % wheelbase, m
TRACK  = 0.420;                 % track, m
M_DES  = 21;                    % design mass, kg (sim_v0_frame.m Q2/Q3)
M_MODE = 20.5;                  % modelled mass, kg
SWATH  = line.D_cut_m;          % 0.200 m swath
R_TIP  = line.R_tip_m;          % 0.100 m tip radius
RPM    = mot.n0;                % 6500 rpm
V_TIP  = 2*pi*RPM/60*R_TIP;     % 68.1 m/s
R_W    = mh.wheel_R_m;          % 0.085 m, front-axle reference

fprintf('\n============================================================\n');
fprintf(' PROTOTYPE V0 - MATERIAL + THICKNESS SIZING (India-available)\n');
fprintf('============================================================\n');
fprintf(' Design mass %.0f kg (modelled %.1f) | allowable %.0f MPa on %.0f MPa yield\n', ...
    M_DES, M_MODE, allow/1e6, fy/1e6);
fprintf(' Cutter tip speed %.1f m/s (%.0f rpm) -> this drives the guard thickness\n', V_TIP, RPM);
fprintf(' Wheel radius %.0f mm (reference for the axle checks)\n', R_W*1000);

fprintf('\n--- WHAT A LOCAL STEEL SHOP STOCKS (confirm at the counter) ---\n');
fprintf(' MS square tube   : 20x20 and 25x25 in 1.2 / 1.6 (16g) / 2.0, 32x32x1.6, 40x40x2\n');
fprintf('                    sold by the length (6 m) - "square pipe 16 gauge"\n');
fprintf(' MS sheet (CRCA)  : 0.8 / 1.0 / 1.2 / 1.6 (16g) / 2.0 / 2.5 / 3.0 mm\n');
fprintf('                    NOT 1.5 mm - that is not an Indian stock thickness\n');
fprintf(' MS round bar     : 6 / 8 / 10 / 12 / 16 / 20 / 25 mm (any steel shop)\n');
fprintf(' MS flat (patri)  : 25x5, 25x6, 40x6, 50x8 mm\n');
fprintf(' MS pipe (IS 1239): 15 NB (21.3 OD), 20 NB (26.7 OD), 25 NB (33.4 OD)\n');
fprintf(' GI / GP sheet    : same gauges, zinc coated (rust option, no welding)\n');
fprintf(' Alu 6061 / HE30  : angle, flat, tube - 2-3x the price, city suppliers only\n');
fprintf(' SS 304 / 202     : sheet 1.0-2.0 mm - 3-4x the price\n');

%% ================================================== Q1 FRAME TUBES 25x25x1.6
fprintf('\n--- Q1 FRAME TUBES ---\n');
tube = shs(25, 1.6);
fprintf(' 25x25x1.6: A %.0f mm2, I %.0f mm4, Z %.0f mm3, J %.0f mm4, %.2f kg/m\n', ...
    tube.A*1e6, tube.I*1e12, tube.Z*1e9, tube.J*1e12, tube.m_per_m);
fprintf(' Governing constraint: ONE TUBE SIZE, plus the handle. Not stress.\n');
fprintf('  MfD pass: the notched full-width front axle is GONE (the front wheels now\n');
fprintf('  run on short stubs in corner brackets), so 25x25 is no longer forced by\n');
fprintf('  geometry - 20x20x1.6 would carry the chassis loads (SF ~10 static, 3.4 at\n');
fprintf('  a 3 g kerb). 25x25 stays for two reasons: the HANDLE is the most heavily\n');
fprintf('  loaded member on the machine and wants the bigger section (braced SF 2.2 at\n');
fprintf('  20x20 vs 3.7 at 25x25), and buying ONE 6 m length of ONE size is the single\n');
fprintf('  biggest thing that makes this easy to build.\n');

M1   = (M_DES*g/2)*TRACK/4;               % mid-span cross member, static
sig1 = M1/tube.Z;
fprintf(' Mid-span cross member : M %.1f Nm -> %.1f MPa -> SF %.0f\n', M1, sig1/1e6, allow/sig1);
fails = fails + gate('frame tube stress, static', sig1, allow, 'max');

M2   = (M_DES*g/2*3)*TRACK/4;             % diagonal / kerb, 3 g
sig2 = M2/tube.Z;
fprintf(' Diagonal 3 g kerb case: M %.1f Nm -> %.1f MPa -> SF %.1f\n', M2, sig2/1e6, allow/sig2);
fails = fails + gate('frame tube stress, 3 g kerb', sig2, allow, 'max');
len_all  = 2*0.235 + 2*0.345 + 2*0.79 + 0.30;      % frame + handle, m
save_all = len_all*(tube.m_per_m - shs(20,1.6).m_per_m);
fprintf(' -> 25x25x1.6 everywhere stays. 20x20x1.6 everywhere would save %.0f g, at\n', ...
    save_all*1000);
fprintf('    SF 10 (vs 17) static and a handle SF of 2.2 (vs 3.7). It is available if\n');
fprintf('    you want the lightest possible build, but it is NOT what is drawn.\n');

%% ================================================== Q2 DECK SHEET
fprintf('\n--- Q2 DECK SHEET (355 x 350 platform) ---\n');
nu      = 0.3;
a_panel = 0.320;                  % longest span between the 4 standoffs (X = +/-160)
gear    = 3.5*9.81;               % N, battery + controller spread over the deck
q_udl   = gear/(0.355*0.350);
P_press = 50;                     % N, a firm hand press on the panel
P_abuse = 200;                    % N, 20 kg dropped / leaning hard
fprintf(' Longest panel span between standoffs %.0f mm. Loads: gear 3.5 kg spread,\n', ...
    a_panel*1000);
fprintf(' a 50 N hand press, and a 200 N abuse case.\n');
for t_mm = [1.2 1.6 2.0]
    t = t_mm/1000;
    D = E_ms*t^3/(12*(1-nu^2));                       % plate rigidity, N.m
    s_pr = 6*(0.1273*P_press)/t^2;                    % square SS plate, centre load
    d_pr = 0.0116*P_press*a_panel^2/D;
    s_ud = 6*(0.0479*q_udl*a_panel^2)/t^2;
    d_ud = 0.00406*q_udl*a_panel^4/D;
    s_ab = 6*(0.1273*P_abuse)/t^2;
    fprintf('  t %.1f: press %.1f MPa (SF %4.1f) sag %.2f mm | gear %.2f MPa sag %.3f mm', ...
        t_mm, s_pr/1e6, allow/s_pr, d_pr*1000, s_ud/1e6, d_ud*1000);
    fprintf(' | abuse SF %.2f\n', allow/s_ab);
end
t_deck = 1.6e-3;
D_deck = E_ms*t_deck^3/(12*(1-nu^2));
sig_pr = 6*(0.1273*P_press)/t_deck^2;
d_pr   = 0.0116*P_press*a_panel^2/D_deck;
fprintf(' -> 1.6 mm: 16 gauge, the most common Indian sheet thickness, and it clears\n');
fprintf('    a 50 N hand press with SF %.1f and %.2f mm of sag.\n', allow/sig_pr, d_pr*1000);
fails = fails + gate('deck sag under a 50 N press (m)', d_pr, 2.0e-3, 'max');
fails = fails + gate('deck stress under a 50 N press', sig_pr, allow, 'max');
fprintf(' 1.6 mm is now the CAD value. 1.5 mm was the original pick and it is NOT\n');
fprintf(' an Indian stock size - that alone moved the deck to 1.6.\n');
fprintf(' WARNING: the deck is a GEAR PLATFORM, not a step. Standing on it (700 N)\n');
fprintf(' is ~208 MPa -> permanent dent. Brace the centre or go 2.0 mm if feet go on.\n');

%% ================================================== Q3 DECK POSTS
fprintf('\n--- Q3 DECK POSTS (why SOLID now) ---\n');
% The raised frame (rail underside now at 104, not 85) shortened these from
% 35 mm to 16 mm - still long enough for a 10 mm M6 tap with 5.9 mm left under
% the bolt. Shorter posts, same joint argument, a little less mass.
post_l  = 0.0159;
solid_m = pi*(16/1000)^2/4*post_l*rho;
tube_m  = shs(20,1.6).m_per_m*post_l;
fprintf(' 4 x O16 SOLID x %.0f = %.2f kg vs 4 x 20x20x1.6 SHS = %.2f kg (solid costs %+.2f).\n', ...
    post_l*1000, 4*solid_m, 4*tube_m, 4*(solid_m - tube_m));
Pcr = pi^2*E_ms*(pi*(16/1000)^4/64)/post_l^2;
fprintf(' The load is 60 N, so this is NOT a stress pick either way: Euler buckling is\n');
fprintf(' %.1f MN against a 60 N post. It is a JOINT pick. A box welded to a rail is\n', Pcr/1e6);
fprintf(' thin-wall on thin-wall - it burns through and it is what would pull the deck\n');
fprintf(' out of flat. A SOLID bar takes ONE thick-on-thin fillet weld and an M6 tap,\n');
fprintf(' so the deck BOLTS down and lifts off for service. %.0f g for that is cheap.\n', ...
    4*(solid_m - tube_m)*1000);

%% ================================================== Q4 FRONT STUB AXLES
fprintf('\n--- Q4 FRONT STUB AXLES (MfD pass: no notched full-width axle) ---\n');
fprintf(' The old O20 x 420 dead axle had to be notched 320 mm through the front cross\n');
fprintf(' member''s bottom wall - the hardest operation on the machine, and it removed\n');
fprintf(' the very wall the member is welded at. The front wheels now run on SHORT O20\n');
fprintf(' stubs welded into the same corner brackets that carry the rear hub motors.\n');
fprintf(' A stub is a CANTILEVER from the bracket to the wheel, not a spanning beam,\n');
fprintf(' so its moment is an order of magnitude below the old axle''s.\n');
arm_st = 0.030;                       % bracket face -> wheel centre
for gfac = [1 3]
    F = M_DES*g/2*gfac;               % whole front axle line on ONE wheel (harsh)
    M = F*arm_st;
    fprintf('  %.0f g single-wheel kerb: F %.0f N, M %.1f Nm\n', gfac, F, M);
    for d_mm = [16 20]
        rb = rod(d_mm);
        fprintf('     O%.0f stub: Z %.0f mm3 -> %.0f MPa -> SF %.1f | %.0f g each x 70 mm\n', ...
            d_mm, rb.Z*1e9, M/rb.Z/1e6, allow/(M/rb.Z), rb.m_per_m*0.070*1000);
    end
end
M_kerb  = (M_DES*g/2*3)*arm_st;
sig_ax  = M_kerb/rod(20).Z;
fails = fails + gate('front stub axle stress, 3 g one wheel', sig_ax, allow, 'max');
fprintf(' -> O20 for the stubs (SF %.1f at the harshest 3 g case). O16 also clears\n', allow/sig_ax);
fprintf('    (SF %.1f) if the wheels are bored 16. Retention is a washer + a O4 split\n', ...
    allow/(M_kerb/rod(16).Z));
fprintf('    pin in a cross-hole: our length, our tolerance, no bought-axle surprise.\n');
fprintf(' CHECK: the wheel bore must MATCH the stub. O20 suits the common 6.5in wheel\n');
fprintf('    bearing (6204 family). Buy the wheels FIRST, then cut the stub to suit.\n');

%% ================================================== Q5 CORNER BRACKETS
fprintf('\n--- Q5 CORNER BRACKETS (ONE 6 x 60 x 60 part, 4 off) ---\n');
T_hub  = 7.21;                       % Nm peak hub torque, spec [EST]
F_flat = T_hub/0.0055;               % D-shaft 16 / 13.5 across: the flat sits
                                     % 13.5 - 16/2 = 5.5 mm off the axis, and
                                     % THAT is the torque arm (not 13.5/2)
A_flat = 0.006*0.0116;               % 6 mm plate x the flat's 11.6 mm chord
fprintf(' The D-FLAT reacts the motor - a plain round hole would let the stator spin.\n');
fprintf('  %.2f Nm -> %.0f N on the flat -> %.1f MPa bearing over %.0f mm2. Trivial.\n', ...
    T_hub, F_flat, F_flat/A_flat/1e6, A_flat*1e6);
br_t_mm = 6;
F_w = M_DES*g/2*3;                   % whole front axle line on ONE wheel, at 3 g
for t_mm = [6 8]
    Zp = 0.060*(t_mm/1000)^2/6;      % weld-line section of the 60 mm wide plate
    M_w = F_w*0.030;
    fprintf('  %d mm plate: wheel-load weld line %.0f MPa -> SF %.1f\n', ...
        t_mm, M_w/Zp/1e6, allow/(M_w/Zp));
end
sig_br = F_w*0.030/(0.060*(br_t_mm/1000)^2/6);
fails = fails + gate('corner bracket stress, 3 g one wheel', sig_br, allow, 'max');
fprintf(' -> 6 mm x 60 x 60, ONE part for all FOUR corners: front bored O20 for the stub\n');
fprintf('    (+ a split pin), rear bored O16.2 with a flat for the motor. Cut and drilled\n');
fprintf('    as one batch. Replaced 2 x 8 mm dropouts PLUS the whole O20 x 420 axle.\n');
fprintf(' CHECK: the rear bracket''s flat must match the motor''s D-flat clocking. Confirm\n');
fprintf('    on the bench - hub-motor kits usually also ship their own bracket.\n');

%% ================================================== Q6 MOTOR CARRIER
fprintf('\n--- Q6 MOTOR CARRIER (ring + 2 arms) ---\n');
bolt_r   = 35;                                  % M5 clamp bolts on R35
ring_min = 2*(bolt_r + 2.5 + 5);                % bolt centre + bolt r + edge, to OD
fprintf(' Binding constraint is THREAD ENGAGEMENT: 4 x M5 need ~5 mm of plate, so the\n');
fprintf(' ring stays 5 mm thick. The OD is not bound by anything:\n');
fprintf('  bore O45.25 + M5 on R35 -> the ring only needs OD >= %.0f mm.\n', ring_min);
ring_old = pi*((160/2/1000)^2 - (45.25/2/1000)^2)*0.005*rho;
ring_new = pi*((120/2/1000)^2 - (45.25/2/1000)^2)*0.005*rho;
fprintf('  O100 x 5 = %.2f kg | O120 x 5 = %.2f kg | O160 x 5 = %.2f kg (current)\n', ...
    pi*((100/2/1000)^2-(45.25/2/1000)^2)*0.005*rho, ring_new, ring_old);
d_ring = ring_new - ring_old;
fprintf(' -> O120 x 5: still %.0f mm of annulus for the clamp, saves %.2f kg.\n', ...
    (120-45.25)/2, -d_ring);

%% ================================================== Q7 GUARD BAND
fprintf('\n--- Q7 GUARD BAND (the one real strength-driven thickness) ---\n');
% The work to punch a plug out is tau x (shear area) x (plug travel = t), so
% E_perf = tau_u * pi * d * t^2. (A linear-in-t model understates it badly.)
fprintf(' Shear-plug model: E_perf = tau_u x (pi d) x t x t, tau_u %.0f MPa, 20 mm\n', tau_u/1e6);
fprintf(' stone. Impact speed = the line tip speed (a deliberately harsh bound).\n');
d_st = 0.020;
m_st = 0.020;
E_stone = 0.5*m_st*V_TIP^2;
t_need  = sqrt(E_stone/(tau_u*pi*d_st));
fprintf('  stone mass %.0f g at %.1f m/s -> %.1f J, so t >= %.1f mm to resist plugging\n', ...
    m_st*1000, V_TIP, E_stone, t_need*1000);
fprintf('  thickness | perforation energy | SF vs the %.0f g stone\n', m_st*1000);
t_guard = 2.5e-3;
for tt = [1.6 2.0 2.5 3.0]
    E_perf = tau_u*pi*d_st*(tt/1000)^2;
    fprintf('   %4.1f mm  |      %5.1f J       | SF %.2f\n', tt, E_perf, E_perf/E_stone);
end
E_guard   = tau_u*pi*d_st*t_guard^2;
guard_old = pi*0.244*0.055*0.0020*rho;
guard_new = pi*0.244*0.055*0.0025*rho;
d_guard   = guard_new - guard_old;
fprintf(' -> 2.0 mm is borderline (SF %.2f). 2.5 mm gives SF %.2f for %.2f kg more, so\n', ...
    (tau_u*pi*d_st*0.0020^2)/E_stone, E_guard/E_stone, d_guard);
fprintf('    pick 2.5 mm. NEVER plastic or aluminium on the guard.\n');
fprintf(' Note: a stone only reaches its full tip speed if it is hit square and once.\n');
fprintf(' Realistically it leaves at 30-50%% of that, i.e. 5-12 J, so this is a harsh\n');
fprintf(' bound and 2.5 mm is comfortably inside it.\n');
fprintf(' ADD a 15-20 mm downward lip (free - cut it from the same strip): it stops\n');
fprintf(' debris leaving sideways, which is the usual failure of a plain band.\n');
fails = fails + gate('guard thickness vs a 20 g stone at full tip speed (m)', ...
    t_guard, t_need, 'min');
% The two tabs that tie the rim to the frame got LONGER when the frame was
% lifted clear of the hub axles (15 -> 34 mm), so check that cantilever, not
% just the band. They are cut from the same 2.5 mm strip.
tab_w  = 30.0e-3;
tab_t  = 2.5e-3;
tab_l  = 34.0e-3;
F_tab  = 200;                                    % N sideways on the rim, hand-harsh
Z_tab  = tab_t*tab_w^2/6;                        % bends about its 30 mm width
sig_tb = F_tab*tab_l/Z_tab;
fprintf(' Tab cantilever %.0f x %.1f x %.0f, %.0f N at the rim: %.0f MPa -> SF %.0f\n', ...
    tab_w*1000, tab_t*1000, tab_l*1000, F_tab, sig_tb/1e6, allow/sig_tb);
fails = fails + gate('guard tab cantilever, 200 N at the rim', sig_tb, allow, 'max');

%% ================================================== Q8 HANDLE
fprintf('\n--- Q8 HANDLE (most heavily loaded member on the machine) ---\n');
F_push = 250;                    % N, a brisk two-handed push
h_grip = 0.90;                   % m
F_leg  = F_push/2;
fprintf(' Operator push %.0f N at a %.0f mm grip on 2 legs (a U handle).\n', F_push, h_grip*1000);
for nm = 1:3
    if nm == 1
        pr = shs(25,1.6); lbl = '25x25x1.6';
    elseif nm == 2
        pr = shs(25,2.0); lbl = '25x25x2.0';
    else
        pr = shs(32,1.6); lbl = '32x32x1.6';
    end
    M_un = F_leg*(h_grip-0.11);
    M_br = F_leg*(h_grip-0.11)/2;
    fprintf('   %s unbraced %.0f MPa (SF %.2f) | mid-braced %.0f MPa (SF %.2f)\n', ...
        lbl, M_un/pr.Z/1e6, allow/(M_un/pr.Z), M_br/pr.Z/1e6, allow/(M_br/pr.Z));
end
pr   = shs(25,1.6);
M_h  = F_leg*(h_grip-0.11)/2;
fprintf(' -> 25x25x1.6 with ONE mid brace: SF %.1f, and it is the frame tube too.\n', allow/(M_h/pr.Z));
fails = fails + gate('handle stress with a mid brace', M_h/pr.Z, allow, 'max');

% ---- what really limits the handle: TIPPING, not bending ------------------
y_cg    = -0.037;                              % CAD-verified CG offset, m
d_tip   = L_wb/2 - y_cg;                       % CG to the front axle line, m
F_grade = M_DES*g*0.08 + M_DES*g*sind(5);      % rolling + 5 deg grade
F_back  = M_DES*g*d_tip/h_grip;                % straight-back push that lifts the fronts
fprintf('\n TIPPING (this, not bending, is what limits the handle):\n');
fprintf('   to roll up a 5 deg grade the operator supplies : %.0f N\n', F_grade);
fprintf('   a STRAIGHT-BACK push lifts the front wheels at: %.0f N (margin %.1f)\n', ...
    F_back, F_back/F_grade);
fprintf('   -> never push straight back; the handle must be used along its own axis.\n');
lean = atand(0.39/0.754);                      % handle leans this far from vertical
den  = sind(lean)*h_grip - cosd(lean)*(0.52 + 0.13);
if den > 0
    F_along = M_DES*g*d_tip/den;
    fprintf('   push ALONG the %.0f deg handle lifts the fronts at %.0f N (margin %.1f)\n', ...
        lean, F_along, F_along/F_grade);
else
    F_along = 99*F_grade;
    fprintf('   push ALONG the %.0f deg handle CANNOT lift the fronts - the downward\n', lean);
    fprintf('     component (%.0f%% of the push) always wins the moment balance.\n', cosd(lean)*100);
end
fails = fails + gate('front-lift margin, push along the handle', F_along/F_grade, 2.0, 'min');
fprintf('   Keep the grip low and well back; and let the DRIVE pull the machine, not\n');
fprintf('   the operator shoving it up a slope.\n');

%% ================================================== Q9 FASTENERS
fprintf('\n--- Q9 FASTENERS ---\n');
fprintf(' M5 x 16  8.8 x 4  - motor clamp bolts into the carrier ring\n');
fprintf(' M6 x 20  8.8 x 4  - carrier arms to the cross members\n');
fprintf(' M6 x 16  8.8 x 4  - deck lid down into the tapped deck posts (deck LIFTS OFF)\n');
fprintf(' M8 x 25  8.8 x 6  - handle legs (4) + battery-box hold-down (2)\n');
fprintf(' O4 split pin x 2  - front stub axle retention (washer + pin)\n');
fprintf(' M16 nyloc + O30 washer x 2 - rear axle clamp (hub motors ship theirs)\n');
fprintf(' All 8.8, nyloc or spring washers (the line vibrates).\n');

%% ================================================== Q10 MASS EFFECT
fprintf('\n--- Q10 MASS EFFECT OF THE MfD PASS (measured, not guessed) ---\n');
d_axle  = pi*0.010^2*0.420*rho;                    % the O20 x 420 rod, deleted
d_stub  = 2*(pi*0.010^2*0.070*rho);                % 2 x O20 x 70 stubs added
d_brkF  = 2*0.15;                                  % 2 x front corner brackets added
d_brkR  = 2*(0.060*0.060*(6-8)/1000*rho);          % rear dropouts 8 -> 6 mm
d_post  = 4*(solid_m - tube_m);                    % standoffs -> solid tapped posts
d_tab   = 2*(0.030*0.0025*0.034*rho);              % 2 guard mount tabs (2.5 x 30 x 34)
fprintf('  full-width O20 x 420 axle deleted  %+.2f kg\n', -d_axle);
fprintf('  2 x O20 x 70 front stubs added     %+.2f kg\n', d_stub);
fprintf('  2 x front corner brackets added    %+.2f kg\n', d_brkF);
fprintf('  rear dropouts 8 -> 6 mm            %+.2f kg\n', d_brkR);
fprintf('  standoffs -> 4 x solid O16 posts   %+.2f kg\n', d_post);
fprintf('  2 x guard mount tabs               %+.2f kg\n', d_tab);
d_all = -d_axle + d_stub + d_brkF + d_brkR + d_post + d_tab;
fprintf('  net MfD change                     %+.2f kg -> fabricated steel 6.13 -> %.2f kg\n', ...
    d_all, 6.13+d_all);
fprintf(' (the CAD measures 5.64 kg; the small remainder is the D-holes, the split-pin\n');
fprintf('  hole and the tapped posts being cut away.)\n');
fprintf(' All-up mass %.1f kg as modelled (CAD 20.53). Design mass stays %.0f kg, so NO\n', ...
    M_MODE, M_DES);
fprintf(' gate in any other sim moves - the tank turn still sizes on 21 kg.\n');

%% ================================================== Q11 ALTERNATIVES
fprintf('\n--- Q11 MATERIAL ALTERNATIVES (why MS wins here) ---\n');
fprintf(' material       density  E(GPa)  fy(MPa)  rel.cost  availability in India\n');
fprintf(' MS / CRCA       7850     200     250      1.00     every steel shop\n');
fprintf(' GI / GP sheet   7850     200     250      1.15     every hardware shop\n');
fprintf(' Alu 6061-T6     2700      69     240      3.00     city suppliers, not local\n');
fprintf(' SS 304          8000     193     215      3.50     city suppliers\n');
fprintf(' -> Aluminium saves ~60%% of the mass but needs ~2.9x the thickness to match\n');
fprintf('    stiffness (E/3), so on a stiffness-driven frame the saving mostly\n');
fprintf('    evaporates - at 3x the cost. It only suits the deck, and the guard must\n');
fprintf('    stay steel for impact.\n');
fprintf(' -> GI sheet is the real cheat for the deck + guard: same thickness, no\n');
fprintf('    paint, survives a wet underside. Weld it only with ventilation.\n');

%% ================================================== Q12 BUY LIST
fprintf('\n============================================================\n');
fprintf(' BUY LIST (Indian shop terms)\n');
fprintf('============================================================\n');
len_tube = 2*0.235 + 2*0.345 + 2*0.79 + 0.30;
fprintf(' 1 x MS square tube 25x25x1.6 (16 gauge)     1 length (6 m)\n');
fprintf('     uses %.2f m: 2 rails 235, 2 cross 345, 2 handle legs 790, 1 brace 300\n', len_tube);
fprintf(' 1 x MS / CRCA sheet 1.6 mm (16g)            a 400 x 400 mm offcut\n');
fprintf('     deck 355 x 350 with 4 x O6.5 bolt holes  (or a full 8x4 ft sheet)\n');
fprintf(' 1 x MS sheet 2.5 mm                         800 x 60 mm strip\n');
fprintf('     guard band 244 OD x 55 tall + a 20 mm lip + 2 x 30 x 34 tabs\n');
fprintf(' 1 x MS round bar O20                        0.2 m  (2 x 70 mm front stubs)\n');
fprintf(' 1 x MS round bar O16                        0.2 m  (4 x 16 mm posts, M6 tapped)\n');
fprintf(' 1 x MS plate 6 mm                           4 x 60 x 60  (the FOUR corner brackets)\n');
fprintf(' 1 x MS plate 5 mm                           170 x 230    (carrier ring + arms)\n');
fprintf(' 4 x M5 x 16, 8 x M6 x 16/20, 6 x M8 x 25 + 2 x O4 split pins - all 8.8, + nylocs\n');
fprintf(' paint: red oxide primer + enamel, or use GI sheet for the deck and guard\n');

%% ================================================================ RESULT
fprintf('\n============================================================\n');
if fails == 0
    fprintf(' RESULT: all sizing gates PASS - every size above is standard Indian stock\n');
else
    fprintf(' RESULT: %d gate(s) need attention\n', fails);
end
fprintf('============================================================\n');

%% ================================================================ helpers
function n = gate(name, value, limit, kind)
%GATE  Print a PASS/FAIL sizing gate, return 1 if it failed.
if strcmp(kind, 'max')
    ok = value <= limit;
    rel = '<=';
else
    ok = value >= limit;
    rel = '>=';
end
if ok
    word = 'PASS';
else
    word = 'FAIL';
end
fprintf('   [%s] %-44s %9.4g %s %9.4g\n', word, name, value, rel, limit);
n = ~ok;
end

function s = shs(a_mm, t_mm)
%SHS  Square hollow section properties. a_mm side, t_mm wall. Returns SI.
ai = a_mm - 2*t_mm;
s.A = (a_mm^2 - ai^2)*1e-6;              % m2
s.I = (a_mm^4 - ai^4)/12*1e-12;          % m4
s.Z = s.I/(a_mm/2/1000);                 % m3
s.J = (a_mm-t_mm)^3*t_mm*1e-12;          % m4, Bredt closed thin-wall square
s.m_per_m = s.A*7850;                    % kg/m
end

function s = rod(d_mm)
%ROD  Solid round bar properties. d_mm diameter. Returns SI.
s.A = pi*d_mm^2/4*1e-6;
s.I = pi*d_mm^4/64*1e-12;
s.Z = pi*d_mm^3/32*1e-9;
s.J = 2*s.I;
s.m_per_m = s.A*7850;
end
