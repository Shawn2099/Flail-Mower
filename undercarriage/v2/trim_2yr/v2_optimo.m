% V2_OPTIMO  2-year edition: min-mass grid with static + 1000hr-fatigue gates.
% Vars: plate t {4,5,6}, flange t {6,8}, beam {SHS32,SHS40}.
% Life rule: 2yr @ 500hr/yr = 1000hr; service every 2mo (~85hr).
% Base lives from v2_fatigue (m=3): beam 25743@114, flange 166889@77.5, plate 218894@70.8.
% Rare-peak allow 225. Bought bores lock shafts/chain/bearings.
clear; clc;
fprintf('=== V2 2-YEAR TRIM OPTIMIZER (static + 1000hr fatigue) ===\n');
best=[];
for pt=[4 5 6]
  for ft=[6 8]
    for b=1:2
      if b==1, Wb=2.775e-6; mb=9.6; bn='SHS32'; nbeam=180; else, Wb=4.4e-6; mb=14.6; bn='SHS40'; nbeam=114; end
      mpl=47*pt/6; mfl=4.3*ft/8;
      % flange is friction-grip (torqued M12+washers): holes see ~30% bypass only
      peak_plate=70.8*(6/pt)*2.30; peak_fl=77.5*0.3*3.20*(8/ft)^2; peak_beam=500/Wb/1e6;
      nplate=70.8*(6/pt); nfl=77.5*(8/ft)^2;
      life_plate=218894*(70.8/nplate)^3; life_fl=166889*(77.5/nfl)^3; life_beam=25743*(114/nbeam)^3;
      okS=peak_plate<=225&&peak_fl<=225&&peak_beam<=225;
      okF=life_plate>=1000&&life_fl>=1000&&life_beam>=1000;
      mt=mpl+mfl+mb;
      s='ok'; if ~okS, s='STATIC-FAIL'; elseif ~okF, s='LIFE-FAIL'; end
      fprintf('pt%d ft%d %s mass=%.1f P%.0f/F%.0f/B%.0f LP%.0f/LF%.0f/LB%.0f %s\n',pt,ft,bn,mt,peak_plate,peak_fl,peak_beam,life_plate,life_fl,life_beam,s);
      if okS&&okF, best=[best; mt pt ft b]; end
    end
  end
end
if isempty(best), fprintf('NO feasible row — frozen violates?! review Kt/bypass.\n');
else
[~,i]=min(best(:,1));
fprintf('min-mass feasible: pt%d ft%d beam%d = %.1fkg\n',best(i,2),best(i,3),best(i,4),best(i,1));
fprintf('FROZEN mass=%.1fkg. Saving to min = %.1fkg.\n',47+4.3+14.6,47+4.3+14.6-best(i,1));
end
fprintf('2-YEAR RECO below. T6 DONE\n');
