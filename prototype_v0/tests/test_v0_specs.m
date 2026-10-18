function tests = test_v0_specs
%TEST_V0_SPECS  Regression tests for the frozen prototype_v0 numbers.
%   Locks the values that the sims, the CAD and BRIEF.md all quote, so a careless
%   edit to a spec - or to one of the three copies of the frozen layout - fails
%   loudly instead of quietly moving a design gate.
%
%   The last block re-derives the headline numbers (tank turn, ground pressure,
%   turning envelope, tip angle) by a path that is independent of the sims, so a
%   changed formula shows up as a disagreement between the two.
%
%   Run:  runtests('<repo>/prototype_v0/tests/test_v0_specs.m')
%   Base MATLAB only (no toolboxes).

tests = functiontests(localfunctions);
end


%% ---------------------------------------------------------------- fixture
function setupOnce(tc)
% Self-locating, same convention as the sims: add this thread's specs/ to the path.
here = fileparts(mfilename('fullpath'));
root = fileparts(here);
addpath(fullfile(root, 'specs'));
tc.TestData.root = root;
end


%% ---------------------------------------------------------------- specs
function test_line_spec_is_the_confirmed_one(tc)
s = nylon_line_1p6();
verifyEqual(tc, s.d_line_m, 1.6e-3);      % FASTRIM 1.6 mm round
verifyEqual(tc, s.D_hub_m, 50e-3);        % printed D50 zip-tie hub
verifyEqual(tc, s.r0_m, 25e-3);
verifyEqual(tc, s.L_line_m, 75e-3);
verifyEqual(tc, s.R_tip_m, 100e-3);
verifyEqual(tc, s.D_cut_m, 200e-3);       % the 200 mm swath every doc quotes
verifyEqual(tc, s.n_lines, 2);
end

function test_775_is_a_standard_775(tc)
mot = motor_775_DC();
verifyEqual(tc, numel(mot), 3);
verifyEqual(tc, [mot.n0], [6500 9000 11000]);
for k = 1:numel(mot)
    verifyEqual(tc, mot(k).D_body_mm, 44.5);
    verifyEqual(tc, mot(k).L_body_mm, 66);
    verifyEqual(tc, mot(k).D_shaft_mm, 5.0);   % the CAD hub bore depends on this
    verifyEqual(tc, mot(k).L_shaft_mm, 17);
    verifyEqual(tc, mot(k).m_kg, 0.35);
    verifyGreaterThan(tc, mot(k).Tstall, mot(k).Tcont);
end
Kt_stall = 9.5493*[mot.V]./[mot.n0];           % V/(rpm) -> Nm/A
verifyLessThan(tc, max([mot.Tstall]./Kt_stall), 45);   % plausible 775 stall current
end

function test_tip_speed_gate_is_reachable(tc)
% A clean cut needs >= 50 m/s tip speed; the 775 at 6500 rpm has to clear it.
s = nylon_line_1p6();
verifyGreaterThanOrEqual(tc, 2*pi*6500/60*s.R_tip_m, s.tip_speed_clean_mps);
end

function test_hub_motor_spec(tc)
m = motor_hub_6p5in_350W();
verifyEqual(tc, m.tyre_OD_mm, 170);
verifyEqual(tc, m.mass_kg, 2.30);
verifyEqual(tc, m.V_nom, 36);
verifyEqual(tc, m.P_rated, 350);
verifyEqual(tc, m.tyre_w_mm, 45);
verifyEqual(tc, m.contact_w_mm, 40);
verifyLessThanOrEqual(tc, m.contact_w_mm, m.tyre_w_mm);   % patch <= section
verifyGreaterThan(tc, m.T_peak_Nm, m.T_cont_Nm);
end


%% ------------------------------------------- the same number, four files
function test_wheel_width_agrees_with_the_cad(tc)
% The CAD's clearance gates are computed against WHEEL_W; the spec describes the
% same tyre. If they drift, every wheel clearance is measured against a fiction.
m  = motor_hub_6p5in_350W();
ww = num_from(fullfile(tc.TestData.root, 'cad', 'build_v0_frame.py'), 'WHEEL_W\s*=\s*([0-9.]+)');
verifyEqual(tc, ww, m.tyre_w_mm);
end

function test_frozen_layout_agrees_in_all_four_files(tc)
% The frozen 260 x 420 layout is written in the frame sim, the drive sim, the CAD
% and the sketch. This is the guard for the drift that once left sim_v0_drive.m
% on a stale 450 x 550 / 30 kg build.
r = tc.TestData.root;
wb_sim = num_from(fullfile(r, 'sim_v0_frame.m'), 'L_wb\s*=\s*([0-9.]+)')*1000;
tr_sim = num_from(fullfile(r, 'sim_v0_frame.m'), 'W_track\s*=\s*([0-9.]+)')*1000;
wb_cad = num_from(fullfile(r, 'cad', 'build_v0_frame.py'), 'WHEELBASE\s*=\s*([0-9.]+)');
tr_cad = num_from(fullfile(r, 'cad', 'build_v0_frame.py'), 'TRACK\s*=\s*([0-9.]+)');
wb_drv = num_from(fullfile(r, 'sim_v0_drive.m'), 'L_wb\s*=\s*([0-9.]+)')*1000;
tr_drv = num_from(fullfile(r, 'sim_v0_drive.m'), 'W_track\s*=\s*([0-9.]+)')*1000;
wb_skt = num_from(fullfile(r, 'sketch_v0.m'), 'L_wb\s*=\s*([0-9.]+)');
tr_skt = num_from(fullfile(r, 'sketch_v0.m'), 'track\s*=\s*([0-9.]+)');
verifyEqual(tc, [wb_cad wb_drv wb_skt], [wb_sim wb_sim wb_sim], 'wheelbase disagrees');
verifyEqual(tc, [tr_cad tr_drv tr_skt], [tr_sim tr_sim tr_sim], 'track disagrees');
end

function test_design_mass_agrees_with_the_docs(tc)
r = tc.TestData.root;
m_drive = num_from(fullfile(r, 'sim_v0_drive.m'), 'm_machine\s*=\s*([0-9.]+)');
brief   = fileread(fullfile(r, 'BRIEF.md'));
tok     = regexp(brief, 'design ([0-9]+) kg', 'tokens', 'once');
verifyNotEmpty(tc, tok, 'no "design NN kg" figure in BRIEF.md');
verifyEqual(tc, m_drive, str2double(tok{1}));
end


%% ------------------------------------------------- the headline numbers
function test_headline_numbers_re_derived(tc)
% Independent re-derivation of the numbers BRIEF.md quotes, by a different path
% than the sims. If a sim formula changes, one of the two moves.
g  = 9.81;
mh = motor_hub_6p5in_350W();

T_pivot = 0.60*21*g*0.26*mh.wheel_R_m/(2*0.42);
verifyEqual(tc, T_pivot, 3.25, 'AbsTol', 0.02);
verifyLessThanOrEqual(tc, T_pivot, mh.T_cont_Nm);          % the actual gate

gp = 21*g/(4*(mh.contact_w_mm/1000)*0.05);
verifyEqual(tc, gp, 25.8e3, 'RelTol', 0.01);

verifyEqual(tc, 2*(hypot(0.21, 0.13) + mh.wheel_R_m)*1000, 664, 'AbsTol', 1);

% CAD-verified CG: 46 mm behind centre, 155 mm high -> worst tip is rearward.
verifyEqual(tc, atand((130-46.4)/155.3), 28.3, 'AbsTol', 0.2);
end


%% ------------------------------------------- the CAD CG and the sim's CG
function test_cg_agrees_between_the_sim_and_the_mass_check(tc)
% freecad_mass_check.py prints the real CG and holds a SIM_CG literal that
% sim_v0_frame.m Q4 must match - otherwise the tip angles in the sim, in the
% mass check and in BRIEF.md are computed about three different centres of mass.
r    = tc.TestData.root;
sim  = num_from(fullfile(r, 'sim_v0_frame.m'), 'cg_h\s*=\s*([0-9.]+)')*1000;
chk  = num_from(fullfile(r, 'cad', 'freecad_mass_check.py'), ...
    'SIM_CG, SIM_LAT, SIM_LONG = ([0-9.]+)');
verifyEqual(tc, sim, chk, 'sim CG height vs mass-check SIM_CG');
end


%% ------------------------------------------- the raised frame, both files
function test_frame_lift_agrees_between_the_sim_and_the_cad(tc)
% The frame was raised to clear the hub motors' axle stack (stub + nut +
% washer) inside the rear cross member. The CAD owns the height; sim_v0_frame.m
% rebuilds the deck height from it, so a careless edit to either moves the
% machine's deck and its CG without the other noticing.
r   = tc.TestData.root;
cad = num_from(fullfile(r, 'cad', 'build_v0_frame.py'), 'FRAME_Z0 = ([0-9.]+)');
sim = num_from(fullfile(r, 'sim_v0_frame.m'), 'rail_z0\s*=\s*([0-9.]+)')*1000;
verifyEqual(tc, cad, sim, 'frame underside height, CAD vs sim');
end


%% --------------------------------------------- material sizes are buyable
function test_material_sizes_agree_between_sim_and_cad(tc)
% sim_v0_structure.m picks the thicknesses; build_v0_frame.py builds them. If the
% picking and the building drift, the drawing stops matching the analysis.
r   = tc.TestData.root;
cad = fullfile(r, 'cad', 'build_v0_frame.py');
sim = fullfile(r, 'sim_v0_structure.m');
verifyEqual(tc, num_from(cad, 'DECK_T = [0-9.]+, [0-9.]+, ([0-9.]+)'), ...
    num_from(sim, 't_deck\s*=\s*([0-9.]+)e-3'), 'deck thickness');
verifyEqual(tc, num_from(cad, 'GUARD_T = [0-9.]+, ([0-9.]+)'), ...
    num_from(sim, 't_guard\s*=\s*([0-9.]+)e-3'), 'guard thickness');
verifyEqual(tc, num_from(cad, 'TAB_W, TAB_T, TAB_L = [0-9.]+, ([0-9.]+)'), ...
    num_from(sim, 'tab_t\s*=\s*([0-9.]+)'), 'guard tab thickness');
end

function test_every_cad_thickness_is_indian_stock(tc)
% The whole point of the sizing exercise: nothing on the drawing is a size that a
% local steel shop will not sell. 1.5 mm sheet, for one, is not an Indian stock
% thickness - that is why the deck moved to 1.6.
r     = tc.TestData.root;
cad   = fullfile(r, 'cad', 'build_v0_frame.py');
sheet = [0.8 1.0 1.2 1.6 2.0 2.5 3.0];       % CRCA / HR / GI sheet
plate = [3 4 5 6 8 10 12];                   % MS plate (patra)
wall  = [1.2 1.6 2.0 2.6 3.2];               % SHS / RHS wall thickness
deck  = num_from(cad, 'DECK_T = [0-9.]+, [0-9.]+, ([0-9.]+)');
guard = num_from(cad, 'GUARD_T = [0-9.]+, ([0-9.]+)');
tube  = num_from(cad, 'WALL\s*=\s*([0-9.]+)');
carr  = num_from(cad, 'CARRIER_T = [0-9.]+, ([0-9.]+)');
brkt  = num_from(cad, 'BR_T, BR_W, BR_H = ([0-9.]+)');
tab   = num_from(cad, 'TAB_W, TAB_T, TAB_L = [0-9.]+, ([0-9.]+)');
verifyTrue(tc, any(abs(sheet-deck)  < 1e-9), sprintf('deck  %g mm not stock sheet', deck));
verifyTrue(tc, any(abs(sheet-guard) < 1e-9), sprintf('guard %g mm not stock sheet', guard));
verifyTrue(tc, any(abs(sheet-tab)   < 1e-9), sprintf('tab   %g mm not stock sheet', tab));
verifyTrue(tc, any(abs(wall-tube)   < 1e-9), sprintf('wall  %g mm not stock tube', tube));
verifyTrue(tc, any(abs(plate-carr)  < 1e-9), sprintf('carrier %g mm not stock plate', carr));
verifyTrue(tc, any(abs(plate-brkt)  < 1e-9), sprintf('bracket %g mm not stock plate', brkt));
end


%% ---------------------------------------------------------------- helper
function v = num_from(file, expr)
%NUM_FROM  First numeric literal captured by EXPR in FILE.
txt = fileread(file);
tok = regexp(txt, expr, 'tokens', 'once');
assert(~isempty(tok), 'pattern "%s" not found in %s', expr, file);
v = str2double(tok{1});
end
