function s = blade_jtype_mulcher()
% BLADE_JTYPE_MULCHER  Meevin Agro J-type mulcher blade spec.
% Source image: "multure blade j type.jpg"
s.name              = 'Meevin Agro Mulcher Blade (J-Type)';
s.type              = 'j_flail';
s.material          = 'Boron Steel 30MnCrB5';
s.mass_kg           = 0.400;     % from datasheet image
s.length_overall_m  = 0.131;
s.width_m           = 0.0585;
s.head_width_m      = 0.045;
s.thickness_m       = 0.008;
s.hole_dia_m        = 0.017;
s.hardness_HRC      = [46 50];
s.bend_angle_deg    = 125;       % hook bend, mulches finer, draws more power
s.tip_radius_m      = 0.105;     % radial reach slightly less than overall (bend)
s.pivot_to_tip_m    = 0.105;     % radial reach slightly less than overall (bend)
s.pivot_to_cg_m     = 0.055;     % approx, refine by measurement
s.edge              = 'blunt impact edge, not razor sharp (per photos)';
s.source_file       = 'multure blade j type.jpg';
end
