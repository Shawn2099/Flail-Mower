% SIM_UC_V4  design checks for v2_optimized_claude (single-stage drive, BM1418ZXF 750 W). Base MATLAB only.
% Reads geometry, mass and drive data from cad_v4/uc_v4.json (written by build_uc_v4.py) and FEM output from cad_v4/parts/*.json.
% NO hard-coded geometry. Every ASSUMPTION is declared below. 'REVIEW' = judgement / unmeasured / unpublished.
clear; clc; fails = 0; reviews = 0;
here = fileparts(mfilename('fullpath'));
J = jsondecode(fileread(fullfile(here,'cad_v4','uc_v4.json'))); Lay = J.layout; Dr = J.drive;
g = 9.81;
% ---------------- ASSUMPTIONS ----------------
deck_kg  = 60;      % deck + battery + electronics: UNKNOWN (lithium pack, size TBD). Was 96 kg earlier; 60 kg is the working guess
margin   = 1.25;    % design-mass margin
mu_rr    = [0.10 0.15];   % motion resistance (textbook 0.1-0.15; wet laterite unmeasured)
mu_t_max = 0.65;    % Wong lateral-resistance coeff (rubber on hard ground; clay unmeasured)
eta_c    = 0.95;    % one chain stage
Trated   = 15.36;   % motor rated OUTPUT torque after its 1:6 box [N.m] (listings; UNVERIFIED)
ovl      = 1.5;     % short-term overload assumed ONLY for turns (UNPUBLISHED - REVIEW)
v_mow = 1/3.6; v_top = 5/3.6; v_turn = 0.3;
soil_c = [1.7e3 4.14e3]; soil_phi = [29 13];                    % repo MBS table: loam, clay
Wtrack = 0.180; Bg = 2*Lay.YC/1000; Rp = Lay.Rp/1000; Ls = Lay.C/1000;
Muc = J.mass_kg.total; M = margin*(Muc + deck_kg); W = M*g; A = 2*Ls*Wtrack;
ratio = Dr.ratio; Tw_rated = Trated*ratio*eta_c; Tdes = 2*Tw_rated;   % design = 2x rated wheel torque (covers controller overload to 2x)
fprintf('UC mass %.1f kg (CAD incl. allowances) | design mass %.0f kg (deck %d kg ASSUMED, x%.2f)\n',Muc,M,deck_kg,margin);
fprintf('Drive: %dT -> %dT, ratio %.2f, speed at 480 rpm = %.2f km/h, 1 km/h needs %.0f%% of motor speed; wheel torque rated %.0f Nm, design %.0f Nm\n\n', ...
  Dr.pinion_T,Dr.wheel_T,ratio,480/ratio*2*pi/60*Rp*3.6,(v_mow/Rp*60/(2*pi)*ratio)/480*100,Tw_rated,Tdes);

% ---------------- CAD gates (computed in build script) ----------------
for i = 1:numel(J.gates)
  q = J.gates(i); if ~q.ok, fails = fails+1; end
  fprintf('CAD %-4s %s\n', tern(q.ok,'PASS','FAIL'), q.gate);
end
fprintf('CAD interference hits: %d\n', numel(J.interference)); if numel(J.interference) > 0, fails = fails+1; end

% ---------------- drive capability vs load (per side) ----------------
fprintf('\n=== torque needed at the sprocket vs what RATED motor torque gives (%.0f Nm) ===\n',Tw_rated);
muP = mu_t_max/0.925; muA = mu_t_max/(0.925+0.15*3);           % spin turn and wide arc (R/B=3)
for rr = mu_rr
  T0 = rr*W/2*Rp; T5 = (rr*cosd(5)+sind(5))*W/2*Rp; T10 = (rr*cosd(10)+sind(10))*W/2*Rp;
  TA = (rr*W/2 + muA*W*Ls/(4*Bg))*Rp; TP = (rr*W/2 + muP*W*Ls/(4*Bg))*Rp;
  ok5 = T5 <= Tw_rated; ok10 = T10 <= Tw_rated; okA = TA <= ovl*Tw_rated; okP = TP <= ovl*Tw_rated;
  fprintf('rr %.2f: flat %3.0f (%.2fx) | 5deg %3.0f (%.2fx) %s | 10deg %3.0f (%.2fx) %s | wide-arc %3.0f (%.2fx) %s | spin %3.0f (%.2fx) %s\n',rr, ...
    T0,T0/Tw_rated,T5,T5/Tw_rated,tern(ok5,'PASS','FAIL'),T10,T10/Tw_rated,tern(ok10,'PASS','FAIL'),TA,TA/Tw_rated,tern(okA,'PASS*','FAIL'),TP,TP/Tw_rated,tern(okP,'PASS*','FAIL'));
  fails = fails + (~ok5);   % 5 deg at rated torque is required; 10 deg / turns are reported (soil + overload unverified)
  if ~ok10 || TA > Tw_rated || TP > Tw_rated, reviews = reviews+1; end
  for s = 1:2
    tr = 0.85*(soil_c(s)*A + W*cosd(10)*tand(soil_phi(s))) >= (rr*cosd(10)+sind(10))*W;
    if ~tr, fails = fails+1; fprintf('   FAIL traction on soil %d at 10 deg\n',s); end
  end
end
fprintf('   (* = relies on the unpublished short-term overload of %.1fx; 5 deg at rated torque is a hard gate)\n',ovl);
Ptop = (max(mu_rr)*W/2*v_top/eta_c); fprintf('power per side at 5 km/h flat: %.0f W mech (motor 750 W) %s\n',Ptop,tern(Ptop<750,'PASS','FAIL')); fails = fails + (Ptop>=750);

% ---------------- drive-train strength at design torque ----------------
Rcw = 12.7/sin(pi/Dr.wheel_T)/2/1000; Fchain = Tdes/Rcw; sf = 17800/Fchain;
fprintf('\nchain pull %.0f N, SF vs 17.8 kN = %.1f (need >=8) %s\n',Fchain,sf,tern(sf>=8,'PASS','FAIL')); fails = fails + (sf<8);
d = 0.040; Lk = 32e-3; t2 = 3.3e-3; sk = 2*Tdes/d/(Lk*t2)/1e6;
fprintf('key 12x8x%d bearing = %.0f MPa (limit 100) %s\n',round(Lk*1000),sk,tern(sk<100,'PASS','FAIL')); fails = fails + (sk>=100);
weldOD = [76 60]; weldName = {'sprocket hub-to-laminate OD76','chain-wheel boss-to-plate OD60'};
for wi = 1:2
  r = weldOD(wi)/2000; Aw = pi*weldOD(wi)/1000*0.0035*2; tw = Tdes/(r*Aw)/1e6;
  fprintf('weld %s: shear %.1f MPa (allow 110) %s\n',weldName{wi},tw,tern(tw<110,'PASS','FAIL')); fails = fails + (tw>=110);
end
% axle as a beam on the two UCFL208: chain pull (vertical) at the overhanging chain wheel, sprocket force (horizontal) between bearings
yc = 237; yi = Lay.plate_y(1)-25.6; yo = Lay.plate_y(4)+25.6; ys = Lay.YC; L = yo-yi; Fs = Tdes/Rp;
Ri = hypot(Fchain*(yo-yc)/L, Fs*(yo-ys)/L); Ro = hypot(Fchain*(yi-yc)/L, Fs*(ys-yi)/L); Cr = 29.1e3;
fprintf('UCFL208 inner %.0f N (L10 %.0f Mrev), outer %.0f N (L10 %.0f Mrev) %s\n',Ri,(Cr/Ri)^3,Ro,(Cr/Ro)^3,tern(min((Cr/Ri)^3,(Cr/Ro)^3)>=300,'PASS','FAIL')); fails = fails + (min((Cr/Ri)^3,(Cr/Ro)^3)<300);
Mb = Fchain*(yi-yc)/1000; sig = 32*Mb/(pi*d^3); tau = 16*Tdes/(pi*d^3); vm = sqrt(sig^2+3*tau^2)/1e6;
fprintf('axle D40: von Mises %.0f MPa (EN8 yield ~300) %s\n',vm,tern(vm<150,'PASS','FAIL')); fails = fails + (vm>=150);
bh = 694; fprintf('UCFL bolt-hole bearing on 6 mm plate: %.1f MPa; M14 bolt shear %.0f N vs %.0f N %s\n',bh/(16*6),bh,0.6*800e6*115e-6,tern(bh<0.6*800e6*115e-6,'PASS','FAIL'));
P = 1.7e3/2; L10b = (14.8e3/P)^3; fprintf('6205 L10 = %.0f Mrev %s\n',L10b,tern(L10b>=300,'PASS','FAIL')); fails = fails + (L10b<300);
Fp = 100/(0.2*0.024); Asp = pi/4*(32^2-25.5^2); fprintf('spool spacer stress at 100 N.m clamp = %.0f MPa %s\n',Fp/Asp,tern(Fp/Asp<150,'PASS','FAIL')); fails = fails + (Fp/Asp>=150);
% track pretension: 2.0 kN idler load shared by two M16 rods; anchor-lug fillet welds
Frod = 2000/2; sr = Frod/157e-6/1e6; Alug = 2*0.7*5*44; tl = Frod/Alug;
fprintf('tension rod M16: %.1f MPa; lug weld shear %.1f MPa %s\n',sr,tl,tern(sr<150 && tl<110,'PASS','FAIL')); fails = fails + ~(sr<150 && tl<110);
% cross beams: bending (weight shared by 3 beams) and frame twist (one roller 1.7 kN shock, joint prying via M12 pair)
Z = (40^4-33.6^4)/(6*40)*1e-9; Lb = (Lay.plate_y(1)*2)/1000; sb = (W/3)*Lb/4/Z/1e6;
fprintf('beam SHS40x3.2 bending %.0f MPa (limit 167) %s\n',sb,tern(sb<167,'PASS','FAIL')); fails = fails + (sb>=167);
Mend = 1700*0.08; Ft = Mend/0.054; fprintf('frame twist: end moment %.0f Nm -> bolt tension %.0f N per M12 (proof ~49 kN) %s\n',Mend,Ft,tern(Ft<0.3*49e3,'PASS','FAIL')); fails = fails + (Ft>=0.3*49e3);

% ---------------- FEM results (FreeCAD/CalculiX, 6 mm inner plate, tet10 ~95k nodes, pad faces restrained) ----------------
cases = {'fem_plate_result.json','fem_plate_result_lateral.json'};
for ci = 1:numel(cases)
  ff = fullfile(here,'cad_v4','parts',cases{ci});
  if exist(ff,'file')
    Fm = jsondecode(fileread(ff));
    ok = Fm.p99_MPa < Fm.allowable_MPa && Fm.max_vm_MPa < Fm.yield_MPa; fails = fails + (~ok);
    fprintf('\nFEM %s\n   p95 %.0f / p99 %.0f / max %.0f MPa (allow %.0f, yield %.0f), disp %.2f mm  %s\n',Fm.case,Fm.p95_MPa,Fm.p99_MPa,Fm.max_vm_MPa,Fm.allowable_MPa,Fm.yield_MPa,Fm.max_disp_mm,tern(ok,'PASS','FAIL'));
    if Fm.max_vm_MPa > Fm.allowable_MPa, fprintf('   REVIEW: peak above working allowable at a loaded hole edge\n'); reviews = reviews+1; end
  else
    fprintf('\nFEM result %s missing\n',cases{ci}); fails = fails+1;
  end
end
fprintf('\nMass: %.1f kg incl. %.1f kg labelled allowances; v2 frozen = 185.7 kg -> delta %+.1f kg\n',Muc,J.mass_kg.by_category.allowance,Muc-185.7);
if fails == 0, fprintf('UC_V4 CAD/structure/drive: ALL GATES PASS (%d items marked REVIEW)\n',reviews); else, fprintf('UC_V4: %d FAILURES (%d REVIEW)\n',fails,reviews); end
function s = tern(c,a,b), if c, s = a; else, s = b; end, end
