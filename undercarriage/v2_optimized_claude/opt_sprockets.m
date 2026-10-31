% OPT_SPROCKETS  choose track-sprocket teeth zt, pinion zp (motor) and chain-wheel zw (axle) by constrained integer optimisation.
% Uses Global Optimization Toolbox ga (integer vars + nonlinear constraints) and cross-checks by exhaustive enumeration (exact for this small space).
% Geometry mirrors cad_v4/build_uc_v4.py (loop closure, axle height, wheel clearance). ASSUMPTIONS are declared below and editable.
clear; clc; rng(1);
% ---------------- fixed data ----------------
pitch=60; N=37; Ld=pitch*N;                 % ACETRAX 180x60x37 loop [mm]
lug=22; belt=12; RR=57.15; zr=lug+belt+RR;  % roller D114.3
R_in_i=109.55; R_pi=R_in_i+6;               % 8NB idler (belt-inner / pitch-line radius)
zi=lug+belt+R_in_i;
Trated=15.36; eta=0.95; n0=480;             % motor output torque [N.m], single chain stage, output rpm
g=9.81; M=301; W=M*g; rr=0.15; Wd=W/2;      % design mass per side (60 kg deck assumed, x1.25)
tipoff=2.1; plate_bottom=30; beam_x=-230; beam_half=20;
% ---------------- availability tables (ASSUMPTION: verified kit sizes score 1.0, other common sizes 0.6) ----------------
zw_all = 36:52; zp_all = 13:17;   % pinion >= 13T: smaller 428 pinions wear and surge the chain
zw_verified = [44 45 48 52]; zp_verified = [13 14];          % Apache RTR160 13/44-45, R15 V3 14/48, MT-15 14/52
avail_w = 0.6*ones(size(zw_all)); avail_w(ismember(zw_all,zw_verified)) = 1.0;
avail_p = 0.6*ones(size(zp_all)); avail_p(ismember(zp_all,[13 14 15 16])) = 0.85; avail_p(ismember(zp_all,zp_verified)) = 1.0;
% ---------------- model ----------------
model = @(zt,zp,zw) evalDesign(zt,zp,zw,pitch,Ld,R_in_i,R_pi,zi,RR,zr,Trated,eta,n0,Wd,rr,tipoff,plate_bottom,beam_x,beam_half);
% objective weights (editable)
w.speed=2.0; w.chord=0.4; w.mass=0.8; w.avail=1.5; w.clear=0.02; w.margin=3.0;
J = @(d,zt,zp,zw) w.speed*abs(d.v-5.0) + w.chord*d.chord + w.mass*((zw/50)^2*0.6+(zt/12)^2*0.4) ...
    + w.avail*(1-avail_p(zp_all==zp)*avail_w(zw_all==zw)) - w.clear*min(d.clear-plate_bottom,20) - w.margin*min(max(d.margin10-0.9,0),0.3);
% ---------------- exhaustive enumeration ----------------
rows = [];
for zt = 9:13
  for zp = zp_all
    for zw = zw_all
      d = model(zt,zp,zw);
      feas = d.v>=4.7 && d.v<=5.5 && d.clear>=plate_bottom && d.beamgap>=10 && d.rollerspan>=150 && d.margin10>=0.90 && d.chord<=4.1 && d.Rin_s>=100 && d.wrap>=120;
      rows = [rows; zt zp zw feas J(d,zt,zp,zw) d.v d.ratio d.margin10 d.clear d.chord d.Rin_s d.C d.beamgap]; %#ok<AGROW>
    end
  end
end
F = rows(rows(:,4)==1,:); [~,ix] = sort(F(:,5)); F = F(ix,:);
fprintf('Feasible designs: %d of %d. Top 10 by cost J (lower is better):\n',size(F,1),size(rows,1));
fprintf(' zt  zp  zw |     J | v km/h  ratio  marg10  wheel z  chord%%  R_in_s  flat run  beam gap\n');
for k = 1:min(10,size(F,1))
  fprintf('%3d %3d %3d | %5.2f | %6.2f %6.3f %7.3f %8.1f %7.2f %7.1f %8.1f %8.1f\n',F(k,1:3),F(k,5),F(k,6),F(k,7),F(k,8),F(k,9),F(k,10),F(k,11),F(k,12),F(k,13));
end
best = F(1,1:3);
% best among the VERIFIED kit pairs only (pinion 13/14 and wheel 44/45/48/52)
Fv = F(ismember(F(:,2),zp_verified) & ismember(F(:,3),zw_verified),:);
fprintf('\nBest with verified kit sprockets only: zt=%d zp=%d zw=%d (J %.2f, %.2f km/h, wheel z %.1f)\n',Fv(1,1:3),Fv(1,5),Fv(1,6),Fv(1,9));
% ---------------- integer GA with nonlinear constraints (Global Optimization Toolbox) ----------------
nonl = @(x) gaCons(x,model,plate_bottom);
obj  = @(x) J(model(round(x(1)),round(x(2)),round(x(3))),round(x(1)),round(x(2)),round(x(3)));
opts = optimoptions('ga','PopulationSize',80,'MaxGenerations',80,'Display','off','UseParallel',false);
[xg,fg] = ga(obj,3,[],[],[],[],[9 13 36],[13 17 52],nonl,[1 2 3],opts);
fprintf('\nga (integer, nonlinear constraints): zt=%d zp=%d zw=%d  J=%.2f  -> %s\n',xg,fg,tern(isequal(round(xg),best),'MATCHES enumeration optimum','differs from enumeration (enumeration is exact)'));
d = model(xg(1),xg(2),xg(3));
fprintf('  GA design: %.2f km/h, ratio %.3f, margin10 %.3f, wheel bottom %.1f mm, chordal %.2f %%, track bend R %.1f mm\n',d.v,d.ratio,d.margin10,d.clear,d.chord,d.Rin_s);

% ---------------- local functions ----------------
function d = evalDesign(zt,zp,zw,pitch,Ld,R_in_i,R_pi,zi,RR,zr,Trated,eta,n0,Wd,rr,tipoff,plate_bottom,beam_x,beam_half) %#ok<INUSL>
  Rp = pitch/(2*sind(180/zt));              % track sprocket pitch radius [mm]
  d.Rin_s = Rp-6; zs = 34+d.Rin_s;          % belt-inner radius, axle height (lug+belt+R_in)
  dr = R_pi-Rp; C = 800;
  for k=1:8, dd=hypot(C,dr); b=asin(dr/dd); C=(Ld-pi*(R_pi+Rp)-2*b*dr)/2; end
  d.C = C; xs = -C/2; xi = C/2;
  d.chord = 100*(1-cosd(180/zt));           % chordal speed variation of the track sprocket [%]
  d.ratio = zw/zp; d.v = n0/d.ratio*2*pi/60*(Rp/1000)*3.6;
  Tw = Trated*d.ratio*eta;                  % [N.m]
  F = Tw/(Rp/1000); Freq = (rr*cosd(10)+sind(10))*Wd; d.margin10 = F/Freq;
  Rw = 12.7/(2*sin(pi/zw)) + tipoff; d.clear = zs - Rw;           % wheel bottom above ground
  d.beamgap = (beam_x-beam_half) - (xs + 12.7/(2*sin(pi/zw)) + 4);
  f = xs + sqrt((Rp*1.005+RR+30)^2-(zs-zr)^2); l = xi - sqrt((R_in_i+RR+30)^2-(zi-zr)^2); d.rollerspan = (l-f)/2;
  Rpin = 12.7/(2*sin(pi/zp)); Cc = Rpin + 12.7/(2*sin(pi/zw)) + 70;
  d.wrap = 180 - 2*asind((12.7/(2*sin(pi/zw)) - Rpin)/Cc);        % wrap on the pinion [deg]
end
function [c,ceq] = gaCons(x,model,plate_bottom)
  d = model(round(x(1)),round(x(2)),round(x(3)));
  c = [4.7-d.v; d.v-5.5; plate_bottom-d.clear; 10-d.beamgap; 150-d.rollerspan; 0.90-d.margin10; d.chord-4.1; 100-d.Rin_s; 120-d.wrap];
  ceq = [];
end
function s = tern(c,a,b), if c, s=a; else, s=b; end, end
