% V2_DUTY_BATT  Task T4: duty-mix runtime + motor thermal estimate (analytic).
% Duty from T2 history: 80% flat / 15% 10deg / 5% 15deg at 250kg estate work.
% Pack 48V20Ah usable 768Wh. Traction+rotor+ctrl from sim_battery_uc numbers.
clear; clc;
P=[808 1309 1555]; w=[0.8 0.15 0.05];
Pavg=sum(P.*w); Tmin=768/Pavg*60;
fprintf('duty-mix avg %.0fW -> runtime %.0fmin\n',Pavg,Tmin);
% motor thermal: 1.2kW unit, worst cont 600W each. I=600/48=12.5A.
% winding R023 (CONFIRM datasheet; Mecwin typical 0.04-0.06): use 0.05.
I=12.5; R=0.05; Pcu=I^2*R; Rth=1.5; dT=Pcu*Rth;
s='PASS'; if 40+dT>120, s='REVIEW'; end
fprintf('motor Cu %.1fW dT~%.0fK (40C amb -> %.0fC vs 120C class) %s\n',Pcu,dT,40+dT,s);
fprintf('ASSUMPTION: R=0.05/Rth=1.5 estimates — confirm against Mecwin datasheet before summer trials. T4 DONE\n');
