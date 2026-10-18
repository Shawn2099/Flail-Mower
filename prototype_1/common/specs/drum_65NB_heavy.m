function s = drum_65NB_heavy()
% DRUM_65NB_HEAVY  Recommended drum: ERW MS black pipe IS 1239, 65NB Heavy.
% Stocked by all Indian steel dealers (Tata/Jindal). 5.4 mm wall takes
% tab weld heat without burn-through.
s.name   = 'ERW pipe 65NB Heavy (IS 1239)';
s.OD_m   = 0.0761;
s.wall_m = 0.0054;
s.ID_m   = s.OD_m - 2*s.wall_m;
s.length_m = 0.500;
s.rho_kgm3 = 7850; s.E_Pa = 200e9; s.yield_MPa = 250;
s.mass_kg = pi/4*(s.OD_m^2 - s.ID_m^2)*s.length_m*s.rho_kgm3;  % ~4.7 kg
end
