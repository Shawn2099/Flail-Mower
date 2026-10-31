% V2_TRIAL1_LEVERS  How much each design/operating lever cuts the worst-case (wet, pivot) wheel torque. Base MATLAB.
% Pivot moment Mr = mu_t*W*Ls/4 (Wong), per-side force = Mr/gauge. Resistance model as v2_trial1_drive.m.
clear; clc; g=9.81; Rp=0.10526; Wm=0.18; Fmow=100; s=struct('n',0.5,'kc',13.19,'kp',692.15,'f',0.08);
function T=tw(M,Ls,gauge,mu,arc,s,Rp,Wm,Fm)
  W=M*9.81; A=2*Ls*Wm; keq=s.kc/Wm+s.kp; p=W/A*1e-3; z=(p/keq)^(1/s.n);
  Rc=2*Wm*Ls*keq*z^(s.n+1)/(s.n+1)*1e3;
  T=((Rc+s.f*W+Fm)/2)*Rp + arc*mu*W*Ls/4/gauge*Rp; end
base=tw(282,1.0013,0.52,0.6,1.0,s,Rp,Wm,Fmow);
L={'Base: pivot, 282 kg, L1.0, gauge .52, mu .6', 282,1.0013,0.52,0.6,1.0;
   'Wide arcs only (turn load ~0.3x)',            282,1.0013,0.52,0.6,0.3;
   'Weight cut 282->262 kg (WEIGHT_EFF)',         262,1.0013,0.52,0.6,1.0;
   'Lighter still 282->240 kg',                   240,1.0013,0.52,0.6,1.0;
   'Gauge .52 -> .60 m',                          282,1.0013,0.60,0.6,1.0;
   'Contact length 1.0 -> 0.8 m (redesign)',      282,0.80,  0.52,0.6,1.0;
   'Real mu_t 0.45 (grass, measure it)',          282,1.0013,0.52,0.45,1.0;
   '262 kg + wide arcs',                          262,1.0013,0.52,0.6,0.3;
   '262 kg + gauge .60 + pivot',                  262,1.0013,0.60,0.6,1.0};
fprintf('%-46s %8s %7s\n','lever','wheel Nm','vs base');
for i=1:size(L,1)
  T=tw(L{i,2},L{i,3},L{i,4},L{i,5},L{i,6},s,Rp,Wm,Fmow);
  fprintf('%-46s %8.1f %6.0f%%\n',L{i,1},T,100*T/base);
end
% what that does to motor choice: 1418ZXF 500W (rated 10 Nm, cap 15, chain 6), 8T pinion
Tm=@(T) T/(6*0.95);
for i=[1 2 3 5 7 8 9]
  T=tw(L{i,2},L{i,3},L{i,4},L{i,5},L{i,6},s,Rp,Wm,Fmow);
  fprintf('500W 1418ZXF: %-40s motor %.1f Nm = %.2fx rated, cap margin %.2f\n',L{i,1},Tm(T),Tm(T)/10,15/Tm(T));
end
% power-based sizing: pivot power at track speed 0.3 m/s
fprintf('\npivot mech power (both sides) at 0.3 m/s: base %.0f W ; at 0.15 m/s %.0f W (torque same)\n',2*base*0.3/Rp,2*base*0.15/Rp);
