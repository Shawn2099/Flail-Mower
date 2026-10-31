% *** SUPERSEDED 2026-10-31: uses early layout assumptions (idler 182/ rollers +-220, M=326 kg). Current values: Rp=0.0971, flat run 0.776 m, design mass 352 kg -> run sim_uc_v4.m ***
% SIM_TRACK_MOTOR_MATRIX  3 tracks x grade{5,10} x speed{0.4,0.5} x motor{350,550 W} (per side).
% Base MATLAB. Reuses repo track specs (common/specs, track_180x60x37/specs) and the repo's
% MBS-paper soil table (sim_motor_track_4combo.m). Track 150x60x37 = ACETRAX PDF p.2 row
% (W150 P60 IGB24 OGB60 C26 D24.5); link count 37 is the repo's size code, NOT in the PDF.
% Because the motor is power-limited, wheel torque at rated point = P*eta*Rp/v (gear ratio
% G is then set so rated rpm gives speed v). Peak = overload*P (assumed 1.5x, few seconds).
% ASSUMPTIONS (placeholders until measured): mu_rr, mu_t, eta, deck mass, overload.
clear; clc;
here = fileparts(mfilename('fullpath'));
root = fileparts(fileparts(here));
addpath(fullfile(root,'common','specs')); addpath(fullfile(root,'track_180x60x37','specs'));
t72 = track_180x72x37(); t60 = track_180x60x37();
t15 = t60; t15.W_mm = 150; t15.name = 'ACETRAX 150x60x37 (PDF row; mass scaled)';
T = {t72, t60, t15}; tn = {'180x72x37','180x60x37','150x60x37'};
Zt = [9 10 10];                         % sprocket teeth (72z9 frozen; z10 per 180x60 sims)
g = 9.81; eta = 0.90*0.95; ovl = 1.5; SF = 1.2;
M = 326;  Bg = 0.86;                    % design mass [kg] (incl 1.25 margin), gauge [m]
mu_rr = [0.10 0.15]; mu_t_max = 0.65; vturn = 0.3;
soil_c = [1.7e3 4.14e3]; soil_phi = [29 13]; soilname = {'sandy loam','clay'};  % repo MBS table
motorsW = [350 550]; fails = 0;
fprintf('M=%d kg  gauge=%.2f m  eta=%.3f overload=%.1fx  mu_t_max=%.2f (Wong fit, pivot)\n\n',M,Bg,eta,ovl,mu_t_max);
for k = 1:3
  Tr = T{k}; P = Tr.pitch_mm/1000; N = Tr.n_links; Wm = Tr.W_mm/1000;
  Rp = P/sin(pi/Zt(k))/2; Ld = P*N; Ls = (Ld-2*pi*Rp)/2; A = 2*Ls*Wm;
  W = M*g; mt = mu_t_max/0.925;                    % spin turn: R=0
  fprintf('--- %s: pitch %d z%d Rp=%.1f mm  contact L=%.3f m  A=%.3f m2  p=%.1f kPa\n',tn{k},Tr.pitch_mm,Zt(k),Rp*1000,Ls,A,W/A/1000);
  for rr = mu_rr
    for th = [5 10]
      for v = [0.4 0.5]
        F = (rr*cosd(th)+sind(th))*W/2; Pcont = F*v/eta*SF;         % motor shaft W needed
        Tt = (rr*W/2 + mt*W*Ls/(4*Bg))*Rp; Pt = Tt*vturn/Rp/eta;   % pivot-turn peak shaft W
        N_ = W*cosd(th); trac = zeros(1,2);
        for s = 1:2, trac(s) = 0.85*(soil_c(s)*A + N_*tand(soil_phi(s))) >= (rr*cosd(th)+sind(th))*W; end
        res = '';
        for Pm = motorsW
          ok = (Pcont <= Pm) && (Pt <= ovl*Pm);
          res = [res sprintf(' %dW:%s', Pm, ternary_(ok))]; %#ok<AGROW>
        end
        fprintf('mu_rr %.2f th%2d v%.1f | cont %4.0fW  turnpk %4.0fW  traction[loam %d clay %d] |%s\n',rr,th,v,Pcont,Pt,trac(1),trac(2),res);
      end
    end
  end
end
fprintf('\nPASS = continuous<=rated AND turn-peak<=%.1fx rated. Traction 1=ok (85%% of Mohr-Coulomb limit).\n',ovl);
function s = ternary_(c), if c, s='PASS'; else, s='FAIL'; end, end
