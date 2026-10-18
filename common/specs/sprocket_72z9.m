function s = sprocket_72z9()
% SPROCKET_72z9  Laser-cut drive sprocket for ACETRAX 180x72x37 track.
% Centre-drive laminated pack in B=23 horn gap. CAD: track_180x60x37/cad/
% sprocket_72z9.dxf(.stl/.json); sims: sim_sprocket_mesh.py (PASS),
% sim_sprocket_verify.m (ALL PASS); notes: SPROCKET_72z9_NOTES.md.
% Sources: ACETRAX pdf (track row), Fedotkin (PD/form), US7425044 (gorge play,
% 0-1%% bed-in), US7413268 (load sharing), DIN6885-1/ISO773 (key+fits),
% Shigley Ch.7/17 (strength), ASME B29.1/ISO606 background.

s.name       = 'Drive sprocket 72z9, 180x72x37 track';
s.track      = '180x72x37';
s.z          = 9;
s.pitch_mm   = 72;
s.PD_mm      = 210.51;   % P/sin(pi/z)
s.Rp_mm      = 105.26;

% --- tooth (mm) ---
s.tip_dia_mm  = 210.51;  % at pitch line (classic tip)
s.root_dia_mm = 160.51;
s.tooth_h_mm  = 25;
s.tip_w_mm    = 22;
s.root_w_mm   = 30;
s.tip_chamfer_mm = 3;    % entry/exit relief (gear practice)
s.root_fillet_mm = 3;    % plasma-safe
s.profile_tol_mm = 0.2;  % laser

% --- pack: laminate of <=8mm sheets (shop limit) ---
s.pack_mm    = 16;
s.laminate   = '8+8';    % any <=8 stack (7+7/6+6), recheck play
s.plate_tol_mm = 0.3;
s.material   = 'MS IS2062 E250Br';
s.centre_play_mm = 3.5;  % per side in B=23 gap (want 1.5..5)
s.drive_window_mm = 52;  % insert-to-insert (tooth 22/30 fits)

% --- mounting (mm) ---
s.bore_mm    = 40;  s.bore_fit = 'H7 (laser 39.6 + ream)'; s.shaft_fit = 'h6';
s.key        = '12x8 Form A'; s.keyway_fit = 'JS9';
s.key_t2_mm  = 3.3; s.key_t1_note = 't1=5.0 on shaft drawing (DIN6885-1)';
s.bolts      = '6xM12-8.8 + nyloc, 80Nm (clamps laminate)';
s.bolt_hole_mm = 13.5; s.bolt_bcd_mm = 110;
s.hub        = 'turned boss OD76xL44 from dia90 bar';
s.weld       = '5mm fillet both sides, alternate, clamp flat';

s.mass_kg    = 3.79;     % FreeCAD 3.786 / STL 3.80 / analytic 3.80

% --- verified limits / constraints ---
s.torque_burst_Nm = 160; % tooth SF41 (3 share), key 55/15 MPa, bolts 485N ea
s.wrap_deg_min    = 150; % keep >=150deg wrap (load sharing, Fukushima watch)
s.mesh_centred_mm = 7.9; % min kinematic clearance, 0 penetrations (sim)
s.chordal_pct_z9  = 6.03;
s.process = 'CUT DXF x2 (nest 2-up); laser profile+bolts; bore ream H7; keyway slot/broach JS9; deburr + break tips 2mm';
s.status = 'CAD+sim verified; NEEDS windowed-belt track rev + sample seating/wear check';
end
