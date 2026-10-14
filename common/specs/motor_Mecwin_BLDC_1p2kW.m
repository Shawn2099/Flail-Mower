function s = motor_Mecwin_BLDC_1p2kW()
% Mecwin L3-BLDC Mid Motor 1.2 kW (Screenshot_20261009_225138_Chrome.jpg)
s.name          = 'Mecwin L3-BLDC Mid Motor 1.2kW';
s.type          = 'BLDC_mid';
s.rated_power_W = 1200;
s.rated_voltage_V = [48 60];
s.rated_speed_rpm = 3300;
s.max_speed_rpm = 3500;
s.max_dc_current_A = 60;
s.stall_torque_Nm = 25;      % @250rpm (geared output)
s.shaft         = 'helical_gear';
s.cont_factor   = 0.65;      % EV peak rating -> industrial continuous derate
s.source_file   = 'Screenshot_20261009_225138_Chrome.jpg';
end
