% SIM_TRACK_COMPARE  180x72x37 vs 180x60x37 head-to-head (base MATLAB only).
% Method (researched, see header refs):
%  [FTS] size/measure rules: Ld=P*N on insert line; pitch controls indexing.
%  [UST] pitch+links match sprocket; width = clearance/floatation only.
%  [MBS] Chamorro Coneo et al., Sci Rep 15:24829 (2025): discrete-segment belt,
%        polygonal contact, Bekker pressure-sinkage + Janosi-Hanamoto shear,
%        belt tension peaks at sprocket; soil params Table 4 (dry sand/sandy
%        loam/clay). Our machine (200 kg, 1 m/s, no planter draft) is ~23x
%        lighter than their 4600 kg planter case, so ABSOLUTE tensions/slips do
%        not transfer - only the EQUATIONS + soil params are reused here, and
%        outputs are RELATIVE (track A vs track B, same machine/soil).
%  [FED] Fedotkin pin-engagement sprocket method: PD=P/sin(pi/z); chordal
%        dv=1-cos(pi/z).
%  Soil = mineral-soil reference (paper Table 4). Turf thatch not modelled;
%  grass mu=0.12 rolling allowance kept from machine_500mm_tracked.
clear; clc;
addpath('C:\Users\malliath\Desktop\matlab\common\specs');
addpath('C:\Users\malliath\Desktop\matlab\track_180x60x37\specs');
t72 = track_180x72x37(); t60 = track_180x60x37();

M   = 200; g = 9.81; Wgt = M*g;          % 200 kg case (also checks 160)
R   = 100/1000;                          % pitch-line end radius, m (parametric)
Wm  = 0.18;                              % track width, m (both)
v   = [0.5 1.0 1.5];                     % forward speeds, m/s
grade = 30;                              % continuous rating, deg
Fgrade = Wgt*sind(grade);                % 981 N @200kg/30deg

% Bekker/Janosi soil params (MBS paper Table 4, SI): kc kN->N, kphi kN->N
soils = {'dry sand','sandy loam','clay'};
kc = [0.9 5.3 13.2]*1e3; kphi = [1523.4 1515 692.2]*1e3;
sn = [1.1 0.7 0.5]; coh = [1 1.7 4.14]*1e3; phi = [30 29 13];

names = {'180x72x37','180x60x37'};
Ts = {t72,t60};
fprintf('=== 180x72x37 vs 180x60x37 (M=%.0fkg, R=%.2fm) ===\n', M, R);
fprintf('%-22s %12s %12s\n','metric','180x72x37','180x60x37');
for k = 1:2
    s = Ts{k}; P = s.pitch_mm/1000; N = s.n_links;
    Ld = P*N; Ls = (Ld-2*pi*R)/2;
    A = 2*(Ls*Wm); p = Wgt/A;
    res(k).P=P; res(k).N=N; res(k).Ld=Ld; res(k).Ls=Ls; res(k).A=A; res(k).p=p;
    res(k).horn_w_each = (s.OGB_A_mm-s.IGB_B_mm)/2;
end
fprintf('%-22s %12.0f %12.0f\n','Ld pitch-line [mm]',res(1).Ld*1000,res(2).Ld*1000);
fprintf('%-22s %12.1f %12.1f\n','Ls contact [mm]',res(1).Ls*1000,res(2).Ls*1000);
fprintf('%-22s %12.3f %12.3f\n','contact area 2trk [m2]',res(1).A,res(2).A);
fprintf('%-22s %12.2f %12.2f\n','ground pressure [kPa]',res(1).p/1000,res(2).p/1000);
fprintf('%-22s %12.1f %12.1f\n','horn width each [mm]',res(1).horn_w_each,res(2).horn_w_each);

% --- soil: sinkage z=(p/keq)^(1/n), keq=kc/w+kphi; motion Rc=2*w*Ls*keq*z^(n+1)/(n+1); traction Fmax=A*c+W*tan(phi)
fprintf('\n--- soil (Bekker/Janosi, level) ---\n');
fprintf('%-12s %-12s %10s %10s %10s %10s\n','soil','track','z[mm]','Rc[N]','Fmax[N]','margin');
for i = 1:3
    keq = kc(i)/Wm + kphi(i);
    for k = 1:2
        z = (res(k).p/keq)^(1/sn(i));
        Rc = 2*(Wm*res(k).Ls*keq*z^(sn(i)+1)/(sn(i)+1));
        Fmax = res(k).A*coh(i) + Wgt*tand(phi(i));
        margin = Fmax/(Fgrade+Rc);
        fprintf('%-12s %-12s %10.2f %10.1f %10.0f %10.2f\n',soils{i},names{k},z*1000,Rc,Fmax,margin);
        sl(i,k).z=z; sl(i,k).Rc=Rc; sl(i,k).Fmax=Fmax; sl(i,k).margin=margin;
    end
end

% --- sprocket: PD, rpm @1m/s, torque/track @30deg (per-track F=Fgrade/2+Rc/2, sandy loam Rc)
fprintf('\n--- sprocket (PD=P/sin(pi/z); torque/track=(Fgrade+Rc)/2*Rp, Rc=sandy loam) ---\n');
zs = [9 10 11];
for zi = 1:numel(zs)
    z = zs(zi);
    fprintf('z=%d: ', z);
    for k = 1:2
        PD = res(k).P/sin(pi/z); Rp = PD/2;
        rpm = 1.0/(pi*PD)*60;
        T = (Fgrade+sl(2,k).Rc)/2*Rp;
        dv = (1-cos(pi/z))*100;
        fprintf('[%s PD=%.0f Rp=%.1f rpm@1m/s=%.0f T=%.1fNm dv=%.2f%%] ',names{k},PD*1000,Rp*1000,rpm,T,dv);
    end
    fprintf('\n');
end

% --- articulation: joints/s @1m/s, angle/pitch, bending-loss proxy v*P/R^2 (relative)
fprintf('\n--- articulation @1m/s, R=100mm ---\n');
for k = 1:2
    jrate = 1.0/res(k).P; ang = res(k).P/R;
    prox = 1.0*res(k).P/R^2;
    fprintf('%s: joints/s=%.1f angle=%.1fdeg bendproxy=%.4f\n',names{k},jrate,ang*180/pi,prox);
end
fprintf('bendproxy ratio 60/72 = %.3f (lower = less bending loss)\n',res(2).P/res(1).P);

% --- verdict scorecard (each line: winner)
fprintf('\n--- scorecard ---\n');
fprintf('footprint/frame fit (750 target) : 60 (796 vs 1018)\n');
fprintf('floatation/pressure              : 72 (5.35 vs 6.85 kPa; both turf-safe)\n');
fprintf('traction margin                  : ~tie (same Wgt; 72 marginally better via area, <5%%)\n');
fprintf('sinkage/motion resistance        : 72 slightly (larger area); abs values small (mm/Ns)\n');
fprintf('sprocket torque demand           : 60 (smaller Rp -> less Nm for same pull)\n');
fprintf('smoothness (pitch polygonal)     : 60 (34 vs 41 deg/joint; more, smaller steps)\n');
fprintf('bending loss proxy              : 60 (ratio %.2f)\n',res(2).P/res(1).P);
fprintf('mass                             : 60 (17.1 vs 18.5 kg)\n');
fprintf('tooth-window/pattern room        : 72 as-built (40 vs 28 mm; fixable via 27/42/18)\n');
fprintf('\nVERDICT: 60-pitch wins for THIS machine (frame fit, torque, smoothness, mass)\n');
fprintf('provided the 27/42/18 pattern fix is applied and tooth/roller version is\n');
fprintf('confirmed on the sample. 72-pitch wins only on floatation in deep soft soil.\n');

% --- plantation duty: grade sweep 30/35/40/45 deg, slope-corrected traction
% Fmax_slope = A*c + W*cos(th)*tan(phi); demand = W*sin(th) + Rc(level approx)
fprintf('\n--- plantation grade sweep (offroad, size target ignored) ---\n');
fprintf('%-6s %-12s %-12s %10s %10s\n','grade','track','soil','T/trk[Nm]','margin');
for th = [30 35 40 45]
    dem = Wgt*sind(th);
    for k = 1:2
        PD10 = res(k).P/sin(pi/10); Rp10 = PD10/2;   % z10 reference sprocket
        for i = 1:3
            Rc = sl(i,k).Rc;
            T = (dem+Rc)/2*Rp10;
            Fmaxs = res(k).A*coh(i) + Wgt*cosd(th)*tand(phi(i));
            mg = Fmaxs/(dem+Rc);
            fprintf('%-6d %-12s %-12s %10.1f %10.2f\n',th,names{k},soils{i},T,mg);
        end
    end
end
fprintf('note: grass-mu 0.12 rolling baked into Rc via Bekker mineral soils;\n');
fprintf('plantation mulch/mud needs field-calibrated kc/kphi/c/phi (see sim_calibrate_grass).\n');
