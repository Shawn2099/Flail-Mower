%% build_drum_2J.m — 2J OPPOSING rotor: 10 positions x 2 (180 deg) = 20 J blades.
% Same drum/discs/shaft/fins as MVP; J hooks (125 deg) modeled as shank + leg.
% Outputs: drum_rotor_2J.stl, rotor_3D_2J.png, coverage_2J.png. Base MATLAB only.
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));
addpath(fullfile(thisdir,'specs'));
cadout = fullfile(thisdir,'cad'); if ~exist(cadout,'dir'), mkdir(cadout); end

bJ = blade_jtype_mulcher();
drum = drum_50NB_medium();
C = config_2J_opposing();

RO = drum.OD_m/2; RI = drum.ID_m/2; LD = 0.500;
PIN_R = RO + 0.020;
xs = C.xs_mm/1000 - 0.25;   % centered coords
NSEG = 48;
F = zeros(0,3); V = zeros(0,3); mass = 0;

[f,v] = cylX(RO,-LD/2,LD/2,NSEG,true);  [F,V] = addPart(F,V,f,v);
mass = mass + pi*(RO^2-RI^2)*LD*7850;
for sgn = [-1 1]
    [f,v] = cylX(0.070, sgn*LD/2 + (sgn<0)*-0.008, sgn*LD/2 + (sgn>0)*0.008, NSEG, true);
    [F,V] = addPart(F,V,f,v);
end
mass = mass + 2*pi*0.07^2*0.008*7850;
[f,v] = cylX(0.0125,-0.35,0.35,24,true); [F,V] = addPart(F,V,f,v);
mass = mass + pi*0.0125^2*0.7*7850;

FB = zeros(0,3); VB = zeros(0,3);
for p = 1:C.nPos
    for j = 1:C.perPos
        ang = C.base_angles_deg(p) + (j-1)*180;
        c = cosd(ang); s = sind(ang);
        [f,v] = box3(xs(p), 0.049, 0, 0.050, 0.042, 0.006);
        v = rotX(v,c,s); [F,V] = addPart(F,V,f,v);
        mass = mass + 0.050*0.042*0.006*7850;
        [f,v] = cylZ(0.0085,-0.006,0.026,16,PIN_R);
        v = rotX(v,c,s); v(:,1)=v(:,1)+xs(p); [F,V] = addPart(F,V,f,v);
        mass = mass + pi*0.0085^2*0.032*7850;
        [f,v] = cylZ(0.014,0.026,0.040,6,PIN_R);
        v = rotX(v,c,s); v(:,1)=v(:,1)+xs(p); [F,V] = addPart(F,V,f,v);
        mass = mass + pi*0.014^2*0.014*7850*0.8;
        % J blade: shank (radial) + leg hooked 125 deg (55 off radial, trailing +tang)
        [f,v] = box3(0, PIN_R+0.030, 0.014, bJ.width_m, 0.060, 0.008);
        v = rotX(v,c,s); v(:,1)=v(:,1)+xs(p); [FB,VB] = addPart(FB,VB,f,v);
        [f,v] = box3(0, 0, 0, bJ.width_m, 0.057, 0.008);
        v = rotX(v, cosd(55), sind(55));
        v(:,2)=v(:,2)+PIN_R+0.060+0.0285*cosd(55); v(:,3)=v(:,3)+0.014+0.0285*sind(55);
        v = rotX(v,c,s); v(:,1)=v(:,1)+xs(p); [FB,VB] = addPart(FB,VB,f,v);
        mass = mass + bJ.mass_kg;
    end
end
Fs = [F; FB+size(V,1)]; Vs = [V; VB];
maxR = max(sqrt(Vs(:,2).^2+Vs(:,3).^2));
omW = C.rpm_work*2*pi/60; omC = C.rpm_cap*2*pi/60;
tipW = omW*(PIN_R+0.104);
Fc = bJ.mass_kg*omC^2*(PIN_R+bJ.pivot_to_cg_m);
sig = Fc*0.014/(pi*0.017^3/32)/1e6;
fprintf('\n=== 2J ROTOR CHECKS ===\n');
fprintf('20 J blades (10 pos x 2 @180) | mass %.1f kg | maxR %.1f mm\n', mass, maxR*1000);
fprintf('Tip %.1f m/s @%d | pin %.0f/180 MPa @cap | balance: perfect pairs\n', tipW, C.rpm_work, sig);

stlwrite(triangulation(Fs,Vs), fullfile(cadout,'drum_rotor_2J.stl'));
fprintf('Wrote drum_rotor_2J.stl (%d triangles)\n', size(Fs,1));

figure('Name','2J rotor');
patch('Faces',Fs,'Vertices',Vs,'FaceColor',[0.72 0.42 0.18], ...
    'EdgeColor','none','FaceLighting','gouraud');
camlight; lighting gouraud; axis equal off; view(-35,20);
title('2J rotor: 50NB drum, 20 J-hooks, 10 pos x 180 deg');
saveas(gcf, fullfile(thisdir,'rotor_3D_2J.png'));
fprintf('Wrote rotor_3D_2J.png\n');

%% helpers
function [F,V] = box3(cx,cy,cz,sx,sy,sz)
V = [cx-sx/2 cy-sy/2 cz-sz/2; cx+sx/2 cy-sy/2 cz-sz/2; cx+sx/2 cy+sy/2 cz-sz/2; cx-sx/2 cy+sy/2 cz-sz/2; ...
     cx-sx/2 cy-sy/2 cz+sz/2; cx+sx/2 cy-sy/2 cz+sz/2; cx+sx/2 cy+sy/2 cz+sz/2; cx-sx/2 cy+sy/2 cz+sz/2];
F = [1 2 3; 1 3 4; 5 7 6; 5 8 7; 1 5 6; 1 6 2; 4 3 7; 4 7 8; 1 4 8; 1 8 5; 2 6 7; 2 7 3];
end
function [F,V] = cylX(r,x1,x2,n,caps)
th = 2*pi*(0:n-1)/n; y = r*cos(th); z = r*sin(th);
V = [x1*ones(n,1) y' z'; x2*ones(n,1) y' z'];
F = zeros(0,3);
for k = 1:n
    k2 = mod(k,n)+1;
    F = [F; k k2 k2+n; k k2+n k+n]; %#ok<AGROW>
end
if caps
    V = [V; x1 0 0; x2 0 0]; c1 = 2*n+1; c2 = 2*n+2;
    for k = 1:n
        k2 = mod(k,n)+1;
        F = [F; c1 k2 k; c2 k+n k2+n]; %#ok<AGROW>
    end
end
end
function [F,V] = cylZ(r,z1,z2,n,yc)
th = 2*pi*(0:n-1)/n; x = r*cos(th); y = yc + r*sin(th);
V = [x' y' z1*ones(n,1); x' y' z2*ones(n,1)];
F = zeros(0,3);
for k = 1:n
    k2 = mod(k,n)+1;
    F = [F; k k+n k2+n; k k2+n k2]; %#ok<AGROW>
end
end
function v = rotX(v,c,s)
y = v(:,2); z = v(:,3);
v(:,2) = c*y - s*z; v(:,3) = s*y + c*z;
end
function [F,V] = addPart(F,V,f,v)
off = size(V,1); F = [F; f+off]; V = [V; v];
end
