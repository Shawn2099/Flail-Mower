function s = track_180x72x37()
% TRACK_180x72x37  ACETRAX mini-excavator rubber track, 180 x 72 x 37.
% Source: ACETRAX - Construction Tracks (5).pdf, p.2 row:
%   Width=180, Pitch=72, IGB(B)=23, OGB(A)=66, C=28.5, D=28.5 (all mm).
% Naming: 180 = width mm, 72 = pitch mm (core-to-core), 37 = link count.
% Loop pitch length Ld = 72*37 = 2664 mm (steel-cord pitch line).
%
% Cross-section key (see pdf diagram, top-left p.2):
%   W = overall width, A = outer span across guide horns at base,
%   B = inner gap between horns, C = horn height above inner roller path,
%   D = horn height above outer roller path, E = outer lug height (NOT in pdf).
%
% All pdf dims are EXACT. E / belt thickness / horn length are ASSUMED
% (documented below) because the catalogue does not give them.

s.name       = 'ACETRAX mini-excavator 180x72x37';
s.W_mm       = 180;    % pdf
s.pitch_mm   = 72;     % pdf
s.n_links    = 37;     % from size code 180x72x37 (count of cores/pitches)
s.IGB_B_mm   = 23;     % pdf col IGB (B) = inner gap
s.OGB_A_mm   = 66;     % pdf col OGB (A) = outer span across horns
s.C_mm       = 28.5;   % pdf
s.D_mm       = 28.5;   % pdf

s.Ld_mm      = s.pitch_mm * s.n_links;   % 2664 pitch-line loop length

% --- derived horn plan (symmetric about centre) ---
s.horn_gap_inner_mm = s.IGB_B_mm;              % 23
s.horn_span_outer_mm = s.OGB_A_mm;             % 66
s.horn_width_each_mm = (s.OGB_A_mm - s.IGB_B_mm)/2;  % 21.5

% --- ASSUMED (not in catalogue; parametric, easy to re-cut) ---
s.belt_thk_mm   = 12;   % carcass rubber+cord below roller path [ASSUMED]
s.lug_h_mm      = 22;   % outer tread lug height = E in diagram [FROZEN by user Oct 2026]
s.horn_len_mm   = 32;   % horn length along track per pitch [ASSUMED]
s.horn_top_w_mm = 16;   % horn top width after draft (each) [ASSUMED]
s.steel_core_mm = [58 20 6]; % [width thk embed] core bar per pitch, centred on
                            % cord line (fully embedded in belt) [ASSUMED]
s.mass_kg_each  = 18.5;  % calculated from CAD volumes (rubber 1200/steel 7850);
                         % builder mass_kg; weigh sample on receipt to confirm
s.status = 'PDF dims frozen; E/belt/horn-length assumed - confirm on sample';
end
