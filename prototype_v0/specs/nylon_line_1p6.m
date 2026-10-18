function s = nylon_line_1p6()
% NYLON_LINE_1P6  1.6 mm round nylon trimmer line + the v0 cutting-head geometry.
% Line CONFIRMED: FASTRIM "Plastic Round/Grass Cutter/Nylon Trimmer line", 1.6 mm
% (0.065 in), 75 m spool, blue - Amazon.in B077Y1M12W. Round cross-section, nylon
% (exact grade not published - PA6 nominal properties used).
% Head: our printed D50 zip-tie hub (cad/gen_adapter_775_ziptie.py); line exits at r25.
% Units SI (m) unless suffixed _mm.
s.name   = '1.6 mm round nylon trimmer line (FASTRIM 75 m, blue)';
s.source = 'Amazon.in B077Y1M12W';
s.spool_m = 75;             % spool length (m)

% Line material (PA6 nominal - exact grade unpublished)
s.d_line_m      = 1.6e-3;   % line diameter (0.065 in) - CONFIRMED
s.rho_kg_m3     = 1140;     % PA6 nominal density
s.UTS_new_Pa    = 75e6;     % virgin round line [EST]
s.UTS_design_Pa = 40e6;     % aged / wet / knotted / abraded design value [EST]
s.A_line_m2     = pi/4*s.d_line_m^2;
s.m_per_m_kg    = s.rho_kg_m3*s.A_line_m2;   % kg per m (~2.29 g/m -> 75 m spool ~172 g)

% Cutting head = our printed D50 zip-tie hub (line exits at the hub OD)
s.D_hub_m   = 50e-3;        % hub OD where the line exits
s.r0_m      = s.D_hub_m/2;  % line root radius = 25 mm
s.L_line_m  = 75e-3;        % exposed line per side -> Rtip 100 mm, swath 200 mm
s.R_tip_m   = s.r0_m + s.L_line_m;
s.D_cut_m   = 2*s.R_tip_m;  % swath diameter = 200 mm
s.n_lines   = 2;            % opposed lines (2 zip ties, 180 deg apart)

% Tip-speed gates (repo convention)
s.tip_speed_clean_mps = 50;  % >= this for a clean cut
s.tip_speed_blunt_mps = 35;  % repo blunt floor (below clean = tears/ragged)

s.status = 'line confirmed; head = printed D50 hub; trim to 75 mm/side';
end
