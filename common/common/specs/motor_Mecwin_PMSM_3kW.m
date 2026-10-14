function s = motor_Mecwin_PMSM_3kW()
% Mecwin PMSM Mid Motor 3 kW (Screenshot_20261009_225241_Chrome.jpg)
s.name          = 'Mecwin PMSM Mid Motor 3kW';
s.type          = 'PMSM_mid';
s.rated_power_W = 3000;
s.rated_voltage_V = [48 60 72];
s.max_speed_rpm = 4000;
s.shaft         = 'spline_sprocket';
s.cont_factor   = 0.65;      % EV peak rating -> continuous derate
s.source_file   = 'Screenshot_20261009_225241_Chrome.jpg';
end
