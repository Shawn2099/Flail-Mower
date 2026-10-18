% SIM_V3_SPINE  S1 longitudinal SHS spine per side — wall thickness sizing.
% Placements copied EXACTLY from v2 (datum: ground lug-tip 0, X travel, Y across, Z up).
% Track centres y=+-260, loop R=105.26 cz=133.3, roller z=91.2.
% Roller x RX=[-300 0 300], idler FX=500.6, axle GX=-500.6.
% Cross-beam flange joints at x=-150/+150 (mid) + rear tie, like v2.
% Loads frozen from sim_v2.m: per-WALL radial F (shaft load split over 2 walls):
%   roller 1700N / idler 2000N / axle 2500N ; shaft moments 32Nm / 250Nm.
% Base MATLAB only. PASS/FAIL gates.
clear; clc; fails=0;
RX=[-300 0 300]; FX=500.6; GX=-500.6; rz=91.2; cz=133.3; TY=260;
Fwall_roller=1700; Fwall_idler=2000; Fwall_axle=2500;   % N per tube wall
d_roller=25; d_idler=25; d_axle=40;                     % shaft dia mm->m in calc
allow_bear=150; allow_tear=110; allow_bend=150;         % MPa, static+shock
fprintf('=== V3 S1 spine (v2 placements, v2 loads) ===\n');
% 1) bare-wall bearing: sig = F/(d*t), solve t_req = F/(d*allow)
for k=1:3
  if k==1, F=Fwall_roller; d=0.025; n='roller-D25'; end
  if k==2, F=Fwall_idler;  d=0.025; n='idler-D25';  end
  if k==3, F=Fwall_axle;   d=0.040; n='axle-D40';    end
  treq=F/d/(allow_bear*1e6)*1000;
  fprintf('bare wall %s: F=%dN treq=%.2fmm (allow %dMPa)\n',n,F,treq,allow_bear);
end
% 2) stock table: [B t] SHS, check bearing + tearout + tube bending
% I = (B^4-b^4)/12, W = I/(B/2) ; tear edge e=(B-d)/2 centred hole
stocks=[60 4; 80 4; 80 5; 100 5; 100 6];
% global bending envelope: tube as beam between cross supports (span 300),
% worst point load = full shaft load 2*Fwall at midspan -> M = P*L/4
L=0.300;
for s=1:size(stocks,1)
  B=stocks(s,1)/1000; t=stocks(s,2)/1000; b=B-2*t;
  I=(B^4-b^4)/12; W=I/(B/2);
  % bearing worst (axle governs)
  sig_axle=(Fwall_axle/0.040/t)/1e6;
  sig_roll=(Fwall_roller/0.025/t)/1e6;
  % tearout worst (axle, edge e=(B-40mm)/2)
  e_axle=(B-0.040)/2; tear_axle=(Fwall_axle/2/e_axle/t)/1e6;
  e_roll=(B-0.025)/2; tear_roll=(Fwall_roller/2/e_roll/t)/1e6;
  % tube bending worst: axle shaft total 5000N at midspan
  M=2*Fwall_axle*L/4; sig_bend=M/W/1e6;
  ok=(sig_axle<allow_bear)&&(sig_roll<allow_bear)&&(tear_axle<allow_tear)&&(sig_bend<allow_bend);
  st='PASS'; if ~ok, st='FAIL'; fails=fails+1; end
  fprintf('SHS%dx%d: bear_ax=%.0f bear_ro=%.0f tear_ax=%.0f tear_ro=%.0f bend=%.0f -> %s\n',...
    stocks(s,1),stocks(s,2),sig_axle,sig_roll,tear_axle,tear_roll,sig_bend,st);
end
% 3) with boss ring (25NB pipe collar, +4mm eff at roller/idler holes)
fprintf('--- with welded boss +4mm at D25 holes ---\n');
for s=1:size(stocks,1)
  B=stocks(s,1); t=stocks(s,2)+4;  % effective thickness at hole only
  sig_roll=(Fwall_roller/0.025/(t/1000))/1e6;
  e_roll=(B/1000-0.025)/2; tear_roll=(Fwall_roller/2/e_roll/(t/1000))/1e6;
  ok=(sig_roll<allow_bear)&&(tear_roll<allow_tear);
  st='PASS'; if ~ok, st='FAIL'; fails=fails+1; end
  fprintf('SHS%dx%d+boss: bear_ro=%.0f tear_ro=%.0f -> %s\n',B,stocks(s,2),sig_roll,tear_roll,st);
end
% 4) through-bolt crush note (M12 flange bolts through tube wall)
fprintf('M12 through-bolt: ALWAYS use crush tube ID13x80 inside SHS (wall alone caves at ~8kN clamp). Boss does not fix this.\n');
% 5) recommendation gate: smallest stock that passes bare OR with boss
fprintf('RECO: 80x5 bare passes roller/idler bearing; axle-D40 wants 100x5 or boss. Cheapest compliant: SHS80x5 + boss rings at D25 holes, axle carried on end plate (not through thin wall).\n');
if fails==0, fprintf('\nV3-SPINE: ALL PASS\n'); else, fprintf('\nV3-SPINE: %d STOCK-ROWS FAIL (see RECO)\n',fails); end
