% V2_WEIGHT_MOTOR  Does a lighter undercarriage buy a smaller traction motor?
% Demand model is the same as sim_v2.m (Bekker Rc + grade), per side.
% Base MATLAB only.
clear; clc;
g=9.81; Rp=0.10526; eta=0.95;
kc=5.3e3; kphi=1515e3; sn=0.7; Wm=0.18; Ls=1.0013;
A=2*Ls*Wm; keq=kc/Wm+kphi;
v1=0.88; v2=0.70;

fprintf('=== V2 WEIGHT vs MOTOR (per side, eta=%.2f) ===\n',eta);
fprintf('%-9s %6s %6s %8s %8s %8s %7s\n',...
  'mass_kg','T15','T20','P15@.88','P15@.70','P20@.88','p_kPa');
for M=[165.7 185.7 250 261.7 281.7 300 350 400]
  [T15,p]=demand(M,15,g,Rp,Ls,Wm,A,keq,sn);
  T20=demand(M,20,g,Rp,Ls,Wm,A,keq,sn);
  P15a=T15*v1/Rp/eta; P15b=T15*v2/Rp/eta; P20=T20*v1/Rp/eta;
  fprintf('%-9.1f %6.1f %6.1f %8.0f %8.0f %8.0f %7.1f\n',...
    M,T15,T20,P15a,P15b,P20,p/1000);
end

fprintf('\n--- weight cut from the as-drawn 185.7 kg ---\n');
cuts={ 'motors 2x9.0 -> 2x5.4 kg', 7.2;
       'side-plate pockets (keep 6 mm bosses)', 6.0;
       'guards 2.0 -> 1.5 mm', 3.0;
       'flanges 8 -> 6 mm', 1.0;
       'deck mounts solid -> fabricated', 2.3;
       'bolts 28 -> 20 M12', 0.5 };
tot=0;
for i=1:size(cuts,1)
  fprintf('  %-42s -%.1f kg\n',cuts{i,1},cuts{i,2});
  tot=tot+cuts{i,2};
end
fprintf('  %-42s -%.1f kg -> %.1f kg\n','TOTAL',tot,185.7-tot);

fprintf('\n--- does it buy a smaller motor? (per side) ---\n');
for M=[281.7 261.7]
  T15=demand(M,15,g,Rp,Ls,Wm,A,keq,sn);
  T20=demand(M,20,g,Rp,Ls,Wm,A,keq,sn);
  P15=T15*v1/Rp/eta; P20=T20*v1/Rp/eta;
  fprintf('machine %.1f kg: 15deg %.0f W cont, 20deg %.0f W burst\n',M,P15,P20);
  for P=[350 450 600 850]
    fprintf('   %3d W motor: 15deg margin %+4.0f%%, 20deg burst margin %+4.0f%% (2x peak)\n',...
      P,(P/P15-1)*100,(2*P/P20-1)*100);
  end
end

fprintf('\n--- 850 W benchmark ---\n');
T850=850*eta/v1*Rp;
fprintf('850 W at 0.88 m/s = %.1f Nm at the wheel = %+.0f%% vs the 400/20 burst.\n',...
  T850,(T850/70.7-1)*100);
fprintf('850 W is %.1f A at 48 V, %.1f A at 24 V.\n',850/48,850/24);
fprintf('A 600 W motor covers the 400/20 burst with its 2x peak; 850 W is not required.\n');

fprintf('\n--- sensitivity ---\n');
fprintf('dP/dM at 15deg/0.88 m/s = %.2f W per kg per side (20 kg saves ~%.0f W).\n',...
  g*sind(15)*v1/(2*eta), 20*g*sind(15)*v1/(2*eta));
fprintf('Speed 0.88 -> 0.70 m/s saves 20%% of traction power.\n');
fprintf('Grade 15 -> 10 deg saves 33%% (sin ratio).\n');

function [T,p]=demand(M,th,g,Rp,Ls,Wm,A,keq,sn)
  W=M*g;
  p=W*cosd(th)/A;
  z=(p/keq)^(1/sn);
  Rc=2*(Wm*Ls*keq*z^(sn+1)/(sn+1));
  T=(W*sind(th)+Rc)/2*Rp;
end
