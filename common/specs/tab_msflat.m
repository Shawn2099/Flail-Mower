function s = tab_msflat(thickness_mm)
% TAB_MSFLAT  MS flat tab, IS 2062 E250. 6 mm for blade pairs, 8 mm for
% singles/triples. Call: tab_msflat(6) or tab_msflat(8).
if nargin < 1, thickness_mm = 6; end
s.name       = sprintf('MS flat tab 50x%.0f (E250)', thickness_mm);
s.width_m    = 0.050;
s.thick_m    = thickness_mm/1000;
s.height_m   = 0.040;
s.hole_dia_m = 0.0172;   % clearance for dia-17 pin
s.yield_MPa  = 250;
end
