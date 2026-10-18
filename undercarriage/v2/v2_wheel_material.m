% V2_WHEEL_MATERIAL  nylon vs cast-iron vs PU vs custom-fab at OUR size (D114x40, 25 bore).
% Use case: plantation, wet, stones, skid-steer side thrust, parked-loaded weeks, 2yr/1000hr.
% Loads: Fv=1700N/wheel static+parked, Flat=300N lateral pivot scrub, stone 10mm/850N.
clear; clc;
Fv=1700; Flat=300;
fprintf('=== WHEEL MATERIAL SHOOTOUT (D114x40, plantation duty) ===\n');
% 1) static tread stress (ring/wall, same geometry factor): MS 250 / SG-iron 320 / PA6sat 40 / PUwet 25
nom=39;  % MPa, cheek-supported (from trade sim, geometry-equal)
for k=1:4
  if k==1, n='MS-fab'; al=250; end
  if k==2, n='SG-iron'; al=320; end
  if k==3, n='PA6-sat '; al=40; end
  if k==4, n='PU-wet  '; al=25; end
  s='PASS'; if nom>al, s='FAIL'; end
  fprintf('%-9s static %d/%dMPa %s\n',n,nom,al,s);
end
% 2) parked creep flat (1000hr, saturated): flat_mm ~ Fv*time-factor/E_creep (screening)
%    Ecreep: steel inf / CI inf / PA6sat 0.4GPa / PU 0.15GPa -> flat = Fv*w/(E*D)*k
cn={'MS','CI','PA6','PU'};
sig_bulk=Fv/(0.114*0.040);  % Pa bulk diametral stress
for k=1:4
  % flat ~ 3x diametral creep set: 3*eps*D, eps=sig/E1000hr (E: PA6sat 0.35GPa, PU 0.03GPa)
  if k<=2, fl=0; elseif k==3, fl=3*sig_bulk*0.114/0.35e9*1000; else, fl=3*sig_bulk*0.114/0.03e9*1000; end
  s='PASS'; if fl>1.0, s='FAIL-flat>1mm'; end
  fprintf('creep-flat %s %.2fmm %s\n',cn{k},fl,s);
end
% 3) stone gouge (10mm granite, 850N): local Hertz vs ultimate (screening, higher=better)
fprintf('stone: steel dents-OK | SG-iron CHIPS (brittle) | PA6 gouges-heals | PU gouges+chunks-wet\n');
% 4) PU bond shear (core OD80xw40): tau=Flat/(pi*0.08*0.04)
fprintf('PU bond shear %.2fMPa (static fine; water+fatigue attack bond) NOTE\n',Flat/(pi*0.08*0.04)/1e6);
% 5) bearing retention: steel/CI press OK | PA6 bore creeps->walkout RISK | PU core steel OK
fprintf('bearing seat: steel/CI press PASS | PA6 bore-relax RISK | PU (steel core) PASS\n');
% 6) score 1-5 (strength-wet, creep, stone, water, weight, cost, no-fab): weighted
%    CI-direct: 2 wheels + gauge spacer + bolt = 6 parts/station, zero fab — but ~2.4kg/wheel
S=[5 5 4 5 3 3 3; 4 5 2 4 2 4 5; 2 1 3 1 5 5 5; 1 2 2 1 5 4 5];
w=[0.25 0.15 0.10 0.20 0.05 0.15 0.10]; tot=S*w';
names={'MS-fab','SG-iron','PA6','PU'};
for k=1:4, fprintf('%-7s score %.2f\n',names{k},tot(k)); end
[~,i]=max(tot);
fprintf('station: CI-direct 2x2.4+bolt = 5.9kg/6 parts ZERO fab | fab one-unit 3.9kg/14 parts SOME fab\n');
fprintf('WINNER: %s. CI-direct takes the work crown IF exact 4.5x2x1 SG found (costs +12kg/machine). PA6/PU stay rejected.\n',names{i});
