function s = machine_500mm_tracked()
% MACHINE_500MM_TRACKED  Chassis + rotor layout for 500 mm tracked flail.
s.name              = 'Tracked flail, 500 mm swath (own chassis)';
s.working_width_m   = 0.500;
s.drum_OD_candidates_m = [0.0508 0.0762 0.100];  % 2in, 3in, 100mm
s.pin_standoff_m    = 0.020;      % pin-centre height above drum surface
s.rotor_speed_sweep_rpm = 2000:250:3500;
s.forward_speed_mps_nom = 1.0;    % 3.6 km/h while mowing
s.forward_speed_mps_range = [0.5 1.5];
% Blade counts under study (hammer 130mm wide -> 4/row; mulchers 58mm -> 9/row):
s.n_blades_hammer   = [8 12];     % 2-3 rows of 4
s.n_blades_mulcher  = 18;         % 2 rows of 9
s.windage_ref_W     = 400;        % no-load air+brg power @3000rpm, 0.5m (tune on test)
s.windage_ref_rpm   = 3000;
s.trans_eff         = 0.92;       % belt/chain rotor drive
s.motor_eff         = 0.88;
% Tracked chassis targets (see CHASSIS_BRIEF.md for sizing math):
s.track_width_m     = 0.750;    % outer, set by 45deg tip-over table (tilt_check)
s.track_contact_m   = [0.750 0.150]; % [length width] per track
s.track_mu_grass    = 0.12;     % rolling resistance, tracks on grass [EST]
s.sprocket_r_m      = 0.10;
s.slope_cont_deg    = 30;       % continuous rating
s.slope_burst_deg   = 45;       % current-limited burst
end
