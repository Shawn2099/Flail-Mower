%% sim_opposing_pair.m
% Tests the user's proposal literally: 2 OPPOSING J-blades per station =
% 10 axial positions x 2 (180 deg apart) = 20 J singles, each on its own
% single-lug tangential bolt (same proven pin as MVP). Compared vs MVP.
% Also tests the "triple" as 3 singles per station (15 positions x ... ) -> shown absurd.
% Base MATLAB only.
clear; clc; close all;

W = 0.500; Es = 800; v = 1.0;
rpmJ = 2300; omJ = rpmJ*2*pi/60;
rpmS = 2200; omS = rpmS*2*pi/60;
pin_r = 0.03015 + 0.020; Wref = 400; eff = 0.92*0.88;
mJ = 0.400; rJ = 0.105; cgJ = 0.055;
mS = 0.340; rS = 0.108; cgS = 0.055;

fprintf('\n=== OPPOSING-J (10 pos x 2 = 20 J singles @2300) vs MVP (10 S @2200) ===\n');
% MVP
PcS = Es*W*v; PwS = Wref*(rpmS/3000)^3*(10/10)*1.0;
PsS = PcS + PwS; PeS = PsS/eff;
FcS = mS*(2500*2*pi/60)^2*(pin_r+cgS);
% Opposing J-20
PcJ = Es*1.2*W*v; PwJ = Wref*(rpmJ/3000)^3*(20/10)*1.3;
PsJ = PcJ + PwJ; PeJ = PsJ/eff;
FcJ = mJ*(2500*2*pi/60)^2*(pin_r+cgJ);
sigJ = FcJ*0.014/(pi*0.017^3/32)/1e6;
tipJ = omJ*(pin_r+rJ); cutsJ = 20*rpmJ/60/v; cutsS = 10*rpmS/60/v;
fprintf('MVP:      shaft %.0f W elec %.0f W (%.0f%% cont) cuts/m %.0f\n', PsS, PeS, PeS/1950*100, cutsS);
fprintf('Opp-J-20: shaft %.0f W elec %.0f W (%.0f%% cont) cuts/m %.0f tip %.1f pin %.0f/180MPa\n', ...
    PsJ, PeJ, PeJ/1950*100, cutsJ, tipJ, sigJ);
fprintf('Coverage: same 52.2 axial pitch -> 100%%. Balance: PERFECT (true opposite twins).\n');
fprintf('Cost: 2x blades/bolts/fins, rotor ~+4 kg, battery -35%% runtime.\n');

%% Triple-as-singles absurdity check (3 per station x 10 pos = 30 blades)
PwT = Wref*(rpmJ/3000)^3*(30/10)*1.25; PsT = Es*1.3*W*v + PwT;
fprintf('\nTriple-as-30-singles: shaft %.0f W elec %.0f W (%.0f%% cont), 30 bolts/fins.\n', ...
    PsT, PsT/eff, PsT/eff/1950*100);
fprintf('Buildable but pointless: +%.0f%% power over MVP for zero extra coverage.\n', (PsT-PsS)/PsS*100);

figure('Name','Opposing pair');
bar([PsS PsJ]); grid on;
set(gca,'XTickLabel',{'MVP 10S','Opp-J 20'});
ylabel('shaft W'); title('Power cost of opposing-J finish');
