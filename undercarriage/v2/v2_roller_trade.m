% V2_ROLLER_TRADE  roller construction x material trade. Least work + least cost wins.
% SUPERSEDED 2026-10-29 by the v3 simple spool: pipe + backplate + welded 65/52
% seat + loose 42.4x109 spacer; no Loctite, no ring stacks. See build_v3_simple.py.
% The trade below is kept as history; its 50NB/6205 centre tube clashes with
% the 28.5mm track horns, which is why the v3 uses the shaft as the spacer.
% Frozen: paired discs/ station, D114.3 x w40, radial 1700N/disc, shaft D25, 1x6205/disc.
% Candidates: (A) fab spool MS-ERW pipe + 2 laser cheeks + Loctite hub [current]
% (B) fab spool with thinner pipe wall (3.6)  (C) COTS conveyor roller D114
% (D) solid MS bar slice. Contact = steel on rubber belt (E~50MPa).
clear; clc;
F=1700; R=0.1143/2; Wd=0.040;
% --- 1) belt contact (Hertz line, rubber compliance dominates) ---
Er=50e6; nu=0.49; Estar=Er/(1-nu^2);
b=sqrt(2*F/(pi*Wd*Estar)); pmax=F/(2*b*Wd)/1e6;
fprintf('contact half-width %.0fmm pmax %.1fMPa -> steel grade IRRELEVANT for contact (rubber gives). No alloy benefit. PASS-MS\n',b*1000,pmax);
% --- 2) pipe ring crush: unsupported thin ring moment M~0.182*F*R ---
for t=[0.0045 0.0036]
  M=0.182*F*R; S=Wd*t^2/6; sig=M/S/1e6;
  s='PASS'; if sig>225, s='FAIL-needs-cheeks'; end
  fprintf('pipe wall %.1fmm bare-ring %.0fMPa %s\n',t*1000,sig,s);
end
fprintf('-> cheeks are STRUCTURAL (ring stiffeners), not optional. Keep 2/drum.\n');
% --- 3) with cheeks (supported edges, factor ~0.3 on moment) ---
M=0.182*F*R*0.3; S=Wd*0.0045^2/6;
fprintf('pipe 4.5 + cheeks: %.0fMPa vs YST210(210)/E250(250) PASS\n',M/S/1e6);
% --- 4) COTS conveyor roller check ---
fprintf('COTS conveyor D114: std lengths 200mm+, solid pressed caps; needs slicing to w40 + re-cap = MORE ops than fab, and full-width use fouls centre horns. REJECT.\n');
% --- 5) solid bar check ---
msolid=pi*(0.1143/2)^2*0.04*7850; mhollow=12*1.88/12;
fprintf('solid slice %.1fkg vs hollow %.1fkg each; solid needs 52mm bore for 6205 = LATHE (banned). REJECT.\n',msolid,mhollow);
% --- 6) cost/work model (EDIT rates with shop quotes; defaults = estimates) ---
rate_pipe=70; rate_laser_part=25; rate_weld=15; rate_hub=40;  % Rs/kg, Rs/part, Rs/fillet, Rs/hub
n=12;
costA=n*(1.88*rate_pipe+2*rate_laser_part+2*rate_weld+rate_hub);
opsA=n*(1+2+1);  % cut + 2 welds + Loctite
fprintf('Option A (MS-ERW 4.5 + cheeks): Rs~%.0f/machine, %d ops. VERDICT: KEEP\n',costA,opsA);
fprintf('MATERIAL: MS ERW YST210 (or IS2062 E250 if same price) — weldable, dent-ok with cheeks, paint + grease for corrosion. No EN8/SS benefit.\n');
% --- 7) user proposal: pipe-section hub (50NB OD60.3) + weld, vs ring stack ---
% Bearing seat needs ID52.0 (+0.05/-0). 50NB ERW IDs: light 53.9 / med 53.1 / hvy 51.3.
% IS1239 wall tol makes ID lottery ~+-0.6. Loctite 638 fills 0.25 max, 660 fills 0.50.
gap_med=53.1-52; gap_hvy=52-51.3;   % diametral
fprintf('50NB-med ID gap %.1f (638 max 0.25) | 50NB-hvy INTERFERENCE %.1f (needs bore/hone=LATHE)\n',gap_med,gap_hvy);
fprintf('-> pipe-ID lottery: no stock class gives a 52 seat; cherry-picking 12 seats with calipers at the yard is not a process. WELD side is fine (adapter OD60.3 + cheek ID60.5 laser = clean slip+weld), but the SEAT still needs exact bore.\n');
fprintf('VERDICT: keep 5-ring laser stack for the seat (bore exact, no lottery); stock-match principle already applied on drum OD114.3. If laser access is the pain, nest rings free inside any laser order (tiny parts).\n');
% --- 8) user proposal E: joined spool (wheel-pipe-wheel), bearings in centre pipe, single bolt through ---
% Per station now: 2 drums(1.88 each incl hub+brg) + shaft 1.0 + 2 collars + grubs + washer + pin.
m_now=2*1.88+1.0+2*0.07+0.05+0.05;
% Spool: 2 bare drums (pipe+2 cheeks: 0.49+0.65=1.14) + centre 50NBx160 (0.80)
% + 2 turned bushes 0.50 + 2 brg 0.26 + bolt+2 nuts 0.90.
m_spool=2*1.14+0.80+0.50+0.26+0.90;
parts_now=2*(1+2+5+1)+1+2+2+1+1; parts_spool=2*3+1+2+2+1+2;
fprintf('SPOOL vs NOW per station: mass %.2f vs %.2fkg | parts %d vs %d (saves %d/station, %d/machine)\n',...
  m_spool,m_now,parts_spool,parts_now,parts_now-parts_spool,(parts_now-parts_spool)*6);
% Horn gate: centre pipe OD60.3 bottom z=91-30.15=60.85; horn tip=34+horn_h.
for horn_h=[15 20 24]
  fprintf('horn_h %dmm -> pipe clearance %.1fmm %s\n',horn_h,60.85-(34+horn_h),iif(60.85-(34+horn_h)>=3,'OK','CLASH-MEASURE SAMPLE'));
end
fprintf('SPOOL VERDICT: ADOPT w/ 2 gates — (1) caliper horn height off track sample (>=3mm clear), (2) lathe quote for 12 bushes + 12 turn-downs vs saved 60 rings + 16 collars + cure waits. Weld centre pipe at assembly AFTER fit-check (tack, verify gauge, finish); bearings press in AFTER welding via open outer cheeks + bolted washer retainers (serviceable, heat never touches seals).\n');
% --- 9) user proposal F (FINAL): ONE-UNIT roller. Per wheel: pipe100NBx40 + ONE outer
% cheek (OD114/ID65) + TURNED adapter (bar turned OD65/ID52x25, welded into cheek).
% Inner reducer ring OD80/ID60 + centre 50NB tube, 2x6205 pressed in turned seats,
% 1 through-bolt plate-to-plate. Lathe: 12 adapters (one setup each) + facing.
m_F=2*0.49+2*0.325+2*0.234+2*0.099+0.45+0.26+0.90;
parts_F=2+2+2+2+1+2+1+2;
fprintf('ONE-UNIT vs NOW per station: mass %.2f vs %.2fkg | parts %d vs %d (saves %d/station, %d/machine) | welds 6 | lathe: 12 turned adapters + facing\n',...
  m_F,m_now,parts_F,parts_now,parts_now-parts_F,(parts_now-parts_F)*6);
fprintf('seat: 6205 pressed full-width in TURNED steel ID52, adapter welded to cheek (no Loctite in load path); horn gate same (50NB centre, measure sample).\n');
fprintf('ONE-UNIT VERDICT: FINAL — take it pending horn caliper. V2 CAD rebuild = 6 stations only when you say go.\n');
function s=iif(c,a,b), if c, s=a; else, s=b; end, end
