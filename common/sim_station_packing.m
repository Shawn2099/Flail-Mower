%% sim_station_packing.m
% How many stations/blades PHYSICALLY fit in the 500 mm drum?
% Each station needs: tab ear(s) + blades + washers + swing clearance +
% pin retention. Max stations = what fits in 500 mm minus end margins.
% Compares the packing LIMIT against the recommended count per config.
% Base MATLAB only. Run from the matlab folder.
clear; clc; close all;

drumL = 500; endMargin = 15; usable = drumL - 2*endMargin;  % mm

% station designs: [ear thicknesses] + blades + hardware (all mm)
% footprint = sum(ears) + sum(blades) + 2mm per gap + 6mm clip side
S(1) = struct('tag','single C2 ','ears',[8],   'bl',[8],      'swing',5);
S(2) = struct('tag','pair C1   ','ears',[6 6], 'bl',[8 8],    'swing',5);
S(3) = struct('tag','triple C4 ','ears',[8 8], 'bl',[8 8 8],  'swing',6);
S(4) = struct('tag','hammer C3 ','ears',[10],  'bl',[40],     'swing',5);
REC = [10 10 12 8];   % recommended blade totals (C1=5st C2=10st C4=4st C3=4st)
BPS = [1 2 3 2];      % blades per station

fprintf('\n=== STATION PACKING (usable %d mm of 500) ===\n', usable);
fprintf('station    footprint pitch maxSt maxBlades recommended fits?\n');
MAXB = zeros(1,4);
for i = 1:4
    gaps = numel(S(i).ears) + numel(S(i).bl);       % gaps between parts
    fp = sum(S(i).ears) + sum(S(i).bl) + gaps*2 + 6;
    pitch = fp + S(i).swing;
    maxSt = floor(usable/pitch) + 1;                 % first at margin, last at L-margin
    MAXB(i) = maxSt*BPS(i);
    recSt = REC(i)/BPS(i);
    if recSt<=maxSt, v='YES'; else, v='NO - REDESIGN'; end
    fprintf('%s %4.0fmm    %3.0fmm %3.0f   %3.0f      %3.0f blades  %s\n', ...
        S(i).tag, fp, pitch, maxSt, MAXB(i), REC(i), v);
end

fprintf('\nAnswer: 10 is NOT the packing limit, it is the coverage optimum.\n');
fprintf('Max singles ~%d, max pairs ~%d blades. Recommended counts use %.0f%% of room.\n', ...
    MAXB(1), MAXB(2), REC(2)/MAXB(1)*100);
fprintf('Extra blades past coverage need only add windage + wear + cost.\n');

figure('Name','Packing');
bar([MAXB' REC']);
grid on; set(gca,'XTickLabel',{'C2 single','C1 pair','C4 triple','C3 hammer'});
ylabel('blades'); title('Packing limit vs recommended'); legend('max fits','recommended');
