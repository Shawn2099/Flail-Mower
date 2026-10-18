function s = blade_hammer()
% BLADE_HAMMER  Meevin Agro hammer blade spec.
% Source image: "hammer blade.jpg"
% NOTE: mass and thickness NOT stated on datasheet -> MUST weigh it.
s.name              = 'Meevin Agro Hammer Blade';
s.type              = 'hammer';
s.material          = 'Boron Steel 30MnCrB5';
s.mass_kg           = 1.050;     % USER MEASURED
s.length_overall_m  = NaN;       % not on drawing (only R110 given) - measure if needed
s.bend_angle_deg    = 0;         % hammer (0 = no hook)
s.tip_radius_m      = 0.110;     % R110.0 pivot-centre to tip (on drawing)
s.width_m           = 0.130;     % cutting width per blade (covers 500mm in 4)
s.head_width_m      = 0.040;
s.thickness_m       = NaN;       % <-- measure with caliper
s.hole_dia_m        = 0.01625;
s.hardness_HRC      = [47 51];
s.pivot_to_tip_m    = 0.110;
s.pivot_to_cg_m     = 0.060;     % approx, refine by measurement
s.edge              = 'blunt impact edge, not razor sharp (per photos)';
s.source_file       = 'hammer blade.jpg';
end
