% SIM_BATTERY_UC  traction + rotor power vs 48V20Ah pack (base MATLAB only).
clear; clc; g=9.81; eta=0.85;
Protor=689; Pctl=60; usable=48*20*0.8;
fprintf('=== pack 48V20Ah usable %dWh (rotor %dW + ctrl %dW base) ===\n',usable,Protor,Pctl);
for M=[200 250 300 400]
  W=M*g;
  for th=[0 10 15]
    Ptr=(W*sind(th)+50)*1.0/eta;  % 1 m/s + Rc allowance
    Ptot=Protor+Ptr+Pctl; t=usable/Ptot*60;
    fprintf('M%d th%d: trac=%4.0fW total=%4.0fW time=%2.0fmin\n',M,th,Ptr,Ptot,t);
  end
end
