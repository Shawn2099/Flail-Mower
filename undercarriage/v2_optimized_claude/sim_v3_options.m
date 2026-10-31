% SIM_V3_OPTIONS  Compare E48-2.2, E48-3.0 and H24 against the v2 demand.
% Demand model: same as sim_v2.m (Bekker Rc + grade), per side.
% Specs: UC_V3_SPECS.md. Costs are planning estimates, kINR.
% Base MATLAB only.
clear; clc;
g=9.81; Rp=0.10526; eta=0.95;
kc=5.3e3; kphi=1515e3; sn=0.7; Wm=0.18; Ls=1.0013;
A=2*Ls*Wm; keq=kc/Wm+kphi;
[T400_15,~]=demand(400,15,g,Rp,Ls,Wm,A,keq,sn);
[T400_20,~]=demand(400,20,g,Rp,Ls,Wm,A,keq,sn);
fprintf('=== UC-V3 BUILD COMPARISON (per side, eta=%.2f) ===\n',eta);
fprintf('400/15 %.1f Nm, 400/20 %.1f Nm at the wheel\n\n',T400_15,T400_20);

% name, V, deck_kW, deck_cost_k, deck_mass, Tmot, Tpk, nmot, G,
% traction_cost_k, traction_mass, pack_kWh, pack_Ah, pack_cost_k, pack_mass,
% aux_cost_k, engine_kW, engine_cost_k, engine_mass, alt_kW, alt_cost_k,
% alt_mass, fuel_Lh, sep, base_mass
B(1)=mk('E48-2.2',48,2.2,17.0,10, 12.0,24.0,480,6.0, 21.7,10.8, 1.92,40,40.0,16, 17.0, 0,0,0, 0,0,0, 0,0, 281.7);
B(2)=mk('E48-3.0',48,3.0,35.8,15, 12.0,24.0,480,6.0, 21.7,10.8, 2.04,40,54.0,16, 22.0, 0,0,0, 0,0,0, 0,1, 281.7);
B(3)=mk('H24',    24,0.0, 0.0, 0, 9.67,19.34,450,6.0, 20.0,10.8, 0.96,40,27.0, 8, 15.5, 5.2,28.0,25, 2.24,9.0,7.5,1.2,0, 281.7);

fprintf('%-9s %3s %5s %6s %6s %6s %7s %6s %7s %6s %8s %9s %s\n',...
 'build','V','v','Twc','Twp','T282','deck','Crate','runmin','mass','parts','allin','selffab');
for i=1:numel(B)
  b=B(i);
  Twc=b.Tmot*b.G*eta; Twp=b.Tpk*b.G*eta;
  v=b.nmot/b.G*2*pi*Rp/60;
  % mass: base has 15 kg deck motor, 18 kg traction, 8 kg pack
  mass=b.base_mass - 15 - 18 - 8 + b.deck_mass + b.traction_mass + b.pack_mass;
  if b.engine_kW>0, mass=mass + b.engine_mass + b.alt_mass + 4 + 3; end
  [T282,~]=demand(mass,15,g,Rp,Ls,Wm,A,keq,sn);
  P282=2*T282*v/Rp/eta;               % W total at build mass, 15 deg
  if b.sep
    Crate=(b.deck_kW*1000/b.V)/20; runmin=1.02/(b.deck_kW)*60;
    note=sprintf('rover %.1fC %.0fmin',(P282/b.V)/20,1.02/(P282/1000)*60);
  elseif b.engine_kW>0
    Crate=(P282/b.V)/40; runmin=0.96/(P282/1000)*60; note='engine unlimited';
  else
    Crate=((b.deck_kW*1000+P282)/b.V)/40; runmin=1.92/((b.deck_kW*1000+P282)/1000)*60;
    note='shared 2P pack';
  end
  % cost
  drive=b.deck_cost_k + b.traction_cost_k + b.pack_cost_k + b.aux_cost_k + b.engine_cost_k + b.alt_cost_k;
  parts=149.3+drive;
  allin=parts*1.18*1.10;
  selffab=(parts-34.0)*1.18*1.10;
  fprintf('%-9s %3d %5.2f %6.1f %6.1f %6.1f %7s %6.2f %7.0f %6.1f %8.1f %9.1f %8.1f\n',...
    b.name,b.V,v,Twc,Twp,T282,deckstr(b),Crate,runmin,mass,parts,allin,selffab);
  fprintf('   %s | cont %s (%.0f/%.1f) | burst %s (%.0f/%.1f) | speed %s\n',...
    note, ok(Twc>=T400_15),Twc,T400_15, ok(Twp>=T400_20),Twp,T400_20, ...
    ok(v>=0.5&&v<=1.1));
  if b.engine_kW>0
    engload=(1.8e3+1.2e3/0.6)/(b.engine_kW*1000);
    fprintf('   engine %.0f%% of %.1f kW cont, fuel %.1f L/h\n',engload*100,b.engine_kW,b.fuel_Lh);
  else
    Pneed=0.988e3;   % electrical at 3000 rpm/1.0 m/s, sim_light_grass_rotor_sizing
    cont=0.65*b.deck_kW*1000;
    fprintf('   deck %.1f kW: cont(0.65) %.2f kW vs %.2f kW need -> %+.0f%%\n',...
      b.deck_kW,cont/1000,Pneed/1000,(cont/Pneed-1)*100);
  end
end

fprintf('\n--- budget (kINR, GST 18%% + contingency 10%%) ---\n');
fprintf('E48-2.2: 318 new | 274 self-fab+used tracks | 248 with used 2P pack -> fits only with used pack\n');
fprintf('E48-3.0: 367 new | 323 self-fab+used tracks | 292 with used packs -> does NOT fit 250\n');
fprintf('H24:     325 new | 281 self-fab+used tracks | 245 with used engine+alt+pack -> fits\n');

function s=mk(name,V,Pd,cd,md,T,Tp,n,G,ct,mt,kWh,Ah,cp,mp,ca,Pe,ce,me,Pa,ca2,ma,fl,sep,mb)
  s=struct('name',name,'V',V,'deck_kW',Pd,'deck_cost_k',cd,'deck_mass',md,...
    'Tmot',T,'Tpk',Tp,'nmot',n,'G',G,'traction_cost_k',ct,'traction_mass',mt,...
    'pack_kWh',kWh,'pack_Ah',Ah,'pack_cost_k',cp,'pack_mass',mp,'aux_cost_k',ca,...
    'engine_kW',Pe,'engine_cost_k',ce,'engine_mass',me,'alt_kW',Pa,'alt_cost_k',ca2,...
    'alt_mass',ma,'fuel_Lh',fl,'sep',sep,'base_mass',mb);
end
function s=deckstr(b)
  if b.engine_kW>0, s='engine'; else, s=sprintf('%.1fkW',b.deck_kW); end
end
function s=ok(b), if b, s='PASS'; else, s='FAIL'; end, end
function [T,p]=demand(M,th,g,Rp,Ls,Wm,A,keq,sn)
  W=M*g; p=W*cosd(th)/A; z=(p/keq)^(1/sn);
  Rc=2*(Wm*Ls*keq*z^(sn+1)/(sn+1));
  T=(W*sind(th)+Rc)/2*Rp;
end
