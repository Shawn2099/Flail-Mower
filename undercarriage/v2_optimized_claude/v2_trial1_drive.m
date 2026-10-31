% V2_TRIAL1_DRIVE  Trial-1 traction sizing for the coffee-estate flail rover (OPTION STUDY, not frozen).
% Scope: firm/flat to mild slope, tracks 180x72x37, undercarriage v2 (48T wheel sprocket, 428 chain),
% all-up mass 282 kg (WEIGHT_EFF.md), NOT the 400 kg/20deg envelope of sim_v2.m.
% Method: per-side wheel torque = grade + Bekker bulldozing + internal track resistance
%   + flail reaction + (skid-steer turn moment, Wong Mr = mu_t*W*L/4).  Then
%   (1) peak gates, (2) duty-cycle RMS gate (thermal), (3) exhaustive discrete selection
%   motor x pinion x controller, min INR.  Exhaustive enumeration == integer program here
%   (a few hundred combos), so base MATLAB only.  Optimization Toolbox is licensed but not needed.
% Tags: [V]=verified in TRIAL1_DRIVE.md sources, [EST]=estimate, must be bench/field confirmed.
clear; clc; close all; fails=0;
g=9.81; Rp=0.10526; Ls=1.0013; gauge=0.52; Wm=0.18; Z=48;          % v2 geometry [CAD]
etaC=0.95;                                                        % 428 chain [EST, typical 0.95-0.98]
M=282;  W=M*g;                                                    % as-built all-up [WEIGHT_EFF.md]
A=2*Ls*Wm;

% ---- terrain (Wong, Theory of Ground Vehicles Table 2.x; SI: kc kN/m^(n+1), kphi kN/m^(n+2)) ----
%        name              n     kc(kN)  kphi(kN)
T(1)=struct('nm','dry sandy loam',  'n',0.70,'kc',5.27, 'kp',1515.04);  % existing sim_v2 choice
T(2)=struct('nm','clayey (wet)',    'n',0.50,'kc',13.19,'kp',692.15);   % wet / monsoon, soft
fint=[0.04 0.08];     % internal rubber-track + roller/idler rolling coeff, firm / soft [EST 4-8% W]
Fmow=100;             % flail reaction force on rover, N [EST]
mu_t=[0.4 0.6];       % lateral coeff tracks on soil/grass [Wong 0.5-0.7 typ, EST range]
slopes=[0 5 8 10];    % deg  (user: trial 1 flat / mild only)
vs=[0.5 0.7 0.88];    % m/s forward speeds under study

% ---- candidates: V, rated W, rated out rpm, rated Nm, peak_Nm (motor), I_rated A, price INR, mass, eta ----
%   MY1020Z: Yalu datasheet 1.80 Nm @3200rpm motor shaft x 6.67 x 0.85 gear eff = 10.2 Nm out [V-partial]; peak 2x [EST].
C(1)=struct('nm','Mecwin 1.2kW BLDC','V',48,'Tr',25.0,'n',275,'Tp',25.0,'pr',10421,'m',9.0,'eta',0.85,'ip',0,'br',0);
C(2)=struct('nm','MY1020Z 600W 48V','V',48,'Tr',10.2,'n',480,'Tp',20.4,'pr',8850,'m',5.4,'eta',0.78,'ip',1,'br',1);
C(3)=struct('nm','MY1020Z 450W 48V','V',48,'Tr',8.2, 'n',450,'Tp',16.5,'pr',7500,'m',5.0,'eta',0.78,'ip',1,'br',1);
C(4)=struct('nm','MY1016Z3 350W 24V','V',24,'Tr',11.1,'n',300,'Tp',19.0,'pr',5500,'m',4.0,'eta',0.78,'ip',1,'br',1);
C(5)=struct('nm','Wheelchair 250W 19:1 24V','V',24,'Tr',16.95,'n',150,'Tp',33.9,'pr',6000,'m',6.0,'eta',0.75,'ip',1,'br',1);
% ip=ingress shroud needed (IP33 e-bike motor), br=brushed (no brake, no regen)
% controllers: name, max amps, price INR, type (0 BLDC,1 brushed), V
K(1)=struct('nm','Mecwin 60A BLDC','A',60,'pr',13867,'br',0,'V',48);
K(2)=struct('nm','generic 48V 30A BLDC','A',30,'pr',4000,'br',0,'V',48);
K(3)=struct('nm','48V 30A brushed','A',30,'pr',2000,'br',1,'V',48);
K(4)=struct('nm','48V 60A brushed','A',60,'pr',3500,'br',1,'V',48);
K(5)=struct('nm','24V 30A brushed + 48-24V DCDC','A',30,'pr',2000+2500,'br',1,'V',24);
shroud=800;           % INR per motor, vent shroud/seal for IP33 e-bike motors [EST]
Nset=8:16;            % pinion teeth on 428 chain, 48T wheel sprocket
fprintf('=== V2 TRIAL-1 DRIVE  M=%.0f kg (W=%.0f N)  Rp=%.4f  Ls=%.3f  gauge=%.2f ===\n',M,W,Rp,Ls,gauge);

% ---- 1. wheel torque per side, load-case table ----
function Tw=sideT(W,th,ti,fint,Fmow,Rp,Ls,Wm,A,T)
  p=W*cosd(th)/A*1e-3;                         % kPa
  keq=T.kc/Wm+T.kp;                            % kN/m^(n+2) with b in m
  z=(p/keq)^(1/T.n);                           % sinkage m
  Rc=2*Wm*Ls*(keq*z^(T.n+1))/(T.n+1)*1e3;     % N, both tracks (bulldozing, Wong 2.x)
  Tw=((W*sind(th)+Rc+fint*W*cosd(th)+Fmow)/2)*Rp;
end
fprintf('\n--- per-side wheel torque Nm (straight) / + pivot-turn moment ---\n');
fprintf('%-14s %5s | %7s %7s | %s\n','soil','slope','straight','z mm','pivot add (mu .4/.6)');
Tcase=[];   % rows: soil, slope, straight, pivotAdd
for si=1:2
  for th=slopes
    Ts=sideT(W,th,si,fint(si),Fmow,Rp,Ls,Wm,A,T(si));
    p=W*cosd(th)/A*1e-3; keq=T(si).kc/Wm+T(si).kp; z=(p/keq)^(1/T(si).n);
    add=mu_t*W*Ls/4/gauge*Rp;                    % N per side * Rp
    fprintf('%-14s %4d* | %7.1f %7.1f | %.1f / %.1f\n',T(si).nm,th,Ts,z*1e3,add(1),add(2));
    Tcase=[Tcase; si th Ts add(1) add(2)]; %#ok<AGROW>
  end
end

% ---- 2. requirement envelope per option (design cases) ----
% Gate cases: [soil, slope, turn-mu(0=none)] ; peak = straight(th)+pivot at flat only (never pivot on slope)
%   Option-W : wide arcs only  -> peak = straight(slope) , arc turn adds <= 0.3*pivot (EST)
%   Option-P : pivot on flat   -> peak = straight(0)+pivot(mu)
fprintf('\n--- design cases (soil dry / wet) ---\n');
th_des=5;                                       % design slope; sweep above shows 8,10 too
Dd.dry_cont=sideT(W,th_des,1,fint(1),Fmow,Rp,Ls,Wm,A,T(1));
Dd.wet_cont=sideT(W,th_des,2,fint(2),Fmow,Rp,Ls,Wm,A,T(2));
Dd.wet_flat=sideT(W,0,2,fint(2),Fmow,Rp,Ls,Wm,A,T(2));
piv=mu_t(2)*W*Ls/4/gauge*Rp;                    % mu_t 0.6 pivot add
Dd.pivot_dry=sideT(W,0,1,fint(1),Fmow,Rp,Ls,Wm,A,T(1))+piv;
Dd.pivot_wet=Dd.wet_flat+piv;
Dd.arc_wet=Dd.wet_flat+0.3*piv;
fn=fieldnames(Dd); for i=1:numel(fn), fprintf('%-10s %6.1f Nm/side\n',fn{i},Dd.(fn{i})); end

% ---- 3. duty cycle RMS (row mowing, 50 m rows, headland turn) ----
rowlen=50; tturn=8;                             % m, s per headland turn [EST]
function rms=cycleRMS(Tstr,Tturn,L,v,tt,fslope,Tslope)
  ts=L/v; t1=ts*(1-fslope); t2=ts*fslope;
  rms=sqrt((Tstr^2*t1+Tslope^2*t2+Tturn^2*tt)/(t1+t2+tt));
end

% ---- 4. exhaustive discrete selection ----
% options set: speed v, turn style, soil.  Gate each combo on peak and RMS.
scen={'DRY wide-arc 5deg 0.5',1,'arc',0.5; 'DRY pivot 5deg 0.5',1,'piv',0.5; ...
      'WET wide-arc 5deg 0.5',2,'arc',0.5; 'WET pivot 5deg 0.5',2,'piv',0.5; ...
      'DRY wide-arc 5deg 0.88',1,'arc',0.88; 'WET pivot 8deg 0.5',2,'piv8',0.5};
pk_util=0.8;  derate_rms=0.85;      % RMS torque allowed = 0.85 * rated continuous (intermittent, 40C ambient) [EST]
Irate=@(c) (c.Tr*2*pi*c.n/60)/(c.V*c.eta);       % A at rated
for sc=1:size(scen,1)
  nm=scen{sc,1}; si=scen{sc,2}; ts=scen{sc,3}; v=scen{sc,4};
  th=5; if strcmp(ts,'piv8'), th=8; ts='piv'; end
  Tflat=sideT(W,0,si,fint(si),Fmow,Rp,Ls,Wm,A,T(si));
  Tslope=sideT(W,th,si,fint(si),Fmow,Rp,Ls,Wm,A,T(si));
  if strcmp(ts,'piv'), Tturn=Tflat+piv; Tpk_w=max(Tslope,Tturn);
  else,                Tturn=Tflat+0.3*piv; Tpk_w=max(Tslope,Tturn); end
  Trms_w=cycleRMS(Tflat,Tturn,rowlen,v,tturn,0.1,Tslope);
  best=[]; bestc=inf; nfeas=0;
  for ci=1:numel(C)
    c=C(ci);
    for N=Nset
      Gr=Z/N; vtop=c.n/Gr*2*pi*Rp/60;
      if vtop<v*1.0 || vtop>1.2, continue; end     % top speed must reach target, not run away
      % speed scaling: at target v the motor runs at fraction v/vtop of rated rpm (controller PWM)
      Tm_pk=Tpk_w/(Gr*etaC); Tm_rms=Trms_w/(Gr*etaC);
      for ki=1:numel(K)
        k=K(ki);
        if k.V~=c.V || k.br~=c.br, continue; end
        kt=c.Tr/Irate(c);                           % Nm/A at motor shaft output (rated point)
        Tcap=min(c.Tp,kt*k.A);                      % torque limited by gearbox peak AND controller amps
        if Tm_pk>pk_util*Tcap || Tm_rms>derate_rms*c.Tr, continue; end
        cost=2*(c.pr+k.pr+c.ip*shroud);
        nfeas=nfeas+1;
        if cost<bestc, bestc=cost; best=struct('c',c.nm,'N',N,'k',k.nm,'vtop',vtop,...
            'pk',Tm_pk/Tcap,'rms',Tm_rms/c.Tr,'Tpk',Tm_pk,'Tcap',Tcap,'m',c.m); end
      end
    end
  end
  fprintf('\n[%s] soil=%s  peak wheel %.1f Nm  RMS %.1f Nm  feasible combos %d\n',nm,T(si).nm,Tpk_w,Trms_w,nfeas);
  if isempty(best)
    fprintf('  NO feasible catalogue combo -> FAIL\n'); fails=fails+1;
  else
    fprintf('  cheapest: %s | %dT pinion | %s | vtop %.2f m/s | peak %.0f%% of cap (%.1f/%.1f Nm) | RMS %.0f%% of rated | 2 sides INR %d | 2 motors %.1f kg\n',...
      best.c,best.N,best.k,best.vtop,100*best.pk,best.Tpk,best.Tcap,100*best.rms,bestc,2*best.m);
  end
end

% ---- 5. bus current / pack (for the single-pack question) ----
fprintf('\n--- bus current, both traction motors at the cheapest-case peak + mower ---\n');
Vbus=46; Pmow_pk=3000/0.9/0.95; Pmow_typ=1800/0.9/0.95;   % mower 3 kW peak, 60%% typ light grass [EST]
for cs={'flat typ',0,0;'5deg',5,0;'pivot flat peak',0,1}'
  th=cs{2}; pv=cs{3};
  Ts=sideT(W,th,1,fint(1),Fmow,Rp,Ls,Wm,A,T(1))+pv*piv;
  Pw=2*Ts/Rp*0.5/0.78/0.95;                      % at 0.5 m/s, brushed motor eta .78, ctrl .95
  fprintf('%-16s traction %.0f W  + mower typ %.0f W = %.0f W = %.0f A @46V ; + mower peak = %.0f A\n',...
    cs{1},Pw,Pmow_typ,Pw+Pmow_typ,(Pw+Pmow_typ)/Vbus,(Pw+Pmow_pk)/Vbus);
end
fprintf('Single 48V 40Ah pack at 2C = 80 A continuous would cover the typ cases; verify BMS/cell sheet.\n');
if fails==0, fprintf('\nTRIAL1 DRIVE: ALL SCENARIOS HAVE A FEASIBLE COMBO\n');
else, fprintf('\nTRIAL1 DRIVE: %d scenario(s) with no feasible catalogue combo\n',fails); end
