% SIM_V2_TURN  skid-steer turn demand vs burst (Wong moment resistance).
% Mr = mu_lat*W*Ls/4 (whole vehicle), dF = Mr/gauge per side, T = dF*Rp.
% Soil: solid estate -> mineral-loam Bekker is conservative; Rc from full keq.
% Base MATLAB only.
clear; clc;
g=9.81; Rp=105.26/1000; Ls=1.0013; gauge=0.52; Wm=0.18;
A=2*Ls*Wm; keq=5.3e3/Wm+1515e3; sn=0.7;
Twb=25*(48/14)*0.95;
fprintf('=== TURN (burst lim %.1f) ===\n',Twb);
for M=[250 400]
  W=M*g;
  p=W/A; z=(p/keq)^(1/sn); Rc=2*(Wm*Ls*keq*z^(sn+1)/(sn+1));
  for mu=[0.4 0.6]
    Mr=mu*W*Ls/4; Tt=Mr/gauge*Rp;
    Tg15=((W*sind(15)+Rc)/2)*Rp;
    f1='PASS'; if Tt>Twb, f1='REVIEW'; end
    f2='PASS'; if Tt+Tg15>Twb, f2='REVIEW'; end
    fprintf('M%d mu%.1f flat-turn %.1f %s | turn+15deg %.1f %s\n',M,mu,Tt,f1,Tt+Tg15,f2);
  end
end
fprintf('RULE: pivot-turn flat only (250 ok, 400 wide-arcs); NEVER pivot on slopes.\n');
