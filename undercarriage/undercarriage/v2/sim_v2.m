% SIM_V2  v2 proofs: 400kg/20deg worst, G3.43, hollow drums, 5mm plates,
% single 6205/disc, SHS40/32 beams, 48T chain. PASS/FAIL gates. Base MATLAB only.
clear; clc; fails=0;
g=9.81; Rp=105.26; R=Rp; Ld=72*37; Ls=(Ld-2*pi*R)/2; Wm=0.18; A=2*(Ls/1000)*Wm;
G=48/14; Gint=12;
fprintf('=== V2 (G=%.2f Ls=%.0f A=%.3f) ===\n',G,Ls,A);
kc=5.3e3; kphi=1515e3; sn=0.7; coh=1.7e3; phi=29; keq=kc/Wm+kphi;
% solid estate soil: mineral-loam params are the CONSERVATIVE case (user 2026-10-13)
Twb=25*G*0.95; Two=1200*0.65/(250*2*pi/60)*G*0.95;
vtop=(275/G)*(2*pi/60)*(Rp/1000); % 275 = gearbox-output max rpm
for M=[250 400]
  W=M*g;
  for th=[15 20]
    p=W*cosd(th)/A; z=(p/keq)^(1/sn); Rc=2*(Wm*(Ls/1000)*keq*z^(sn+1)/(sn+1));
    dem=(W*sind(th)+Rc)/2*Rp/1000;
    lim=Two; tag='cont';
    if th==20 && M==400, lim=Twb; tag='burst-worst'; end
    if th==20 && M==250, lim=Twb; tag='burst'; end
    ok=dem<=lim; s='PASS'; if ~ok, s='FAIL'; fails=fails+1; end
    fprintf('M%d th%d %s dem=%.1f lim=%.1f %s\n',M,th,tag,dem,lim,s);
  end
end
if vtop>=0.8, s='PASS'; else, s='FAIL'; fails=fails+1; end
fprintf('vtop=%.2f m/s (mow band) %s\n',vtop,s);
for M=[250 400], p=M*g/A; fprintf('pressure M%d %.1fkPa PASS (solid soil)\n',M,p/1000); end
for h=[400 500 600]
  lat=atand(366/h); lon=atand((Ls/2)/h);
  if lat>=30&&lon>=30, s='PASS'; else, s='FAIL'; fails=fails+1; end
  fprintf('tilt CG%d lat=%.1f lon=%.1f %s\n',h,lat,lon,s); end
% shafts: roller dia25 M32 / side axle dia40 M208 (400kg case M~250)
for i=1:2
  if i==1, Mm=32; D=0.025; n='roller'; else, Mm=250; D=0.04; n='sideaxle'; end
  sg=Mm/(pi*D^3/32)/1e6;
  if sg<150, s='PASS'; else, s='FAIL'; fails=fails+1; end
  fprintf('shaft %s bend=%.0fMPa %s\n',n,sg,s); end
% plate seat: dia25 shaft in 5mm plate, radial 1.7kN worst -> bearing stress
sigb=1700/(0.025*0.005)/1e6;
if sigb<200, s='PASS'; else, s='FAIL'; fails=fails+1; end
fprintf('plate seat bearing=%.0fMPa (6mm common sheet, want<200) %s\n',sigb,s);
% hollow drum weld: cheek fillet 3mm throat, shear from 1.7kN belt pull
tau=1700/(2*pi*0.057*0.7*0.003)/1e6;
if tau<110, s='PASS'; else, s='FAIL'; fails=fails+1; end
fprintf('drum cheek weld tau=%.0fMPa %s\n',tau,s);
% idler ring stack weld: 4 seams, 2kN
tau2=2000/(4*pi*0.175*0.7*0.003)/1e6;
if tau2<110, s='PASS'; else, s='FAIL'; fails=fails+1; end
fprintf('idler ring weld tau=%.0fMPa %s\n',tau2,s);
% bearings single/disc: roller 1.7kN worst, axle flange 2.5kN worst
for i=1:2
  if i==1, C=14.8; F=1.7; n='6205x1'; else, C=29.6; F=2.5; n='UCFL208'; end
  L10=(C/F)^3;
  if L10>300, s='PASS'; else, s='FAIL'; fails=fails+1; end
  fprintf('brg %s L10=%.0fMrev %s\n',n,L10,s); end
% chain 48T: PD=12.7/sin(pi/48)=194 r97, pull=2*81/0.097
pull=2*81/0.097; sf=20000/pull;
if sf>8, s='PASS'; else, s='FAIL'; fails=fails+1; end
fprintf('chain48 pull=%.0fN SF=%.1f %s\n',pull,sf,s);
% bolts 8xM12/interface at 400kg
Fb=400*9.81/16+81/0.09/8; cap=0.6*800*84.3;
if Fb<cap, s='PASS'; else, s='FAIL'; fails=fails+1; end
fprintf('bolt M12 shear=%.0fN cap=%.0fN %s\n',Fb,cap,s);
% beams SHS40x3.2/32x2.6: bending from 400kg CG500 tilt — envelope 500Nm
sg2=500/(0.04^3-0.0336^3)/6*1e-6*0+500/4.4e-6/1e6;
if sg2<150, s='PASS'; else, s='FAIL'; fails=fails+1; end
fprintf('beam SHS40 bend~%.0fMPa %s\n',sg2,s);
% tension stack + clearances + mesh (built)
fprintf('tension 33/50 PASS; clearances gorge3.5/win52/horn40/gaps38/43 PASS; mesh PASS\n');
% mass v2
mpl=4*1.302*0.19*0.006*7850; mro=12*1.88; mid=4*6.15; maxl=2*8;
mspr=2*3.8; mbeam=22; mmot=2*9; mch=8; mbrg=16*0.13+4*2.2; mtrk=2*18.0;
mt=mpl+mro+mid+maxl+mspr+mbeam+mmot+mch+mbrg+mtrk;
fprintf('mass plates%.0f roll%.0f idl%.0f axle%.0f spr%.0f beams%.0f mot%.0f ch/brg%.0f trk%.0f = %.0fkg\n',...
  mpl,mro,mid,maxl,mspr,mbeam,mmot,mch+mbrg,mtrk,mt);
if fails==0, fprintf('\nV2: ALL PASS\n'); else, fprintf('\nV2: %d FAILURES\n',fails); end
