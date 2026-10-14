function s = controller_Mecwin_PMSM_300A()
% Mecwin PMSM hub-motor controller (Screenshot_20261009_225210_Chrome.jpg)
s.name              = 'Mecwin PMSM Controller 300A';
s.rated_voltage_V   = [48 60 72];
s.max_dc_current_A  = 300;
s.control           = 'Hall_or_Encoder';
s.has_GUI           = true;
s.price_INR         = 16386;
s.note              = 'Set rotor RPM cap in GUI (2800-3100 rpm). Non-returnable.';
s.source_file       = 'Screenshot_20261009_225210_Chrome.jpg';
end
