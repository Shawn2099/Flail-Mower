function s = pin_EN8(dia_mm)
% PIN_EN8  EN8 bright-steel rotor pin, R-clip retained.
% Call: pin_EN8(17) for mulcher blades, pin_EN8(16) for hammer.
% Allowances are fatigue-based and conservative.
if nargin < 1, dia_mm = 17; end
s.name            = sprintf('EN8 pin dia-%.0f', dia_mm);
s.dia_m           = dia_mm/1000;
s.area_m2         = pi*s.dia_m^2/4;
s.Z_m3            = pi*s.dia_m^3/32;
s.shear_allow_MPa   = 150;
s.bending_allow_MPa = 180;
end
