% V2_MOTOR_SWAP  COTS brushed geared-motor screen for the v2 undercarriage.
% Requirement frozen by sim_v2.m / BRIEF.md:
%   wheel 53.5 Nm cont (400 kg/15deg), 70.7 Nm burst (400 kg/20deg),
%   vtop 0.88 m/s at 275 rpm motor, chain G=48/14=3.43, eta=0.95.
% Candidate data from maker sheets (links in MOTOR_SWAP.md).
% Peak torque where the sheet gives none = 2x rated [EST].
% Base MATLAB only.
clear; clc; fails=0;
G0=48/14; eta=0.95; Rp=0.10526; n_w=80.2;      % wheel rpm at 0.88 m/s
T_cont=53.5; T_burst=70.7; vmin=0.5; vmax=1.1;
T_req_c=T_cont/(G0*eta); T_req_b=T_burst/(G0*eta);
P_req_c=T_cont*2*pi*n_w/60/eta; P_req_b=T_burst*2*pi*n_w/60/eta;
fprintf('=== V2 MOTOR SWAP (48 V pack, existing 48T/14T, G=%.2f, eta=%.2f) ===\n',G0,eta);
fprintf('wheel: cont %.1f Nm / burst %.1f Nm at 0.88 m/s\n',T_cont,T_burst);
fprintf('motor: cont %.1f Nm (%.0f W) / burst %.1f Nm (%.0f W) at 275 rpm\n',...
        T_req_c,P_req_c,T_req_b,P_req_b);
fprintf('mow band %.2f-%.1f m/s; minimum motor count = 2 (one per track)\n\n',vmin,vmax);

C(1)=struct('name','Mecwin 1.2kW BLDC (ref)','V',48,'P',1200,'n',275,'Tr',25.0,'Tp',25.0);
C(2)=struct('name','MY1016Z2 250W','V',24,'P',250,'n',357,'Tr',6.65,'Tp',11.5);
C(3)=struct('name','MY1016Z3 350W','V',24,'P',350,'n',300,'Tr',11.1,'Tp',19.0);
C(4)=struct('name','MY1020Z 450W','V',48,'P',450,'n',450,'Tr',9.70,'Tp',19.4);
C(5)=struct('name','MY1020Z 600W','V',48,'P',600,'n',480,'Tr',12.0,'Tp',24.0);
C(6)=struct('name','wheelchair 250W 19:1','V',24,'P',250,'n',150,'Tr',16.95,'Tp',33.9);
C(7)=struct('name','Rhino N34 worm 500W (BLDC)','V',48,'P',500,'n',150,'Tr',19.6,'Tp',39.0);

fprintf('--- re-geared to 0.88 m/s (Npin = 48/G_req) ---\n');
fprintf('%-26s %3s %5s %5s %6s %6s | %5s %4s %7s %8s %5s %s\n',...
  'candidate','V','P_W','n_out','T_rat','T_pk','G_req','Npin','T_wh_c','T_wh_pk','v_top','gate');
for i=1:numel(C)
  c=C(i); Greq=c.n/n_w; Npin=48/Greq;
  Twc=c.Tr*Greq*eta; Twp=c.Tp*Greq*eta;
  v=c.n/Greq*2*pi*Rp/60;
  ok=Twc>=T_cont && Twp>=T_burst && v>=vmin && v<=vmax;
  if ok, s='PASS'; else, s='FAIL'; fails=fails+1; end
  fprintf('%-26s %3d %5d %5d %6.2f %6.1f | %5.2f %4.1f %7.1f %8.1f %5.2f %s\n',...
    c.name,c.V,c.P,c.n,c.Tr,c.Tp,Greq,Npin,Twc,Twp,v,s);
end

fprintf('\n--- drop-in with existing G=%.2f (no sprocket change) ---\n',G0);
fprintf('%-26s %6s %8s %8s %6s %5s %5s %5s\n',...
  'candidate','v_m/s','T_wh_c','T_wh_pk','P/Prat','cont','burst','speed');
for i=1:numel(C)
  c=C(i); v=c.n/G0*2*pi*Rp/60;
  Twc=c.Tr*G0*eta; Twp=c.Tp*G0*eta;
  Pd=T_cont*v/Rp/eta;   % power to meet the continuous demand at this speed
  if Twc>=T_cont, a='PASS'; else, a='FAIL'; end
  if Twp>=T_burst, b='PASS'; else, b='FAIL'; end
  if v<vmin, s='SLOW'; elseif v>vmax, s='FAST'; else, s='OK'; end
  fprintf('%-26s %6.2f %8.1f %8.1f %6.2f %5s %5s %5s\n',...
    c.name,v,Twc,Twp,Pd/c.P,a,b,s);
end

fprintf('\n--- MY1020Z 48V 600W: pinion choice (48T wheel, 428 chain) ---\n');
fprintf('%4s %5s %6s %8s %9s %8s %s\n','Npin','G','v_m/s','T_mot_dem','T_mot/T_rat','P_dem_W','note');
for N=[8 9 10 14]
  G=48/N; v=480/G*2*pi*Rp/60;
  Td=T_cont/(G*eta); Pd=T_cont*v/Rp/eta;
  if Td<=12, s='OK'; else, s='OVER'; end
  fprintf('%4d %5.2f %6.2f %8.2f %9.2f %8.0f %s\n',N,G,v,Td,Td/12,Pd,s);
end

fprintf('\n--- motor count ---\n');
fprintf('track gauge 0.52 m: a 1 m-radius turn at 0.5 m/s needs 0.63/0.37 m/s.\n');
fprintf('A pivot turn needs -0.5/+0.5 m/s. One motor + diff cannot do either.\n');
fprintf('MINIMUM = 2 motors, one per track; 4 is unnecessary.\n');

fprintf('\nMinimum at 0.88 m/s: 16.4 Nm cont / 21.7 Nm burst at 275 rpm = 600 W class.\n');
if fails==0
  fprintf('MOTOR SWAP: ALL PASS\n');
else
  fprintf('MOTOR SWAP: %d candidate(s) rejected; see PASS rows above.\n',fails);
end
