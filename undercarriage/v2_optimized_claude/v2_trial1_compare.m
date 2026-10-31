% V2_TRIAL1_COMPARE  Mecwin 1.2kW BLDC (9T) vs Robokits 1418ZXF 48V 500W (8T), 282 kg, pivot turns.
% Pivot = one track forward, other reversed (both motors driving). Nylon-gear limit swept.
% 1418ZXF: 10 Nm rated @450rpm, 1:6, 13.4A rated (robokits page). Gear peak rating UNVERIFIED -> swept.
% Mecwin: 25 Nm output [nameplate stall]. Resistance model = v2_trial1_drive.m. Base MATLAB.
clear; clc;
g=9.81; Rp=0.10526; Ls=1.0013; gauge=0.52; Wm=0.18; Z=48; M=282; W=M*g; A=2*Ls*Wm; etaC=0.95;
soil=struct('nm',{'dry','wet'},'n',{0.7,0.5},'kc',{5.27,13.19},'kp',{1515.04,692.15},'f',{0.04,0.08});
function Tf=flatT(W,s,Rp,Ls,Wm,A)   % per-side straight resistance, slope 0, no flail reaction
  keq=s.kc/Wm+s.kp; p=W/A*1e-3; z=(p/keq)^(1/s.n);
  Rc=2*Wm*Ls*keq*z^(s.n+1)/(s.n+1)*1e3; Tf=((Rc+s.f*W)/2)*Rp; end
mot(1)=struct('nm','Mecwin 1.2kW 9T','N',9,'Tr',25,'cap',25,'n',275);
mot(2)=struct('nm','1418ZXF 8T','N',8,'Tr',10,'cap',NaN,'n',450);
fprintf('%-6s %-5s | wheel Nm | motor Nm  | x rated: Mecwin  1418ZXF\n','soil','mu_t');
for si=1:2
  for mu=[0.3 0.4 0.5 0.6]
    Tw=flatT(W,soil(si),Rp,Ls,Wm,A)+mu*W*Ls/4/gauge*Rp;
    Tm1=Tw/(Z/9*etaC); Tm2=Tw/(Z/8*etaC);
    fprintf('%-6s %-5.1f | %6.1f   | %5.1f/%5.1f |          %.2f    %.2f\n',soil(si).nm,mu,Tw,Tm1,Tm2,Tm1/25,Tm2/10);
  end
end
fprintf('\n1418ZXF: pivot ok if nylon gear peak >= motor Nm / 0.8. Needed gear peak (x rated 10 Nm):\n');
for si=1:2, for mu=[0.4 0.6]
  Tm2=(flatT(W,soil(si),Rp,Ls,Wm,A)+mu*W*Ls/4/gauge*Rp)/(Z/8*etaC);
  fprintf('  %s mu %.1f -> %.1f Nm peak, %.1fx rated; with 0.8 util gear must be >= %.1f Nm (%.1fx)\n',soil(si).nm,mu,Tm2,Tm2/10,Tm2/0.8,Tm2/0.8/10);
end,end
fprintf('\nSpeed: Mecwin 9T vtop %.2f ; 1418ZXF 8T vtop %.2f m/s (no-load 516rpm: %.2f)\n',...
  275/(Z/9)*2*pi*Rp/60,450/(Z/8)*2*pi*Rp/60,516/(Z/8)*2*pi*Rp/60);
% pivot electrical power: wheel speed during pivot 0.3 m/s track speed
wv=0.3/Rp; Tw=flatT(W,soil(1),Rp,Ls,Wm,A)+0.5*W*Ls/4/gauge*Rp;
fprintf('pivot at 0.3 m/s track speed, mu 0.5 dry: %.0f W mech per side, %.0f W both; ~%.0f A @46V (eta .75)\n',Tw*wv,2*Tw*wv,2*Tw*wv/0.75/46);
fprintf('current-limit idea: cap 1418ZXF at 1.5x rated = 15 Nm -> wheel %.0f Nm available\n',15*(Z/8)*etaC);
fprintf('cost 2 sides: Mecwin 2x(10421+ctrl 5000)=%d ; 1418ZXF 2x(5620+ctrl 2000..6000)=%d..%d\n',2*15421,2*7620,2*11620);
