function s = motor_traction_geared()
% MOTOR_TRACTION_GEARED  Track drive requirement (2x, one per track). Values =
% calculated demand (see CHASSIS_BRIEF.md); dims TBD against supplier catalogue.
% Duty: 30deg continuous, 45deg current-limited burst. Bus 48V (common with MVP pack).
s.name            = 'Traction gearmotor 48V ~1kW (2x)';
s.qty             = 2;
s.bus_V           = 48;
s.rated_power_W   = 1000;     % each; demand 1185W total @30deg/200kg/1m/s
s.output_torque_Nm = 60;      % each; demand 59 @30deg, 78 burst @45deg (sprocket r=0.10)
s.output_rpm      = 150;      % ~1.5 m/s at r=0.10 sprocket
s.driver          = 'separate 48V BLDC drivers (NOT the Mecwin 300A - that is the mower)';
s.mount           = 'TBD: inside track frames, shaft outboard to sprocket';
s.mass_kg_each    = 8;        % [EST] incl. gearbox; confirm at order
s.status          = 'OPEN: pick catalogue part against this sheet (track supplier combo)';
end
