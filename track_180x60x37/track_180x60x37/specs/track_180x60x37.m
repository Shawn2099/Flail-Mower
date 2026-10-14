function s = track_180x60x37()
% TRACK_180x60x37  ACETRAX mini-excavator rubber track, 180 x 60 x 37.
% Source: ACETRAX - Construction Tracks (5).pdf, Mini-Excavator table row:
%   Width=180, Pitch=60, IGB(B)=24, OGB(A)=62, C=25, D=24.5 (all mm).
% Naming: 180 = width mm, 60 = pitch mm (core-to-core), 37 = link count.
% Loop pitch length Ld = 60*37 = 2220 mm (steel-cord pitch line).
%
% Cross-section key (see pdf diagram, top-left p.2):
%   W = overall width, A = outer span across guide horns at base,
%   B = inner gap between horns, C = horn height above inner roller path,
%   D = horn height above outer roller path, E = outer lug height (NOT in pdf).
%
% All pdf dims are EXACT. E / belt thickness / horn length are CARRIED OVER
% from the verified 180x72x37 build (E=22 FROZEN by user Oct 2026).

s.name       = 'ACETRAX mini-excavator 180x60x37';
s.W_mm       = 180;    % pdf
s.pitch_mm   = 60;     % pdf
s.n_links    = 37;     % from size code 180x60x37 (count of cores/pitches)
s.IGB_B_mm   = 24;     % pdf col IGB (B) = inner gap
s.OGB_A_mm   = 62;     % pdf col OGB (A) = outer span across horns
s.C_mm       = 25;     % pdf
s.D_mm       = 24.5;   % pdf

s.Ld_mm      = s.pitch_mm * s.n_links;   % 2220 pitch-line loop length

% --- derived horn plan (symmetric about centre) ---
s.horn_gap_inner_mm = s.IGB_B_mm;              % 24
s.horn_span_outer_mm = s.OGB_A_mm;             % 62
s.horn_width_each_mm = (s.OGB_A_mm - s.IGB_B_mm)/2;  % 19.0

% --- CARRIED OVER from 180x72x37 (not in catalogue; parametric) ---
s.belt_thk_mm   = 12;   % carcass rubber+cord below roller path [CARRIED OVER]
s.lug_h_mm      = 22;   % outer tread lug height = E in diagram [FROZEN by user Oct 2026, same as 1st track]
s.horn_len_mm   = 32;   % horn length along track per pitch [CARRIED OVER]
s.horn_top_w_mm = 16;   % horn top width after draft (each) [CARRIED OVER]
s.steel_core_mm = [58 20 6]; % [width thk embed] core bar per pitch, centred on
                             % cord line (fully embedded in belt) [CARRIED OVER]
s.mass_kg_each  = 17.1;  % calculated from CAD volumes (rubber 1200/steel 7850);
                         % builder mass_kg; weigh sample on receipt to confirm
s.status = 'PDF dims frozen; E/belt/horn-length carried over from 180x72x37 - confirm on sample';
end
