% SIM_DRIVE_CHAIN  pick 1 vs 1.2kW + chain ratio for undercarriage duty.
% Duty (INPUTS.md 2026-10-13): 250-kg class, 15deg work sustained, 30deg burst,
% light mowed grass on coffee-estate loam (sandy-loam mineral params interim),
% Rp = 105.26mm (72z9 exact), vtop >= 1.5 m/s.
% Convention (same as sim_motor_track_4combo): burst = stall*G*0.95 at axle,
% cont = (P_rated/rated_w)*G*0.95. Stall figures are nameplate burst anchors.
% Base MATLAB only.
clear; clc;
addpath('C:\Users\malliath\Desktop\matlab\common\specs');
m1k = motor_Mecwin_BLDC_1p0kW(); m2k = motor_Mecwin_BLDC_1p2kW();
g = 9.81; Rp = 0.10526; eta_g = 0.95; eta_d = 0.85;
M = 250; W = M*g;
% soil: sandy loam (MBS Table 4) as interim for estate loam+mulch
Wm = 0.18; P = 0.072; N = 37; Ld = P*N; R = Rp;
Ls = (Ld-2*pi*R)/2; A = 2*Ls*Wm;
kc = 5.3e3; kphi = 1515e3; sn = 0.7; coh = 1.7e3; phi = 29;
keq = kc/Wm + kphi;
Mots = {m1k, m2k}; mnames = {'1kW','1.2kW'};
Gs = [2 2.5 3 3.5 4 5 6 8 10];
fprintf('=== chain pick M=250 Rp=105.26 Ls=%.0fmm A=%.3fm2 ===\n', Ls*1000, A);
for mi = 1:2
  Mo = Mots{mi};
  Tc_b = Mo.stall_torque_Nm;
  Tc_c = Mo.rated_power_W/(Mo.rated_speed_rpm*2*pi/60);
  fprintf('\n-- %s stall=%.0f cont=%.2fNm rated=%drpm max=%drpm --\n', ...
    mnames{mi}, Tc_b, Tc_c, Mo.rated_speed_rpm, Mo.max_speed_rpm);
  for G = Gs
    Twb = Tc_b*G*eta_g; Twc = Tc_c*G*eta_g;
    vtop = (Mo.max_speed_rpm/G)*(2*pi/60)*Rp;
    % demand per side at 15 and 30 deg (level-Rc approx, slope-corrected traction separate)
    for th = [15 30]
      p = W*cosd(th)/A; z = (p/keq)^(1/sn);
      Rc = 2*(Wm*Ls*keq*z^(sn+1)/(sn+1));
      dem_axle = (W*sind(th)+Rc)/2*Rp;   % Nm per track at axle
      dem_mot_b = dem_axle/(G*eta_g);
      ok_b = dem_axle <= Twb; ok_c = dem_axle <= Twc;
      Pdem = (W*sind(th)+Rc)*1.0/eta_d;   % total W at 1 m/s
      if th == 15
        fprintf('G=%4.1f vtop=%3.1f Twb=%5.1f Twc=%5.1f | th15 axle=%5.1fNm mot=%5.2f %s/%s P1m/s=%4.0fW\n', ...
          G, vtop, Twb, Twc, dem_axle, dem_mot_b, ...
          ternary(ok_b,'Bok','Bno'), ternary(ok_c,'Cok','Cno'), Pdem);
      else
        fprintf('G=%4.1f vtop=%3.1f Twb=%5.1f Twc=%5.1f | th30 axle=%5.1fNm mot=%5.2f %s/%s\n', ...
          G, vtop, Twb, Twc, dem_axle, dem_mot_b, ...
          ternary(ok_b,'Bok','Bno'), ternary(ok_c,'Cok','Cno'));
      end
    end
  end
end
fprintf(['note: B=Burst(stall) short climbs; C=Continuous(rated) sustained.\n' ...
  'want: 15deg Cok + 30deg Bok, vtop>=1.5, P@1m/s within 2x rated.\n']);
function s = ternary(c,a,b), if c, s=a; else, s=b; end, end
