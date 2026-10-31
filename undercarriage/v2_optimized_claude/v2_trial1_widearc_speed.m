% V2_TRIAL1_WIDEARC_SPEED  Highest top speed per drive when pivots are banned (wide arcs only). Base MATLAB.
% Gates: peak wheel demand (wet arc 42 Nm, 8deg wet 37 Nm) <= 0.8*Tcap ; RMS (row cycle ~21 Nm) <= 0.85*rated.
% Pinion 8..20T on 48T sprocket, 428 chain, Rp=0.10526. Option data as v2_trial1_compare_all.m.
clear; clc; Rp=0.10526; eta=0.95; Tpk=42.2; Trms=21.2;
O={'A Mecwin 1.2kW',25,25,275,1,0.95; 'B 1418ZXF 500W',10,15,450,1,0.95; 'C BM1418ZXF 750W',15.36,23,480,1,0.95; 'D LION 13.5A+diff',1.75,3.3,3000,10,0.95*0.9};
fprintf('%-20s %5s %6s %8s %9s %9s\n','option','pinion','G','vtop m/s','peak/cap','RMS/rated');
for i=1:size(O,1)
  best=0;
  for N=8:20
    G=O{i,5}*48/N; e=O{i,6};
    pk=Tpk/(G*e)/O{i,3}; rm=Trms/(G*e)/O{i,2}; v=O{i,4}/G*2*pi*Rp/60;
    if pk<=0.8 && rm<=0.85 && v>best, best=v; bN=N; bpk=pk; brm=rm; bG=G; end
  end
  fprintf('%-20s %4dT %6.2f %8.2f %9.0f%% %9.0f%%\n',O{i,1},bN,bG,best,100*bpk,100*brm);
end
fprintf('\nfrozen v2 14T/48T (G=3.43) for reference: Mecwin 0.88 m/s needs %.0f%% of its cap in a wet arc.\n',100*Tpk/(3.43*0.95)/25);
