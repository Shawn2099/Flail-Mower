%% step_enclosure.m — fit OUR rotor (500 drum, discs +/-258, roof 218, depth 450)
%% into the modeled end boxes. Assumes 3 mm sheet walls (state if different).
clear; clc;
load('step_solids.mat','RES','PTS');
WALL = 3;
fprintf('=== CANDIDATE BOXES (outer, mm: X0 X1 Y0 Y1 Z0 Z1) ===\n');
for id = [577 578 596 597 579]
    b = box6(RES(RES(:,1)==id,:));
    fprintf('#%d  X %.0f..%.0f  Y %.0f..%.0f  Z %.0f..%.0f\n', id, b(1),b(2),b(3),b(4),b(5),b(6));
end
fprintf('\n=== FIT vs OUR NEEDS (inner = outer - 2x%d) ===\n', WALL);
fprintf('need: width>=516 (rotor+discs) | depth>=450 | height>=436\n');
for id = [578 579 597]
    b = box6(RES(RES(:,1)==id,:));
    iw = (b(2)-b(1))-2*WALL; idp = (b(4)-b(3))-2*WALL; ih = (b(6)-b(5))-2*WALL;
    if iw>=516, w='OK'; else, w='FAIL'; end
    if idp>=450, d='OK'; else, d='FAIL'; end
    if ih>=436, h='OK'; else, h='marginal/low'; end
    fprintf('#%d inner %.0f x %.0f x %.0f -> width %s | depth %s | height %s\n', ...
        id, iw, idp, ih, w, d, h);
end
b = box6(RES(RES(:,1)==587,:));
fprintf('\n#587 side unit X %.0f..%.0f size %.0fx%.0fx%.0f (bearing/drive candidate)\n', ...
    b(1),b(2),b(2)-b(1),b(4)-b(3),b(6)-b(5));
fprintf('\nBearing span note: if cheeks sit on end-box outer walls, span grows past our\n');
fprintf('600 spec -> sag x2.8 (~0.02 mm, trivial), critical ~5300 vs 6000 gate.\n');
fprintf('Operating 2500 keeps 2.1x margin; or weld inner sub-cheeks at +/-300.\n');

function b = box6(r)
b = [r(2) r(5) r(3) r(6) r(4) r(7)];   % x0 x1 y0 y1 z0 z1
end
