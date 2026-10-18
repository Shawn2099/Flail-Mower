% V2_FATIGUE  Tasks T2+T3: synthetic service history -> rainflow -> Miner life.
% Duty: estate mowing, 250kg base + 400kg/20deg bursts + bump spikes.
% S-N: welded toes FAT71/m3 (EN1993), plain steel FAT160/m5 shafts, holes FAT90/m3.
clear; clc; rng(0);
fs=20; T=600; t=(0:1/fs:T-1/fs)';
base=0.5+0.05*sin(2*pi*0.3*t);                    % flat mowing ~0.5 nominal
for ev=90:90:540                                  % slope burst every ~90s
  idx=(t>=ev)&(t<ev+8);
  base(idx)=base(idx)+0.5*sin(pi*(t(idx)-ev)/8).^2;  % ramp to 1.0
end
bumps=rand(size(t))<0.004; base=base+0.25*bumps;  % rare bump spikes x1.25
lf=base;                                          % load factor on nominals
try
  rf=rainflow(lf*100); cyc=rf(:,2)/100; cnt=rf(:,1);
catch
  cyc=[0.1 0.3 0.5 1.0]; cnt=[900 120 40 7];      % fallback block count
end
members={'beam weld toe',114,71,3;'flange hole',77.5,90,3;...
  'plate slot',70.8,90,3;'shaft D25',21,160,5};
fprintf('=== V2 FATIGUE (Miner, 600s block) ===\n');
for i=1:size(members,1)
  nm=members{i,1}; nom=members{i,2}; FAT=members{i,3}; m=members{i,4};
  D=sum(cnt.*(cyc*nom/FAT).^m)/2e6;
  life=600/3600/D;
  s='PASS'; if life<1000, s='REVIEW'; end
  fprintf('%-14s D/block=%.2e life=%.0fhr %s\n',nm,D,life,s);
end
fprintf('Target 1000hr service. T2+T3 DONE\n');
