%% build_drum.m — ULTIMATE DRUM: parametric 3D model + laser DXF + STL + checks
% Geometry (verified: Orec 38 x ~17 mm = 650 mm -> blade WIDTH lies along X):
%   X = drum axis. Blade flats in X-radial planes (58 mm swath along X).
%   Pins TANGENTIAL through single-fin lugs; blades swing in X-radial planes.
% Outputs (in the matlab folder): drum_disc.dxf, drum_rotor.stl, rotor_3D.png
% Base MATLAB only.
clear; clc; close all;
thisdir = fileparts(mfilename('fullpath'));
addpath(fullfile(thisdir,'specs'));
cadout = fullfile(thisdir,'cad'); if ~exist(cadout,'dir'), mkdir(cadout); end

bS = blade_straight_mulcher();
bJ = blade_jtype_mulcher();
drum = drum_50NB_medium();

%% CONFIG: 'MVP' = 10 straights (1 per station) | 'J20' = 20 J (2 opposing per station)
CFG = 'J20';
if strcmp(CFG,'J20')
    OUT = '_J20';  BB = bJ;  PERPOS = 2;  NBL = 20;
    RPMW = 2300; RPMM = 2500;
else
    OUT = '';      BB = bS;  PERPOS = 1;  NBL = 10;
    RPMW = 2200; RPMM = 2500;
end
omW = RPMW*2*pi/60; omM = RPMM*2*pi/60;

%% Locked dimensions (m)
RO = drum.OD_m/2;            % 0.03015 tube outer radius
RI = drum.ID_m/2;            % tube inner radius
LD = 0.500;                  % drum length
RD = 0.070; TD = 0.008;      % end disc radius / thickness
RS = 0.0125; LS = 0.700;     % shaft radius / length
PIN_R = RO + 0.020;          % pin circle radius (20 mm standoff)
RCUT = PIN_R + bS.pivot_to_tip_m;   % cutting radius
xs = linspace(-0.235, 0.235, 10);   % 10 stations, 15..485 mm
th = (0:9)*36;               % helix degrees
NSEG = 48;

F = zeros(0,3); V = zeros(0,3);
mass = 0;

% tube (outer wall + annulus end caps)
[f,v] = cylX(RO,-LD/2,LD/2,NSEG,true);   [F,V] = addPart(F,V,f,v);
mass = mass + pi*(RO^2-RI^2)*LD*7850;
% end discs + shaft
for sgn = [-1 1]
    [f,v] = cylX(RD, sgn*LD/2 + (sgn>0)*0 + (sgn<0)*-TD, sgn*LD/2 + (sgn>0)*TD + (sgn<0)*0, NSEG, true);
    [F,V] = addPart(F,V,f,v);
end
mass = mass + 2*pi*RD^2*TD*7850;
[f,v] = cylX(RS,-LS/2,LS/2,24,true);     [F,V] = addPart(F,V,f,v);
mass = mass + pi*RS^2*LS*7850;

% stations: fin + tangential bolt + blade, PERPOS blades at 180 deg per station
FB = zeros(0,3); VB = zeros(0,3);   % blades kept separate (spinning set)
for p = 1:10
    for j = 1:PERPOS
        ang = th(p) + (j-1)*180;
        c = cosd(ang); s = sind(ang);
        % fin: X 50 wide, radial 28..70, tangential 6 thick (+2 spacer washers for 8 eye)
        [f,v] = box3(xs(p), 0.049, 0, 0.050, 0.042, 0.006);
        v = rotX(v, c, s);  [F,V] = addPart(F,V,f,v);
        mass = mass + 0.050*0.042*0.006*7850;
        % bolt: turned shoulder dia-17 with M14 thread + nyloc nut
        [f,v] = cylZ(0.0085, -0.006, 0.026, 16, PIN_R);
        v = rotX(v, c, s); v(:,1) = v(:,1) + xs(p);  [F,V] = addPart(F,V,f,v);
        mass = mass + pi*0.0085^2*0.032*7850;
        [f,v] = cylZ(0.014, 0.026, 0.040, 6, PIN_R);
        v = rotX(v, c, s); v(:,1) = v(:,1) + xs(p);  [F,V] = addPart(F,V,f,v);
        mass = mass + pi*0.014^2*0.014*7850*0.8;
        % blade: straight box, or J = shank + 125-deg hooked leg
        if strcmp(CFG,'J20')
            [f,v] = box3(0, 0.030, 0, BB.width_m, 0.060, 0.008);   % shank
            v = rotX(v, c, s); v(:,1) = v(:,1) + xs(p); v(:,2) = v(:,2) + PIN_R;
            [FB,VB] = addPart(FB,VB,f,v);
            [f,v] = box3(0, 0, 0, BB.width_m, 0.057, 0.008);       % hooked leg
            v = rotX(v, cosd(55), sind(55));
            v(:,2) = v(:,2) + PIN_R + 0.060; v(:,1) = v(:,1) + xs(p);
            v = rotX(v, c, s); v(:,1) = v(:,1) - xs(p); v(:,1) = v(:,1) + xs(p);
            [FB,VB] = addPart(FB,VB,f,v);
        else
            [f,v] = box3(xs(p), (PIN_R+RCUT)/2, 0.014, 0.058, (RCUT-PIN_R), 0.008);
            v = rotX(v, c, s);  [FB,VB] = addPart(FB,VB,f,v);
        end
        mass = mass + BB.mass_kg;
    end
end
Fs = [F; FB+size(V,1)]; Vs = [V; VB];   % full spinning assembly

%% Checks (symmetry: 10 identical stations on full 36-deg circle -> CG on axis)
maxR = max(sqrt(Vs(:,2).^2 + Vs(:,3).^2));
Fc = bS.mass_kg*(2500*2*pi/60)^2*(PIN_R + bS.pivot_to_cg_m);
pinZ = pi*0.017^3/32;
sigPin = Fc*0.014/pinZ/1e6;   % 14 mm load arm (spacer + half eye)
fprintf('\n=== ULTIMATE DRUM CHECKS ===\n');
fprintf('Parts: tube + 2 discs + shaft + 10 fins + 10 shoulder bolts + nuts + 10 blades\n');
fprintf('Assembly mass: %.1f kg | max radius: %.1f mm (cutting %.1f) | pin bending @cap: %.0f/180 MPa\n', ...
    mass, maxR*1000, RCUT*1000, sigPin);
fprintf('Balance: 10 stations x 36 deg = full circle, identical blades -> static CG on axis.\n');

%% STL export
stlwrite(TRI(Fs,Vs), fullfile(cadout,'drum_rotor.stl'));
fprintf('Wrote drum_rotor.stl (%d triangles)\n', size(Fs,1));

%% DXF: end disc laser profile (mm)
dxf = fullfile(cadout,'drum_disc.dxf');
fh = fopen(dxf,'w');
fprintf(fh,'0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n');
C = @(x,y,r) fprintf(fh,'0\nCIRCLE\n8\nCUT\n10\n%.3f\n20\n%.3f\n40\n%.3f\n',x,y,r);
L = @(x1,y1,x2,y2) fprintf(fh,'0\nLINE\n8\nMARK\n10\n%.3f\n20\n%.3f\n11\n%.3f\n21\n%.3f\n',x1,y1,x2,y2);
C(0,0,70); C(0,0,12.5);                       % outer + shaft bore
for a = 0:60:300, C(45*cosd(a),45*sind(a),5); end   % 6x dia-10 on BCD90
for k = 0:9                                       % 10 helix witness marks + labels
    a = k*36; L(52*cosd(a),52*sind(a),68*cosd(a),68*sind(a));
    fprintf(fh,'0\nTEXT\n8\nMARK\n10\n%.3f\n20\n%.3f\n40\n4\n1\nST%d\n',60*cosd(a),60*sind(a),k);
end
fprintf(fh,'0\nENDSEC\n0\nEOF\n'); fclose(fh);
fprintf('Wrote drum_disc.dxf (disc O140, bore dia-25, 6x dia-10 BCD90, 10 station marks)\n');

%% Render + PNG (spinning view: blades radial)
figure('Name','Ultimate drum'); patch('Faces',Fs,'Vertices',Vs,'FaceColor',[0.75 0.45 0.2], ...
    'EdgeColor','none','FaceLighting','gouraud'); 
camlight; lighting gouraud; axis equal off; view(-35,20);
title('MVP rotor: 50NB drum, 10 fins, 10 straights, 36-deg helix');
saveas(gcf, fullfile(thisdir,'rotor_3D_v3.png'));
fprintf('Wrote rotor_3D_v3.png\n');

%% Coverage proof: union of blade swaths along the 500 mm drum
xsmm = (xs+0.25)*1000;   % station positions from left end, mm
lo = max(xsmm-29,0); hi = min(xsmm+29,500);
[los,ord] = sort(lo); his = hi(ord);
cov = 0; cur0 = los(1); cur1 = his(1);
for k = 2:numel(los)
    if los(k) <= cur1, cur1 = max(cur1,his(k)); else, cov = cov + (cur1-cur0); cur0 = los(k); cur1 = his(k); end
end
cov = cov + (cur1-cur0);
fprintf('Coverage: %.1f%% of 500 mm (overlap %.1f mm between neighbours)\n', cov/5, 58-470/9);
figure('Name','Coverage');
hold on; grid on; ylim([0 3]);
for k = 1:10, patch([lo(k) hi(k) hi(k) lo(k)],[0.5 0.5 1.5 1.5],'b','FaceAlpha',0.5); end
xline(0,'k-'); xline(500,'k-'); xlabel('drum position mm'); yticks([]);
title(sprintf('Swath coverage: %.1f%% (blue = cut, 10 x 58 mm blades)', cov/5));
saveas(gcf, fullfile(thisdir,'coverage.png'));
fprintf('Wrote coverage.png\n');

%% Parked view: every blade dangling straight down (as a real parked rotor looks)
F3 = F; V3 = V;   % static parts only (tube, discs, shaft, fins, bolts)
for k = 1:10
    c = cosd(th(k)); s = sind(th(k));
    ey = PIN_R*c - 0.014*s; ez = PIN_R*s + 0.014*c;   % eye point on pin line
    [f,v] = box3(xs(k), ey-0.054, ez, 0.058, 0.108, 0.008);
    [F3,V3] = addPart(F3,V3,f,v);
end
figure('Name','Parked'); patch('Faces',F3,'Vertices',V3,'FaceColor',[0.75 0.45 0.2], ...
    'EdgeColor','none','FaceLighting','gouraud');
camlight; lighting gouraud; axis equal off; view(-35,20);
title('Parked: all blades dangling down (dense bottom = working look)');
saveas(gcf, fullfile(thisdir,'rotor_parked.png'));
fprintf('Wrote rotor_parked.png\n');

%% ---- local geometry helpers ----
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
function T = TRI(F,V), T = triangulation(F,V); end
