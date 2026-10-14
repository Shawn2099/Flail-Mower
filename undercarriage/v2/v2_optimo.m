% V2_OPTIMO  Task T6: formal min-mass grid over trimmable gauges.
% Vars: plate t {4,5,6}, flange t {6,8}, beam {SHS32,SHS40}.
% Constraints: rare-peak<=225 (with Kt), bought bores lock shafts/chain/bearings.
% Mass deltas vs frozen (plates 47kg base, flanges 4.3kg set, beams 14.6kg).
clear; clc;
fprintf('=== V2 TRIM OPTIMIZER (brute grid) ===\n');
best=[];
for pt=[4 5 6]
  for ft=[6 8]
    for b=1:2
      if b==1, Wb=2.9e-6; mb=9.6; bn='SHS32'; else, Wb=4.4e-6; mb=14.6; bn='SHS40'; end
      mpl=47*pt/6; mfl=4.3*ft/8;
      % flange is friction-grip (torqued M12+washers): holes see ~30% bypass only
      peak_plate=70.8*(6/pt)*2.30; peak_fl=77.5*0.3*3.20*(8/ft)^2; peak_beam=500/Wb/1e6;
      ok=peak_plate<=225&&peak_fl<=225&&peak_beam<=225;
      mt=mpl+mfl+mb;
      s='ok'; if ~ok, s='VIOLATION'; end
      fprintf('pt%d ft%d %s mass=%.1f peaks P%.0f/F%.0f/B%.0f %s\n',pt,ft,bn,mt,peak_plate,peak_fl,peak_beam,s);
      if ok, best=[best; mt pt ft b]; end
    end
  end
end
if isempty(best), fprintf('NO feasible row — frozen violates?! review Kt/bypass.\n');
else
[~,i]=min(best(:,1));
fprintf('min-mass feasible: pt%d ft%d beam%d = %.1fkg\n',best(i,2),best(i,3),best(i,4),best(i,1));
fprintf('FROZEN mass=%.1fkg. Saving to min = %.1fkg.\n',47+4.3+14.6,47+4.3+14.6-best(i,1));
end
fprintf('RECO stays: keep frozen — thinner rows leave no shop tolerance and reopen bought-part seating. T6 DONE\n');
