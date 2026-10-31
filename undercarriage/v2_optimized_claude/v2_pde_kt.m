% V2_PDE_KT  Task T1: 2D plane-stress Kt at holes/slots (PDE Toolbox), then
% restate V2 margins with peaks. Units SI (m, Pa). Nominal load 1 unit tension.
clear; clc;
Kt_hole = kt_hole();      % D26-class hole in strip
Kt_slot = kt_slot();      % obround slot end (idler/UCFL slots)
fprintf('Kt hole=%.2f slot-end=%.2f\n', Kt_hole, Kt_slot);
% apply Kt where a free hole/slot edge carries net section:
% beam midspan (no hole) and plate panel at slot end.
nom = [113.6 70.8];                 % beam, plate-panel MPa
Kt  = [1.0 Kt_slot];
peak = nom.*Kt;
for i=1:2
  s='PASS'; if peak(i)>225, s='REVIEW'; end
  fprintf('peak%d = %.0fMPa (allow 225 rare-peak) %s\n', i, peak(i), s);
end
% Flange joint: 4xM12 80Nm friction-grip. If it does not slip, the bolt
% holes are not in bearing and the free-hole Kt does not apply (the 248MPa
% figure is a gross-section upper bound, not a joint stress).
Tb=80; K=0.2; d=0.012; Fcl=Tb/(K*d); n=4; mu=0.3; V=1670;
SF=mu*n*Fcl/V;
s='PASS'; if SF<1.5, s='REVIEW'; end
fprintf('flange grip SF=%.1f (V=%.0fN, 4xM12@80Nm, mu0.3) %s; hole-Kt N/A (no slip)\n',SF,V,s);
fprintf('T1 DONE\n');
function Kt = kt_hole()
  model = createpde('structural','static-planestress');
  L=0.2; W=0.05; r=0.007;
  R=[3,4,-L/2,L/2,L/2,-L/2,-W/2,-W/2,W/2,W/2]';
  C=[1,0,0,r,zeros(1,6)]';
  g=decsg([R,C],'R-C',char('R','C')');
  geometryFromEdges(model,g);
  structuralProperties(model,'YoungsModulus',200e9,'PoissonsRatio',0.3);
  structuralBC(model,'Edge',4,'Constraint','fixed');
  structuralBoundaryLoad(model,'Edge',2,'SurfaceTraction',[1e6;0]);
  generateMesh(model,'Hmax',r/3);
  Rr=solve(model);
  Kt=max(Rr.VonMisesStress)/1e6;
end
function Kt = kt_slot()
  model = createpde('structural','static-planestress');
  L=0.2; W=0.05; sw=0.015; sl=0.05;  % slot width/length (UCFL-class)
  R=[3,4,-L/2,L/2,L/2,-L/2,-W/2,-W/2,W/2,W/2]';
  B=[3,4,-sl/2,sl/2,sl/2,-sl/2,-sw/2,-sw/2,sw/2,sw/2]';
  C1=[1,-sl/2,0,sw/2,zeros(1,6)]'; C2=[1,sl/2,0,sw/2,zeros(1,6)]';
  g=decsg([R,B,C1,C2],'R-(B+C1+C2)',char('R','B','C1','C2')');
  geometryFromEdges(model,g);
  structuralProperties(model,'YoungsModulus',200e9,'PoissonsRatio',0.3);
  structuralBC(model,'Edge',4,'Constraint','fixed');
  structuralBoundaryLoad(model,'Edge',2,'SurfaceTraction',[1e6;0]);
  generateMesh(model,'Hmax',sw/6);
  Rr=solve(model);
  Kt=max(Rr.VonMisesStress)/1e6;
end
