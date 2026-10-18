%% sim_775_torque_types.m
% Torque experienced in cutting - research + sweep of grass/line types
% Base MATLAB only.
clear; clc;
fprintf('\n=== CUTTING TORQUE - RESEARCH + TYPE SWEEP ===\n');
fprintf('Research note:\n');
fprintf(' - Repo light grass Es=800 J/m2 [500-1500] (blunt impact, incl. inefficiency)\n');
fprintf(' - Theory single-blade shear ~30 J/m2 is ideal sharp; trimmer tears at 10-30x due to\n');
fprintf('   high-speed impact, recut, air pumping. Hence 500-1500 light, 2000-3000 dense/wet.\n');
fprintf(' - Mower lit: 0.7 kW @0.5m/0.6m/s ~ 2300 J/m2 dense; 250-500W trimmers @0.25m confirm Es~1000-3000.\n');
fprintf(' - Torque on trimmer T=(Es*W*v + Paero)/om. Paero often > Pcut at high rpm.\n');

% Base head
r0=30e-3; L=70e-3; R=r0+L; W=2*R; v=0.15;
rhoA=1.225;
% Grass types [name Es]
G={ 'light lawn (mowed, dry)',800; 'medium (weekly, 10cm)',1500; ...
    'dense tall (15-20cm)',2500; 'wet heavy',3500; 'weeds/brush stems',6000};
% Line types [name d Cd]
Ln={ '1.6mm round',1.6e-3,1.1; '2.0mm round',2.0e-3,1.1; '2.4mm square',2.4e-3,1.3};
rpmT=[6500 9600]; % 12V-generic op vs SP-12000 op
for k=1:numel(rpmT)
  r=rpmT(k); o=r*2*pi/60;
  fprintf('\n--- @%d rpm, R=100mm, v=0.15 m/s, W=0.20m ---\n', r);
  fprintf('%-26s | %-12s | Pcut | Paero | Pshaft | Tcut-only | Ttotal\n', 'grass','line');
  for gi=1:size(G,1)
    Es=G{gi,2};
    Pc=Es*W*v;
    for li=1:size(Ln,1)
      d=Ln{li,2}; Cd=Ln{li,3};
      Kg=rhoA*Cd*d*(R^4-r0^4)/8; pa=2*Kg*o^3;
      ps=Pc+pa; Ttot=ps/o; Tc=Pc/o;
      fprintf('%-26s | %-12s | %4.0f | %4.1f | %5.1f | %5.3f   | %5.3f %s\n', ...
        G{gi,1}, Ln{li,1}, Pc, pa, ps, Tc, Ttot, torqueFlag(Ttot));
    end
  end
end
fprintf('\nFlag: OK<=0.08 (775 cont) | PEAK 0.08-0.15 (short duty) | STALL>0.15 (droop/burn @12V)\n');
fprintf('\nLine-type note: thicker/square line raises Paero ~d*Cd (+50-95%% 1.6->2.4sq) and holds energy\n');
fprintf('better in weeds but overloads 775 faster. For POC stay 1.6mm round.\n');
function f=torqueFlag(T)
if T<=0.08, f='OK'; elseif T<=0.15, f='PEAK'; else, f='STALL'; end
end
