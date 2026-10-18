function s = motor_Mecwin_PMSM_4p5kW()
% Mecwin PMSM Mid Motor 4.5 kW (Screenshot_20261009_225249_Chrome.jpg)
s.name          = 'Mecwin PMSM Mid Motor 4.5kW';
s.type          = 'PMSM_mid';
s.rated_power_W = 4500;
s.rated_voltage_V = [48 60 72];
s.max_speed_rpm = 4500;
s.shaft         = 'spline';
s.cont_factor   = 0.65;      % EV peak rating -> continuous derate
s.source_file   = 'Screenshot_20261009_225249_Chrome.jpg';
end
