function s = grass_light_maintained()
% GRASS_LIGHT_MAINTAINED  Operating condition: clean, known ground.
% Light fresh grass 2-3 in (50-75 mm), regularly mowed, no rocks/branches.
s.name              = 'Light maintained grass';
s.height_m          = [0.050 0.075];
s.ground            = 'clean_known_no_rocks';
% Specific cutting energy for light grass (J/m^2 of swath):
s.spec_energy_J_per_m2_nom = 800;
s.spec_energy_J_per_m2_range = [500 1500];  % use range for sensitivity
s.tip_speed_min_mps = 30;     % sharp edge minimum
s.tip_speed_blunt_mps = 35;   % blunt impact edges (per photos) need 35+ m/s
s.tip_speed_ok_mps  = [30 40];
s.note = 'No shock-load allowance needed; stone-strike clutch still recommended.';
end
