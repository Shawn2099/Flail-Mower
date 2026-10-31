% V2_PDE_KT  Task T1: 2D plane-stress Kt at holes/slots (PDE Toolbox), then
% restate V2 margins with peaks. Units SI (m, Pa). Nominal load 1 unit tension.
clear; clc;
Kt_hole = kt_hole();      % D26-class hole in strip
Kt_slot = kt_slot();      % obround slot end (idler/UCFL slots)
fprintf('Kt hole=%.2f slot-end=%.2f\n', Kt_hole, Kt_slot);
% apply to V2 nominals (burst allow 225 = 0.9*yield for rare peak)
nom = [113.6 77.5 70.8];            % beam, flange, plate-panel MPa
Kt  = [1.0 Kt_hole Kt_slot];        % beam critical section has no holes
peak = nom.*Kt;
for i=1:3
  s='PASS'; if peak(i)>225, s='REVIEW'; end
  fprintf('peak%d = %.0fMPa (allow 225 rare-peak) %s\n', i, peak(i), s);
end
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
