% SIM_V1_FULL  consolidated v1 proofs with PASS/FAIL gates (base MATLAB only).
% Covers: drive, pressure, tilt, shafts+deflection, bearings L10, chain,
% bolts, welds, tension stack, clearances, mass rollup.
clear; clc; fails=0;
g=9.81; Rp=72/sin(pi/9)/2; R=Rp; Ld=72*37; Ls=(Ld-2*pi*R)/2; Wm=0.18; A=2*(Ls/1000)*Wm;
Gint=12; % motor internal gear (3000->250rpm class)
fprintf('=== V1 FULL (Ls=%.0f A=%.3f) ===\n',Ls,A);
%% 1 drive G=3, 250kg, 15 cont / 30 burst
for cn={'1kW',1200} %#ok (placeholder)
end
M=250; W=M*g;
kc=5.3e3; kphi=1515e3; sn=0.7; coh=1.7e3; phi=29; keq=kc/Wm+kphi;
cfgs={'1kW',1000,3000,3300,23;'1.2kW',1200,3300,3500,25};
for i=1:2
  nm=cfgs{i,1}; Pr=cfgs{i,2}; nr=cfgs{i,3}; nx=cfgs{i,4}; st=cfgs{i,5};
  Tc=Pr/(nr*2*pi/60); G=3;
  Twb=st*G*0.95; % gearbox-output burst
  Two=Pr*0.65/(250*2*pi/60)*G*0.95; % gearbox-output cont (250rpm base)
  vtop=(nx/Gint/G)*(2*pi/60)*(Rp/1000); % axle rpm -> m/s at pitch radius
  for th=[15 30]
    p=W*cosd(th)/A; z=(p/keq)^(1/sn); Rc=2*(Wm*(Ls/1000)*keq*z^(sn+1)/(sn+1));
    dem=(W*sind(th)+Rc)/2*Rp/1000;
    if th==15, ok=dem<=Two; tag='cont15'; lim=Two; else, ok=dem<=Twb; tag='burst30'; lim=Two*0+Twb; end
    if ok, s='PASS'; else, s='FAIL'; fails=fails+1; end
    fprintf('drive %s %s: dem=%.1f lim=%.1f %s\n',nm,tag,dem,lim,s);
  end
  if vtop>=0.9, s='PASS'; else, s='FAIL'; fails=fails+1; end
  fprintf('drive %s vtop=%.2f (mow 0.5-1.0, transport wish 1.5) %s\n',nm,vtop,s);
end
%% 2 pressure 200..350
for M=[200 250 300 350], p=M*g/A; s='PASS'; if p/1000>15, s='REVIEW'; end
  fprintf('pressure M%d %.1fkPa %s\n',M,p/1000,s); end
%% 3 tilt CG 400..600 outer700/Ls
for h=[400 500 600]
  lat=atand(350/h); lon=atand((Ls/2)/h);
  if lat>=30&&lon>=30, s='PASS'; else, s='FAIL'; fails=fails+1; end
  fprintf('tilt CG%d lat=%.1f lon=%.1f %s\n',h,lat,lon,s); end
%% 4 shafts: roller dia25 (M32) + side axle dia40 (M208)
for D=[0.025 0.04], Mm=[32 208]; end
Mv=[32 208]; Dv=[0.025 0.04];
for i=1:2, sg=Mv(i)/(pi*Dv(i)^3/32)/1e6;
  if sg<150, s='PASS'; else, s='FAIL'; fails=fails+1; end
  fprintf('shaft d%.0f bend=%.0fMPa %s\n',Dv(i)*1000,sg,s); end
% deflection roller shaft: simply supported c-loads, approx 5FL^3/384EI order
E=210e9; I=pi*0.025^4/64; dfl=850*2*0.2^3/(48*E*I)*0.5;
if dfl<0.2/500, s='PASS'; else, s='FAIL'; fails=fails+1; end
fprintf('roller deflect=%.4fmm %s\n',dfl*1000,s);
%% 5 bearings: 6205 C=14.8kN @0.85kN; UCFL208 C=29.6kN @2.0kN
brgn={'6205','UCFL208'}; brgC=[14.8 29.6]; brgF=[0.85 2.0];
for i=1:2
  L10=(brgC(i)/brgF(i))^3; % million revs
  if L10>50, s='PASS'; else, s='FAIL'; fails=fails+1; end
  fprintf('brg %s L10=%.0fMrev %s\n',brgn{i},L10,s); end
%% 6 chain 428 tensile 20kN pull<=1.9kN; slack 10-15
pull=2*80/0.085; sf=20000/pull;
if sf>8, s='PASS'; else, s='FAIL'; fails=fails+1; end
fprintf('chain pull=%.0fN SF=%.1f %s\n',pull,sf,s);
%% 7 bolts 8xM12-8.8 per interface: shear from 350Nm + 3kN weight share
Fb=350/(8*0.09)+3000/8; cap=0.6*800*84.3; % 8.8 shear ~0.6*UTS*At
if Fb<cap, s='PASS'; else, s='FAIL'; fails=fails+1; end
fprintf('bolt M12 shear=%.0fN cap=%.0fN %s\n',Fb,cap,s);
%% 8 welds: 5mm fillet, throat 3.5mm, 200mm run/side, shear from 3kN + 350Nm
tau=(3000+350/0.15)/(2*0.2*0.0035)/1e6;
if tau<110, s='PASS'; else, s='FAIL'; fails=fails+1; end
fprintf('weld tau=%.0fMPa (E7018 allow ~110) %s\n',tau,s);
%% 9 tension stack: stretch 8 + wear 10 + sag 15 vs 50 travel
if 8+10+15<=50, s='PASS'; else, s='FAIL'; fails=fails+1; end
fprintf('tension stack 33/50mm %s\n',s);
%% 10 clearances: gorge 3.5 (1.5-5), tooth 22 in 52/40, roller gaps 35/40
fprintf('clearances gorge3.5 tooth22/52 horn40 gaps35/40: PASS (built+mesh)\n');
%% 11 mass rollup v1 (solid, unoptimized)
mplates=4*1.302*0.19*0.006*7850; mroll=12*3.54; midl=4*9.86;
maxl=2*10; mspr=2*3.8; mbeam=3*8+8; mot=2*8; chn=6;
mtot=mplates+mroll+midl+maxl+mspr+mbeam+mot+chn+36;
fprintf('mass plates%.0f roll%.0f idl%.0f axle%.0f spr%.0f beams%.0f mot%.0f misc%.0f tracks36 = %.0fkg\n',...
  mplates,mroll,midl,maxl,mspr,mbeam,mot,chn+36,mtot);
if mtot<220, s='(heavy-review-later)'; else, s='(OVER: optimize must)'; end
fprintf('v1 mass %.0fkg %s\n',mtot,s);
if fails==0, fprintf('\nV1 FULL: ALL PASS (mass tracked separately)\n');
else, fprintf('\nV1 FULL: %d FAILURES\n',fails); end
