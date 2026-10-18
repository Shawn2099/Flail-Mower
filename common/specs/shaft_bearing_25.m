function s = shaft_bearing_25()
% SHAFT_BEARING_25  Through-shaft + plummer bearings (sized by standard
% sizes and sealing, NOT by strength - rotor torque is only ~2.5 Nm).
s.shaft_dia_m = 0.025;
s.shaft_mat   = 'EN8/C45 bright';
s.shaft_len_m = 0.700;
s.span_m      = 0.600;      % bearing to bearing
s.bearing     = 'UCP205 sealed';
s.C_dyn_kN    = 14;         % dynamic rating per bearing
end
