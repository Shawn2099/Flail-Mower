function s = config_2J_opposing()
% CONFIG_2J_OPPOSING  The 2J program configuration (MVP straights untouched).
% 10 axial positions x 2 blades at 180 deg = 20 J singles, one per bolt.
s.name            = '2J opposing (20 J singles)';
s.blade_fn        = 'blade_jtype_mulcher';
s.nPos            = 10;
s.perPos          = 2;
s.nBlades         = 20;
s.xs_mm           = linspace(15, 485, 10);   % 15..485 mm, 52.2 pitch
s.base_angles_deg = (0:9)*36;                % per position; 2nd blade +180
s.rpm_work        = 2300;
s.rpm_cap         = 2500;
s.rpm_floor       = 2100;                    % below this tip <35 m/s
s.forward_mps     = 1.0;
end
