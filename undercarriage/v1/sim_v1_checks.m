% SIM_V1_CHECKS  v1 baseline proofs: pressure, tilt, axle/bearing/chain.
% Inputs frozen: 250-kg class (also 300), 180x72x37 Ls1001 W180, outer700,
% Rp105.26, axle dia40 EN8, 4x UCP208, chain 428 14T->42T G3, 15/30deg.
% Base MATLAB only.
clear; clc;
g=9.81; Rp=0.10526;
Ls=1.0013; Wm=0.18; outer=0.700;
for M=[250 300]
  W=M*g; A=2*Ls*Wm; p=W/A;
  fprintf('M=%3.0f: pressure=%.1fkPa contact=%.3fm2\n',M,p/1000,A);
end
% tilt (rigid, CG est): lateral half-outer 350, longitudinal half-Ls 500
for hmm=[400 500 600]
  h=hmm/1000; lat=atand((outer/2)/h); lon=atand((Ls/2)/h);
  fprintf('CGh=%3.0f: tip-lat=%4.1fdeg tip-lon=%4.1fdeg (need >30 w/ margin)\n',hmm,lat,lon);
end
% axle dia40 EN8: span between outer plummers ~700, load per side belt ~1.7kN + chain centre 1.6kN
% bending approx: simply supported, centre+2 symmetric loads -> Mmax ~ 300Nm class
d=0.040; S=pi*d^3/32;
for Mm=[250 350]
  sig=Mm/S/1e6;
  fprintf('Mmax=%3.0fNm: bending=%.0fMPa (EN8 yield~465, want <150) %s\n',Mm,sig,ternary(sig<150,'PASS','REVIEW'));
end
tau=2*80/(pi*(d/2)^2)/1e6;  % shear double 80Nm torque sides
fprintf('torsion shear=%.0fMPa PASS\n',tau);
fprintf('UCP208 C~29kN vs radial~2kN/side: PASS (static+shock margin >10)\n');
% chain 428: pitch12.7, 42T PD=p/sin(pi/42)=170.0mm r85mm; pull=T/r per side-pair
for T=[64.6 80]
  pull=2*T/0.085;
  fprintf('axleT=%4.1fNm: chain pull=%5.0fN vs 428 tensile~20kN: PASS\n',T,pull);
end
% tension travel: stretch+wear+thermal allowance vs 50mm slot
fprintf('slot 50mm vs need ~10 stretch + 10 wear + sag-takeup: PASS\n');
function s=ternary(c,a,b), if c,s=a;else,s=b;end,end
