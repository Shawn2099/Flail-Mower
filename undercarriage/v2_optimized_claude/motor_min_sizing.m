% *** SUPERSEDED 2026-10-31: uses early layout assumptions (idler 182/ rollers +-220, M=326 kg). Current values: Rp=0.0971, flat run 0.776 m, design mass 352 kg -> run sim_uc_v4.m ***
% MOTOR_MIN_SIZING  smallest per-side motor for the v2_optimized_claude track drive.
% Base MATLAB only. Run: run('<this file>'). All inputs are PLACEHOLDERS to be replaced by
% measured values (mu_rr, mu_t, mass) - see ASSUMPTIONS below. Per-side values.
clear; clc;
g=9.81; Rp=0.10526;            % sprocket pitch radius [m]
L=1.0013;                      % ground contact length [m] (sim_v2)
Bg=0.86;                       % track-centre gauge [m] (overall ~1166 mm)
eta=0.90*0.95;                 % planetary x chain (ASSUMED, unverified)
mu_rr=0.15;                    % motion resistance coeff, wet soil (ASSUMED)
mu_t=0.5;                      % lateral resistance coeff, pivot (ASSUMED, unverified)
SF=1.20;                       % continuous margin on thermal sizing
fprintf('ASSUMPTIONS: eta=%.3f mu_rr=%.2f mu_t=%.2f L=%.3f B=%.2f SF=%.2f\n\n',eta,mu_rr,mu_t,L,Bg,SF);

fprintf('=== CONTINUOUS motor shaft power per side [W] (straight, with grade) ===\n');
fprintf('%6s %6s %6s | %8s %8s %8s\n','M kg','grade','v m/s','wheelNm','wheel W','motor W');
for M=[200 261 326]
 for th=[0 5 10]
  for v=[0.3 0.4 0.5]
   W=M*g; F=(mu_rr*cosd(th)+sind(th))*W/2; Tw=F*Rp; Pw=F*v; Pm=Pw/eta*SF;
   fprintf('%6d %6d %6.2f | %8.1f %8.0f %8.0f\n',M,th,v,Tw,Pw,Pm);
  end
 end
end

fprintf('\n=== TURN PEAK (outer track), torque Nm and motor-shaft power at turn speed ===\n');
fprintf('%6s %6s %6s | %8s %10s\n','M kg','B m','mu_t','wheelNm','motorW@0.3');
for M=[261 326]
 for B=[0.52 0.86]
  for mt=[0.4 0.5 0.6]
   W=M*g; T=(mu_rr*W/2+mt*W*L/(4*B))*Rp; Pm=T*(0.3/Rp)/eta;
   fprintf('%6d %6.2f %6.1f | %8.0f %10.0f\n',M,B,mt,T,Pm);
  end
 end
end

fprintf('\nNOTE: arc turns do NOT lower outer-track torque in this model (same Mr/B term);\n');
fprintf('only mu_t drops with turning radius (Wong fit, being verified). L/B is the lever.\n');
