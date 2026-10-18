%% sim_775_SPlectron_check.m
% Check SP Electron RS-775 12V 12000rpm 100W DB + SEN51 3A PWM for POC trimmer
% Base MATLAB only.
clear; clc;
fprintf('\n=== SP ELECTRON RS-775 12V 12000rpm CHECK ===\n');
% Head (same POC as before)
d=1.6e-3; rhoA=1.225; Cd=1.1; r0=30e-3; L=70e-3; R=r0+L; nL=2;
Kgeo=rhoA*Cd*d*(R^4-r0^4)/8;
EsN=800; EsH=1500; W=2*R; v=0.15;
PcutN=EsN*W*v; PcutH=EsH*W*v;
fprintf('Swath %.0f mm, Pcut nom %.1f W / heavy %.1f W\n', W*1000, PcutN, PcutH);
% SP motor: n0=12000 @12V, est Tstall 0.40 Nm, Tcont 0.08 Nm (~80W cont), Ppeak ~140W shaft, eta 0.62
n0=12000; Ts=0.40; Tc=0.08; Pc=80; Pp=140; eta=0.62; V=12;
om=@(r) r*2*pi/60;
fprintf('rpm | Vtip | Paero | PshaftN | TloadN | Tavail | I(A@12V) | verdict vs 3A PWM\n');
for r=[5000 6500 8000 9500 10000 11000]
    o=om(r); pa=nL*Kgeo*o^3; ps=PcutN+pa; tl=ps/o; ta=Ts*(1-r/n0); pe=ps/eta; I=pe/V;
    if I<=3 && ps<=Pc, vv='OK on 3A';
    elseif ps<=Pc, vv='MOTOR OK, 3A PWM TRIPS - need 20A';
    elseif ps<=Pp, vv='PEAK only, 3A TRIPS';
    else, vv='OVERLOAD';
    end
    fprintf('%5d | %4.0f | %5.1f | %6.1f  | %5.3f | %5.3f | %5.1f | %s\n', r, o*R, pa, ps, tl, ta, I, vv);
end
% Operating point: Tavail=Tload
rr=1000:100:n0-100;
f=arrayfun(@(r) Ts*(1-r/n0)-(PcutN+nL*Kgeo*om(r)^3)/om(r), rr);
op=NaN; for k=numel(rr):-1:1, if f(k)>0, op=rr(k); break; end, end
o=om(op); pa=nL*Kgeo*o^3; ps=PcutN+pa; pe=ps/eta;
fprintf('\nPredicted no-limit operating point: ~%d rpm, Vtip %.0f m/s, Pshaft %.0f W, I %.1f A\n', op, o*R, ps, pe/V);
fprintf('With SEN51 3A cap (~36W elec -> ~22W shaft): motor chokes at ~4000 rpm, Vtip ~42 m/s -> ragged tear, PWM burns.\n');
fprintf('TO MAKE SURE, simulate/measure: (1) rpm under load, (2) amps vs 3A/20A, (3) Vtip>=50, (4) 5-min temp.\n');
% Plot
figure('Name','SP Electron check');
rpms=2000:250:12000; o2=rpms*2*pi/60; pa2=nL*Kgeo*o2.^3;
subplot(2,1,1); plot(rpms, o2*R,'b-', 'LineWidth',1.6); grid on; hold on;
yline(35,'r--'); yline(50,'m--'); xline(op,'g--','op');
xlabel('rpm'); ylabel('Vtip m/s'); title('Tip speed - SP 12000rpm motor');
subplot(2,1,2); plot(rpms, PcutN+pa2,'b-', 'LineWidth',1.6); grid on; hold on;
plot(rpms, PcutH+pa2,'r--'); yline(Pc,'g--','cont 80W'); yline(Pp,'m--','peak 140W');
xlabel('rpm'); ylabel('shaft W'); title('Power - 3A PWM cannot supply this');
