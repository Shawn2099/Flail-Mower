# rev2 — box-5 housing (CURRENT BUILD)
- `sim_enclosure_design_v2.m` — housing sim + fab sheet + §12 CAD closed-loop check.
- `sim_structural_audit.m` — resonance + member checks.
- `cad/build_enclosure_box5.py` → `enclosure_box5.step/.stl` + `enclosure_cad.json`.
- `cad/tilt_check.py` (CG + track table), `cad/weigh.py` (masses), `cad/export_dxf.py` → `cad/dxf/` (plasma files).
- `enclosure_profile_v2.*` — sim plots. Shared inputs: `../../common/specs/`.