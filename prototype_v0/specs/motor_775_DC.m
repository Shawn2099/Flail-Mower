function mot = motor_775_DC()
% MOTOR_775_DC  Standard "regular" 775 brushed DC motor (RS-775 class).
% Electrical: 12 / 18 / 24 V operating envelopes - conservative continuous + peak
% estimates for a fan-cooled, display-duty motor.
% Mechanical: nominal generic-775 can + shaft. Generic clones vary in shaft dia
% (5 mm vs 6.35 mm) and body length (57 / 66 / 74 mm) - VERIFY on the actual unit.
% Sources: RobotShop RS775SM-4445-F, Handsontec 775-Motor.pdf, generic 775 12-24 V.
% Fields: V (V), n0 (rpm no-load), Tstall (Nm), Tcont (Nm), Pcont/Ppeak (W shaft),
%         eta (-), D_body_mm, L_body_mm, D_shaft_mm, L_shaft_mm, m_kg, mount.
% Sanity: Kt = 9.5493*V/n0 -> stall I ~ 34 / 30 / 31 A; plausible for a 775.

V   = [12   18    24  ];
n0  = [6500 9000  11000];
Tst = [0.60 0.68  0.72];
Tc  = [0.15 0.17  0.18];
Pc  = [80   120   150 ];
Pp  = [150  220   280 ];
eta = [0.62 0.64  0.66];

mot = repmat(struct('name',"", 'V',0, 'n0',0, 'Tstall',0, 'Tcont',0, ...
    'Pcont',0, 'Ppeak',0, 'eta',0, 'D_body_mm',0, 'L_body_mm',0, ...
    'D_shaft_mm',0, 'L_shaft_mm',0, 'm_kg',0, 'mount',""), 1, numel(V));

for k = 1:numel(V)
    mot(k).name   = sprintf('775 @%dV', V(k));
    mot(k).V      = V(k);
    mot(k).n0     = n0(k);
    mot(k).Tstall = Tst(k);
    mot(k).Tcont  = Tc(k);
    mot(k).Pcont  = Pc(k);
    mot(k).Ppeak  = Pp(k);
    mot(k).eta    = eta(k);
    % Mechanical - identical for all voltages (nominal standard 775)
    mot(k).D_body_mm  = 44.5;   % can OD
    mot(k).L_body_mm  = 66;     % can length, shaft excluded
    mot(k).D_shaft_mm = 5.0;    % shaft OD (some clones are 6.35 mm)
    mot(k).L_shaft_mm = 17;     % protruding shaft length, with flat
    mot(k).m_kg       = 0.35;   % typical
    mot(k).mount      = '44.5 mm saddle clamp (generic 775 face-hole pattern varies)';
end
end
