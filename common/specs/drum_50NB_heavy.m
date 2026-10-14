function s = drum_50NB_heavy()
% DRUM_50NB_HEAVY  Optimum drum for blunt blades at 2200 rpm: ERW MS black
% pipe IS 1239, 50NB Heavy. Smallest standard pipe that reaches 35 m/s
% tip speed at ~2200 rpm with straight blades, keeping centrifugal loads
% and rotor weight down. 65NB is the roomier alternative (see drum_65NB_heavy).
s.name   = 'ERW pipe 50NB Heavy (IS 1239)';
s.OD_m   = 0.0603;
s.wall_m = 0.0054;
s.ID_m   = s.OD_m - 2*s.wall_m;
s.length_m = 0.500;
s.rho_kgm3 = 7850; s.E_Pa = 200e9; s.yield_MPa = 250;
s.mass_kg = pi/4*(s.OD_m^2 - s.ID_m^2)*s.length_m*s.rho_kgm3;  % ~3.7 kg
end
