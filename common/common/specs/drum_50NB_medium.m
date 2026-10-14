function s = drum_50NB_medium()
% DRUM_50NB_MEDIUM  Current optimum drum: ERW MS black pipe IS 1239, 50NB Medium
% (60.3 OD x 3.65 wall x 500). Lightest standard pipe passing all gates with 6 mm
% tabs (weld needs wall>=tab/2=3.0): tip>=35 with 3% droop, sag<=0.05, critical>=6000.
% Supersedes drum_50NB_heavy (kept as fallback). 65NB = roomy alternative.
s.name   = 'ERW pipe 50NB Medium (IS 1239)';
s.OD_m   = 0.0603;
s.wall_m = 0.00365;
s.ID_m   = s.OD_m - 2*s.wall_m;
s.length_m = 0.500;
s.rho_kgm3 = 7850; s.E_Pa = 200e9; s.yield_MPa = 250;
s.mass_kg = pi/4*(s.OD_m^2 - s.ID_m^2)*s.length_m*s.rho_kgm3;  % ~2.5 kg
end
