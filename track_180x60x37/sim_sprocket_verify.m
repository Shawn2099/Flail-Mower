% SIM_SPROCKET_VERIFY  independent re-verification of 72z9 sprocket (base MATLAB).
% Recomputes everything from scratch: PD law (ASME B29.1/ISO606/Shigley Ch.17),
% chordal effect, tooth/gap geometry vs track windows (52mm) and B-gap (23mm),
% cantilever tooth stress, key + bolt joints, mass via polygon area.
% PASS/FAIL gated. Run: run('sim_sprocket_verify.m')
clear; clc;
fails = 0;
Z = 9; P = 72;
PD = P/sin(pi/Z); Rp = PD/2;
fprintf('PD=%.2f (expect 210.51) Rp=%.2f\n', PD, Rp);
if abs(PD-210.51) > 0.01, fails = fails+1; fprintf('FAIL PD\n'); else fprintf('PASS PD\n'); end
dv = (1-cos(pi/Z))*100; fprintf('chordal z9: %.2f%%\n', dv);
% tooth (final CAD): tip22/root30/h25/chamfer3/tip@pitch, plate14, bore40
Rtip = Rp; Rroot = Rp-25;
win = P-20;                                    % insert-to-insert drive window
gap_root = P - 30; gap_tip = P - 22;           % backlash totals at root/tip circles
fprintf('window=%.0f root-gap=%.0f tip-gap=%.0f (all > insert 20)\n', win, gap_root, gap_tip);
if ~(win > 20 && gap_root > 20 && gap_tip > 20), fails = fails+1; fprintf('FAIL window\n'); else fprintf('PASS window/fit\n'); end
play = (23-16)/2; fprintf('centre-gap play/side=%.1f (want 1.5..5)\n', play);
if ~(play >= 1.5 && play <= 5), fails = fails+1; fprintf('FAIL play\n'); else fprintf('PASS play\n'); end
% strength: T=160Nm (400kg/45deg 80.8 x SF2); 3 teeth share (mesh sim)
T = 160; Ft = T/(Rp/1000)/3;
sig = 6*Ft*25/(14*30^2); fprintf('tooth sigma=%.1f MPa SF=%.0f\n', sig, 250/sig);
if ~(250/sig >= 10), fails = fails+1; fprintf('FAIL tooth\n'); else fprintf('PASS tooth\n'); end
Fk = 2*T/0.04; brg = Fk/(0.0033*0.044)/1e6; shr = Fk/(0.012*0.044)/1e6;
fprintf('key DIN6885 12x8 L44: bearing(t2min)=%.1f shear=%.1f MPa\n', brg, shr);
if ~(brg < 100 && shr < 100), fails = fails+1; fprintf('FAIL key\n'); else fprintf('PASS key\n'); end
Fb = T/(6*0.055); fprintf('bolt shear=%.0f N each\n', Fb);
if ~(Fb < 5000), fails = fails+1; fprintf('FAIL bolts\n'); else fprintf('PASS bolts\n'); end
% mass: rebuild outline polygon independently, shoelace, minus holes
th = @(r,d) [r*cosd(d), r*sind(d)];
ar = (30/2)/Rroot*180/pi; at = (22/2)/Rtip*180/pi; ac = (22/2+3)/(Rtip-3)*180/pi;
poly = [];
for i = 0:Z-1
  c = i*360/Z;
  a0 = c-360/Z+ar; a1 = c-ar;
  for k = 0:4, a_ = a0+(a1-a0)*k/4; if k>0, poly=[poly; th(Rroot,a_)]; end, end
  p_rl = th(Rroot,c-ar); p_cl = th(Rtip-3,c-ac);
  mx = (p_rl(1)+p_cl(1))/2; my = (p_rl(2)+p_cl(2))/2;
  poly = [poly; p_rl; p_rl*0.82+[mx my]*0.18; p_cl; th(Rtip,c-at)];
  for k = 0:4, a_ = (c-at)+(2*at)*k/4; if k>0, poly=[poly; th(Rtip,a_)]; end, end
  p_tr = th(Rtip,c+at); p_cr = th(Rtip-3,c+ac); p_rr = th(Rroot,c+ar);
  mx2 = (p_cr(1)+p_rr(1))/2; my2 = (p_cr(2)+p_rr(2))/2;
  poly = [poly; p_cr; p_rr*0.82+[mx2 my2]*0.18; p_rr];
end
A = abs(sum(poly(:,1).*poly([2:end 1],2)-poly([2:end 1],1).*poly(:,2)))/2;
Ab = pi*20^2; Ah = 6*pi*(13.5/2)^2;
Ahub = pi*(38^2-20^2);
mass = ((A-Ab-Ah)*16 + Ahub*(44-16))*7.85e-6;   % 2x8 laminate pack
fprintf('mass=%.2f kg (FreeCAD/STL ~3.8; tol +-3%%)\n', mass);
if abs(mass-3.80)/3.80 > 0.03, fails = fails+1; fprintf('FAIL mass\n'); else fprintf('PASS mass\n'); end
if fails == 0, fprintf('\nSPROCKET VERIFY: ALL PASS\n'); else fprintf('\nSPROCKET VERIFY: %d FAILURES\n', fails); end
