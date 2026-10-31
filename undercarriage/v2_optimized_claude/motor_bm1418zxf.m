% MOTOR_BM1418ZXF  drive calculation with the REAL motor (BM1418ZXF 750 W 48 V, in-built 1:6 gearbox), single chain stage. Base MATLAB.
% Motor facts (seller/maker listings, UNVERIFIED vs a datasheet): rated 750 W, 48 V, motor 2800 rpm, output 480 rpm (Kelly listing: 450 actual),
% rated OUTPUT torque 15.36 N.m, full-load 20 A, no-load 5 A, mass 7.12 kg (listings 3.0/7.12/10.66). Shaft/mounting/peak torque/IP: NOT PUBLISHED.
% Reads mass + geometry + drive from cad_v4/uc_v4.json (no hard-coded geometry). Choice of teeth: see opt_sprockets.m.
clear; clc;
here = fileparts(mfilename('fullpath'));
J = jsondecode(fileread(fullfile(here,'cad_v4','uc_v4.json'))); Lay = J.layout; Dr = J.drive;
g = 9.81; Rp = Lay.Rp/1000; Ls = Lay.C/1000; Bg = 2*Lay.YC/1000;
deck_kg = 60; margin = 1.25; M = margin*(J.mass_kg.total + deck_kg); W = M*g;    % deck/battery/electronics UNKNOWN: 60 kg working guess
mu_rr = [0.10 0.15]; mt = 0.65/0.925; eta_c = 0.95;                              % one chain stage
n_out = [480 450]; T_rated = 15.36; P_rated = 750; V = 48; I_full = 20; v_t = 5/3.6;
fprintf('Design mass %.0f kg (deck %d kg ASSUMED x%.2f), track sprocket %dT Rp %.4f m, flat run %.3f m, gauge %.2f m\n',M,deck_kg,margin,Lay.spr_teeth,Rp,Ls,Bg);
fprintf('Chain: %dT pinion -> %dT wheel, ratio %.3f, %d links, centre distance %.1f mm\n\n',Dr.pinion_T,Dr.wheel_T,Dr.ratio,Dr.chain_links,Dr.chain_C_mm);
r = Dr.ratio; Tw_rated = T_rated*r*eta_c;
fprintf('speed at 480 rpm: %.2f km/h (at 450 rpm: %.2f km/h); 1 km/h mowing needs %.0f%% of motor speed\n',n_out(1)/r*2*pi/60*Rp*3.6,n_out(2)/r*2*pi/60*Rp*3.6,(1/3.6/Rp*60/(2*pi)*r)/480*100);
fprintf('wheel torque at rated motor torque: %.1f Nm -> thrust %.0f N per side\n\n',Tw_rated,Tw_rated/Rp);

eff = P_rated/(V*I_full);                                      % 0.78, derived from the 750 W : 20 A listing
fprintf('=== per motor, load case: sprocket torque / motor output torque (%% of rated) / mech power / est. current ===\n');
for rr = mu_rr
  for th = [0 5 10]
    F = (rr*cosd(th)+sind(th))*W/2; Tw = F*Rp; Tm = Tw/(r*eta_c); P = F*v_t/eta_c;
    fprintf('rr %.2f %2d deg at 5 km/h: wheel %5.1f Nm | motor %5.2f Nm (%3.0f%%) | %4.0f W | %4.1f A\n',rr,th,Tw,Tm,100*Tm/T_rated,P,P/(V*eff));
  end
  Fm = F; %#ok<NASGU>
end
rr = max(mu_rr); Tturn = (rr*W/2 + mt*W*Ls/(4*Bg))*Rp; Tm = Tturn/(r*eta_c);
fprintf('spin turn (outer track): wheel %.0f Nm | motor out %.2f Nm (%.0f%% of rated) %s\n',Tturn,Tm,100*Tm/T_rated,tern(Tm<=T_rated,'within rated','needs overload (unpublished)'));
Rw = 12.7/sin(pi/Dr.wheel_T)/2/1000; Rpi = 12.7/sin(pi/Dr.pinion_T)/2/1000;
F1 = 2*T_rated/Rpi; F2 = 2*Tw_rated/Rw;
fprintf('chain pull at 2x rated torque: %.0f N (pinion) / %.0f N (wheel); SF vs 17.8 kN = %.1f %s\n',F1,F2,17800/max(F1,F2),tern(17800/max(F1,F2)>=8,'PASS','FAIL'));
Ihill = 2*((rr*cosd(10)+sind(10))*W/2*v_t/eta_c)/(V*eff); Iflat = 2*(rr*W/2*v_t/eta_c)/(V*eff);
fprintf('battery current (both drives) at 5 km/h: flat %.1f A, 10 deg %.1f A at 48 V; motor full-load rating 20 A each\n',Iflat,Ihill);
function s = tern(c,a,b), if c, s = a; else, s = b; end, end
