function s = motor_Mecwin_BLDC_1p0kW()
% Mecwin L3-BLDC Mid Motor 1.0 kW (1kw bldc.png, shared Oct 2026)
s.name          = 'Mecwin L3-BLDC Mid Motor 1.0kW';
s.type          = 'BLDC_mid';
s.rated_power_W = 1000;
s.rated_voltage_V = [48 60];
s.rated_speed_rpm = 3000;
s.max_speed_rpm = 3300;
s.max_dc_current_A = 55;
s.stall_torque_Nm = 23;      % @250rpm (geared output)
s.shaft         = 'helical_gear';
s.cont_factor   = 0.65;      % EV peak rating -> industrial continuous derate
s.source_file   = '1kw bldc.png';
end
