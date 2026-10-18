function m = motor_hub_6p5in_350W()
% MOTOR_HUB_6P5IN_350W  Robokits RKI-9011 6.5in 36V 350W BLDC hub motor + tyre.
% Datasheet dims/ratings verified from the product page (Oct 2026). Values marked
% [EST] are inferred and MUST be bench-confirmed (Kv, phase R) or datasheet-confirmed.
% It is a DIRECT-DRIVE wheel motor: the rotor IS the wheel, there is no gearbox,
% so there is no reduction stage to slow it down - throttle does the slowing.

% --- Datasheet ---
m.name          = 'Robokits RKI-9011 6.5in 36V 350W hub motor';
m.V_nom         = 36;        % V nominal
m.P_rated       = 350;       % W rated, per motor
m.mass_kg       = 2.30;      % kg each
m.pole_pairs    = 25;        % 25 pole pairs (50 magnets)
m.max_speed_kmh = 26;        % page "Max speed" (kit figure - cap hard for mowing)
m.shaft_type    = 'D-type';
m.shaft_len_mm  = 57;
m.shaft_d_mm    = 16;        % round side
m.shaft_flat_mm = 13.5;      % flat side
m.hub_OD_mm     = 134;       % motor body OD
m.tyre_OD_mm    = 170;       % OD WITH airless tyre  <-- rolling diameter
m.tyre          = 'airless (solid rubber)';
m.tyre_w_mm     = 45;        % [EST] tyre SECTION width - sets the wheel width
                             % (used for CAD clearances to the deck/rails)
m.contact_w_mm  = 40;        % [EST] ground CONTACT patch width (<= section) -
                             % use this one for ground pressure. MEASURE both.
m.sensors       = 'hall + temperature';
m.ip            = 'IP4';

% --- Derived geometry ---
m.wheel_R_m = m.tyre_OD_mm/2/1000;      % 0.085 m
m.circ_m    = pi*m.tyre_OD_mm/1000;     % 0.534 m

% --- [EST] electrical / mechanical (bench-confirm) ---
% Kv from max speed: 26 km/h on 170 mm wheel = 7.22 m/s -> 811 rpm @ 36 V
m.Kv_rpm_per_V = 811/36;                  % ~22.5 rpm/V        [EST]
m.Kt_Nm_per_A  = 9.5493/m.Kv_rpm_per_V;   % ~0.424 Nm/A        [EST]
m.R_phase_ohm  = 0.35;                    % [EST]
m.I_cont_A     = m.P_rated/m.V_nom;       % ~9.7 A
m.I_peak_A     = 20;                      % controller current limit [EST]
m.eff          = 0.85;
m.T_cont_Nm    = m.Kt_Nm_per_A*m.I_cont_A*m.eff;  % ~3.5 Nm [EST]
m.T_peak_Nm    = m.Kt_Nm_per_A*m.I_peak_A*m.eff;  % ~7.2 Nm [EST]

m.status = '[EST] Kv/Kt/R inferred from max-speed figure - confirm on bench';
end
