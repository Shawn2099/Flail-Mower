%% sim_pattern_optimize.m
% PATTERN OPTIMIZATION for J blades on the 500 mm drum. Families:
%   A: single helix (1/station)   B: opposed pairs (2/station at 180 deg)
%   C: triples (3/station at 120 deg)
% Gates: coverage 100%% | residual imbalance ~0 | NO fin collision |
%        pin<=180 MPa | tip>=35. Ranked: smoothness first, power as cost.
% Base MATLAB only.
clear; clc; close all;

W = 0.500; Es = 800; v = 1.0; rpmJ = 2300; omJ = rpmJ*2*pi/60;
pin_r = 0.03015 + 0.020; Wref = 400; eff = 0.92*0.88;
mJ = 0.400; rJ = 0.105; cgJ = 0.055; BW = 58.5;
Rcg = pin_r + cgJ; Rcut = pin_r + rJ;
Fc1 = mJ*(2500*2*pi/60)^2*Rcg;                    % per-blade @cap
sig1 = Fc1*0.014/(pi*0.017^3/32)/1e6;             % single-bolt bending
tip = omJ*Rcut;

% candidates: {name, nPos, perPos, phase offsets}
CN = {'A-8','A-10','A-12','B-5pos','B-8pos','B-10pos','C-4pos','C-6pos'};
NPOS = [8 10 12 5 8 10 4 6];
NPP  = [1 1 1 2 2 2 3 3];
fprintf('\n=== PATTERN SEARCH (J blades, 2300 rpm) ===\n');
fprintf('pattern   blades cover imbal finClash minGap smooth powerW verdict\n');
best = Inf; bw = '';
bwA = ''; bestA = Inf;   % singles-only champion (A family = indices 1..3)
for i = 1:numel(CN)
    m = NPOS(i); q = NPP(i); N = m*q;
    xs = linspace(15, 485, m);
    th = [];
    for k = 1:m
        base = (k-1)*360/m;
        off = (0:q-1)*360/q;
        th = [th, base+off]; %#ok<AGROW>
    end
    sp = 470/max(m-1,1); cover = (BW >= sp*1.1);
    imb = abs(sum(exp(1i*deg2rad(th))))/N;         % residual fraction
    % fin collision: adjacent-x stations need dx>=50 OR tangential sep>=16 at r=50
    dth = 360/m; sep = 50*dth*pi/180;
    clash = (sp < 50) && (sep < 16);
    gaps = sort(mod(diff(sort(mod(th,360))),360)); gaps = [gaps, 360-sum(gaps)];
    mg = min(gaps(gaps>0.5));
    Pw = Wref*(rpmJ/3000)^3*(N/10)*1.3;
    Ps = Es*1.2*W*v + Pw;
    feas = cover && imb<0.05 && ~clash && sig1<=180 && tip>=35;
    if feas, vd='FEASIBLE'; else, vd='out'; end
    if cover, ck='OK  '; else, ck='GAP '; end
    if clash, fh='HIT '; else, fh='NO  '; end
    fprintf('%-8s %3d    %s    %.2f  %s      %4.0fdeg  %3.0fW  %s\n', CN{i}, N, ...
        ck, imb, fh, mg, Ps, vd);
    if feas
        score = mg*-1 + Ps/100;   % smoothness first (bigger min-gap wins), power cost
        if score<best, best=score; bw=CN{i}; end
        if i<=3 && (isempty(bwA)||score<bestA), bestA=score; bwA=CN{i}; end
    end
end
fprintf('\nWINNER overall: %s. Winner under SINGLES-ONLY constraint: %s.\n', bw, bwA);
fprintf('Note: B-10pos angle SET = every 18 deg (same as 20 singles) but only B is weldable:\n');
fprintf('20 single fins at 24.7 pitch collide (fin 50 wide); paired fins share stations.\n');
