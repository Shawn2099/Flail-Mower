function s = blade_straight_mulcher()
% BLADE_STRAIGHT_MULCHER  Meevin Agro straight mulcher blade spec.
% Source image: "multure blade straight type.jpg"
% Use: s = blade_straight_mulcher();  % then pass s into simulation
s.name              = 'Meevin Agro Mulcher Blade (Straight)';
s.type              = 'straight_flail';
s.material          = 'Boron Steel 30MnCrB5';
s.mass_kg           = 0.340;     % from datasheet image
s.length_overall_m  = 0.130;
s.width_m           = 0.058;     % cutting width per blade (along rotor axis)
s.head_width_m      = 0.045;
s.thickness_m       = 0.008;
s.hole_dia_m        = 0.017;
s.hardness_HRC      = [46 50];
s.bend_angle_deg    = 0;          % straight (0 = no hook)
s.tip_radius_m      = 0.108;     % = pivot reach for straight blades
% Geometry estimates (measure on real part to refine):
s.pivot_to_tip_m    = 0.108;     % hole-centre to tip, ~overall minus top margin
s.pivot_to_cg_m     = 0.055;     % approx, refine by balancing/weighing
s.edge              = 'blunt impact edge, not razor sharp (per photos)';
s.source_file       = 'multure blade straight type.jpg';
end
