% SIM_MOTOR_TRACK_4COMBO  2 Mecwin traction motors x 2 track sizes: max gradient.
% Motors (nameplate, user-supplied screenshots):
%   1kW:   1000W @3000rpm, max 3300rpm, stall 23Nm @250rpm (1kw bldc.png)
%   1.2kW: 1200W @3300rpm, max 3500rpm, stall 25Nm @250rpm (Screenshot_...225138)
%   Stall figures = burst anchor at low speed (separate drivers, NOT the 300A mower unit).
% Tracks: 180x72x37 vs 180x60x37 (PDF rows, R=100mm, z10 sprocket reference).
% External reduction G is a DESIGN variable here (user: different ratios per motor):
%   T_wheel_burst = stall*G*0.95; T_wheel_cont = (P_rated/rated_w)*G*0.95.
%   Best G = maximises overall gradient subject to top speed >= 1.5 m/s.
% Limits per combo: traction (Janosi slope-corrected) / burst torque / cont torque
% (sustained) / cont power at 0.5 & 1.0 m/s / 50deg scan cap. Soil = MBS paper
% Table 4 mineral reference (plantation mulch/mud needs field calibration).
% Base MATLAB only.
clear; clc;
addpath('C:\Users\malliath\Desktop\matlab\common\specs');
addpath('C:\Users\malliath\Desktop\matlab\track_180x60x37\specs');
m1k = motor_Mecwin_BLDC_1p0kW(); m2k = motor_Mecwin_BLDC_1p2kW();
t72 = track_180x72x37(); t60 = track_180x60x37();
g = 9.81; R = 0.10; eta_g = 0.95; eta_d = 0.85;
Ms = [200 400]; Vs = [0.5 1.0];
soils = {'dry sand','sandy loam','clay'};
kc = [0.9 5.3 13.2]*1e3; kphi = [1523.4 1515 692.2]*1e3;
sn = [1.1 0.7 0.5]; coh = [1 1.7 4.14]*1e3; phi = [30 29 13];
Mots = {m1k, m2k}; Trks = {t72, t60};
mnames = {'1kW','1.2kW'}; tnames = {'180x72x37','180x60x37'};
Gs = [2.5 3 4 5 6 8 10 12 15 20];
thscan = 0:0.25:50;

fprintf('=== 4-combo max gradient (torque | traction | power) ===\n');
for mi = 1:2
    Mo = Mots{mi};
    Tc_burst = Mo.stall_torque_Nm;
    Tc_cont  = Mo.rated_power_W/(Mo.rated_speed_rpm*2*pi/60);
    for ki = 1:2
        Tr = Trks{ki}; P = Tr.pitch_mm/1000; N = Tr.n_links;
        Wm = Tr.W_mm/1000; Ld = P*N; Ls = (Ld-2*pi*R)/2; A = 2*Ls*Wm;
        PD = P/sin(pi/10); Rp = PD/2;
        for msi = 1:2
            M = Ms(msi); W = M*g;
            for si = 1:3
                keq = kc(si)/Wm + kphi(si);
                % traction-limited grade (motor-independent)
                th_t = 0;
                for th = thscan
                    p = W*cosd(th)/A; z = (p/keq)^(1/sn(si));
                    Rc = 2*(Wm*Ls*keq*z^(sn(si)+1)/(sn(si)+1));
                    Fmax = A*coh(si) + W*cosd(th)*tand(phi(si));
                    if Fmax >= W*sind(th)+Rc, th_t = th; else break; end
                end
                % sweep G
                best = struct('th',-1,'G',NaN,'bind','');
                for G = Gs
                    Twb = Tc_burst*G*eta_g; Twc = Tc_cont*G*eta_g;
                    vtop = (Mo.max_speed_rpm/G)*(2*pi/60)*Rp;
                    if vtop < 1.5 || vtop > 3.5, continue; end   % sane tracked-mower envelope
                    th_b = 0; th_c = 0;
                    for th = thscan
                        p = W*cosd(th)/A; z = (p/keq)^(1/sn(si));
                        Rc = 2*(Wm*Ls*keq*z^(sn(si)+1)/(sn(si)+1));
                        dem = (W*sind(th)+Rc)/2*Rp;
                        if dem <= Twb, th_b = th; else break; end
                    end
                    for th = thscan
                        p = W*cosd(th)/A; z = (p/keq)^(1/sn(si));
                        Rc = 2*(Wm*Ls*keq*z^(sn(si)+1)/(sn(si)+1));
                        dem = (W*sind(th)+Rc)/2*Rp;
                        if dem <= Twc, th_c = th; else break; end
                    end
                    th_p = 50;
                    for vv = Vs
                        thv = 50;
                        for th = thscan
                            p = W*cosd(th)/A; z = (p/keq)^(1/sn(si));
                            Rc = 2*(Wm*Ls*keq*z^(sn(si)+1)/(sn(si)+1));
                            if (W*sind(th)+Rc)*vv/eta_d <= 2*Mo.rated_power_W, thv = th; else break; end
                        end
                        th_p = min(th_p, thv);
                    end
                    [th_o, bi] = min([th_t, th_b, th_p]);
                    binds = {'traction','burst-torque','power'};
                    if th_o > best.th + 1e-9, best = struct('th',th_o,'G',G,'bind',binds{bi}); end
                    if mi==1 && ki==1 && msi==1 && si==2
                        % keep cont-grade at chosen G for report below
                    end
                end
                % cont (sustained) grade at best G
                Twc = Tc_cont*best.G*eta_g; th_c = 0;
                for th = thscan
                    p = W*cosd(th)/A; z = (p/keq)^(1/sn(si));
                    Rc = 2*(Wm*Ls*keq*z^(sn(si)+1)/(sn(si)+1));
                    if (W*sind(th)+Rc)/2*Rp <= Twc, th_c = th; else break; end
                end
                vtop = (Mo.max_speed_rpm/best.G)*(2*pi/60)*Rp;
                fprintf('%s x %s M=%3.0f %-10s: G=%4.1f thMax=%4.1f (%s) thCont=%4.1f vtop=%3.1fm/s\n',...
                    mnames{mi}, tnames{ki}, M, soils{si}, best.G, min(best.th,50), best.bind, th_c, vtop);
            end
        end
    end
end
fprintf(['note: burst = short climbs only; sustained climbing capped at thCont.\n' ...
    'tip-over above ~45deg needs 750 outer-width check (tilt_check).\n' ...
    'soil = mineral reference; plantation mulch/mud needs calibration.\n']);

% --- 15deg sustained requirement (usual 0-10deg): min G holding 15deg on
% cont torque + cont power @1.0m/s, sandy loam; report vtop + burst reserve
fprintf('\n--- 15deg sustained check (sandy loam) ---\n');
si = 2; keq0 = kc(si);
for mi = 1:2
    Mo = Mots{mi};
    Tc_cont = Mo.rated_power_W/(Mo.rated_speed_rpm*2*pi/60);
    for ki = 1:2
        Tr = Trks{ki}; P = Tr.pitch_mm/1000;
        Wm = Tr.W_mm/1000; Ld = P*Tr.n_links; Ls = (Ld-2*pi*R)/2; A = 2*Ls*Wm;
        PD = P/sin(pi/10); Rp = PD/2; keq = keq0/Wm + kphi(si);
        for msi = 1:2
            M = Ms(msi); W = M*g; th = 15;
            p = W*cosd(th)/A; z = (p/keq)^(1/sn(si));
            Rc = 2*(Wm*Ls*keq*z^(sn(si)+1)/(sn(si)+1));
            dem = (W*sind(th)+Rc)/2*Rp;
            Gneed = dem/(Tc_cont*eta_g);
            Gall = Gs(Gs >= Gneed - 1e-9); G = Gall(1);
            vtop = (Mo.max_speed_rpm/G)*(2*pi/60)*Rp;
            Pdem = (W*sind(th)+Rc)*1.0/eta_d;
            Twb = Mo.stall_torque_Nm*G*eta_g;
            burst_deg = 0;
            for thb = thscan
                pb = W*cosd(thb)/A; zb = (pb/keq)^(1/sn(si));
                Rcb = 2*(Wm*Ls*keq*zb^(sn(si)+1)/(sn(si)+1));
                if (W*sind(thb)+Rcb)/2*Rp <= Twb, burst_deg = thb; else break; end
            end
            if Pdem <= 2*Mo.rated_power_W, pflag = 'OK'; else pflag = 'OVER'; end
            if vtop >= 1.5, vflag = 'OK'; else vflag = 'SLOW'; end
            fprintf('%s x %s M=%3.0f: Gmin=%4.1f vtop=%3.1f P@1m/s=%4.0fW %s burst-to=%4.1f %s\n',...
                mnames{mi}, tnames{ki}, M, G, vtop, Pdem, pflag, burst_deg, vflag);
        end
    end
end
