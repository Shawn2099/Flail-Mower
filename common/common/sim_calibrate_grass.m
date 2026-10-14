%% sim_calibrate_grass.m
% CALIBRATION FRAMEWORK: turns two field tests into your grass's true numbers.
%  Test A (no-load): spin rotor free at 3 RPMs, record battery current each.
%  Test B (mowing) : mow a measured strip at steady speed, record current.
% The script then computes YOUR windage curve + YOUR specific energy Es,
% and tells you which lines to paste back into the spec files.
% Base MATLAB only. === REPLACE THE EXAMPLE VALUES BELOW WITH MEASURED DATA ===
clear; clc;

%% ---- MEASURED INPUTS (edit these after the field tests) ----
% EXAMPLE values (laptop estimates, NOT measurements):
rpmA   = [2000 2200 2500];  % Test A rotor speeds
ampsA  = [6.0  7.3  9.0];    % Test A battery amps @72V (EXAMPLE)
ampsB  = 9.6;                % Test B steady mowing amps @72V (EXAMPLE)
voltB  = 72;                 % pack voltage during Test B
stripL = 100; stripT = 100;  % Test B: 100 m in 100 s -> v = 1.0 m/s
width  = 0.500;              % working width m

%% ---- Windage fit: P = k * rpm^3 ----
PelecA = ampsA * voltB;
k = mean(PelecA ./ rpmA.^3);            % electrical-windage coefficient
fprintf('Windage fit: Pelec = %.3e x rpm^3 (from Test A)\n', k);
fprintf('  -> predicted no-load @2200: %.0f W. Compare with sim assumption 196 W elec.\n', k*2200^3);

%% ---- Specific energy from Test B ----
v = stripL/stripT;
Ptot = ampsB * voltB;
Pwind = k*rpmA(2)^3;                     % windage at mowing rpm (use Test A rpm nearest)
Pcut = Ptot - Pwind;
Es = Pcut/(width*v);
fprintf('\nTest B: v=%.2f m/s, total %.0f W - windage %.0f W = cut %.0f W\n', v, Ptot, Pwind, Pcut);
fprintf('YOUR Es = %.0f J/m2 (sim assumed 800). Paste into specs/grass_light_maintained.m\n', Es);
fprintf('YOUR windage k = %.3e (replaces 400 W @3000 assumption via k*3000^3 = %.0f W)\n', k, k*3000^3);
