# AGENTS.md

This is **not a software project**. It is a sim-first mechanical design repo for a
500 mm tracked flail mower plus its rubber-track undercarriage. MATLAB does the
engineering sizing; Python does the CAD. There is no build system, test runner,
package manifest, or git repo.

## Layout — independent design threads, don't cross-wire them

- `common/` + `flail/rev2/` — the 500 mm flail mower (rotor, drive, box-5 housing). **Current build.**
- `flail/rev1/` — superseded volute housing, reference only.
- `undercarriage/v1|v2|v3/` — rubber-track chassis. `v2` is the frozen build (6/8/40);
  `v2/trim_2yr/` is a **rejected** 2-yr-life weight-trim snapshot; `v3` is spine sizing in progress.
- `track_180x60x37/` — second track variant; `common/` holds the first track (180×72×37).
- `prototype_v0/` — independent 775-motor nylon-line walk-behind cart (own sims + `specs/` + `cad/`).
  Rear 2 wheels driven for tank turn; cutter is 775 + trimmer line only.
- `prototype_1/` — frozen archive snapshot of `common/` + `flail/`. **Never edit it.**

The many duplicated-looking rev/snapshot folders are intentional history, not cruft to clean up.

## Running the MATLAB sims

- **Base MATLAB only** (no toolboxes) — this is a real constraint, several sims say so explicitly.
- MATLAB R2026b is wired up as an MCP server in `opencode.json`; prefer the MCP
  MATLAB tools over a shell. Its working folder is this repo root.
- Sims are standalone scripts (`clear; clc; close all;` at top). Run with
  `run('<path>.m')` from anywhere: they self-locate via `fileparts(mfilename('fullpath'))`
  and `addpath` their own `specs/`. Header comments saying "run from matlab folder" are
  legacy and ignored by the code.
- `specs/*.m` (`common/specs/`, `track_180x60x37/specs/`) are **one function per component**
  returning a struct whose fields carry unit suffixes (`_m`, `_mm`, `_N`, …). Call them as
  functions. These are frozen numbers proven by executed sims — don't silently change values;
  update the sim + `COMPONENTS.md` together.
- Sims report results as printed `PASS`/`FAIL` gates and a `fails` counter. There is no test
  framework: "passing" means the script runs clean and the gates print PASS.
- Run order is authoritative in `common/FILEMAP.md` ("Run order") and `common/GUIDE.md` §4.

## Units and datums

- CAD/drawings: **mm**. Sim internals: **SI** (m, kg, N, W). Spec field names encode the unit.
- Datums are documented per thread (e.g. undercarriage: ground lug-tip = 0, X = travel,
  Y = across, Z = up; track centres y = ±260). Read the file header before assuming a datum.

## CAD

- Parametric CAD scripts use **build123d** (+ `ezdxf` for DXF). Run with the system Python 3.11.
- FreeCAD assemblies (`.FCStd`) are rebuilt by executing a script *inside* FreeCAD, e.g.
  `exec(open('C:/Users/malliath/Desktop/matlab/undercarriage/v2/cad/freecad_build.py').read())`.
  That file is the single source of truth for v2 placements. FreeCAD MCP tools are also available.
- Some sims consume CAD output (e.g. `flail/rev2/sim_enclosure_design_v2.m` reads
  `flail/rev2/cad/enclosure_cad.json`; undercarriage `*.json`). **Regenerate CAD first**, then
  re-run the sim, or the closed-loop numbers go stale.
- `.stl` / `.dxf` / `.step` are build artifacts: regenerate from the `.py` scripts, don't hand-edit.

## Toolchain — installed & available

### MATLAB (R2026b, license 40705494) — full catalog installed

All toolboxes below are **licensed and installed** (verified via MCP `detect_matlab_toolboxes`).
Note: sims are deliberately **base-MATLAB only**; toolboxes are available when a sim genuinely
needs one (e.g. Optimization Toolbox for trade studies, Curve Fitting for bench data).

**Core & Simulation:** MATLAB, Simulink, Simscape, Simscape Battery, Simscape Driveline,
Simscape Electrical, Simscape Fluids, Simscape Multibody, SimEvents, Stateflow.

**Math & Optimization:** Optimization Toolbox, Global Optimization Toolbox, Symbolic Math Toolbox,
Curve Fitting Toolbox, Statistics and Machine Learning Toolbox, Econometrics Toolbox,
Partial Differential Equation Toolbox, System Identification Toolbox.

**Control & Signal:** Control System Toolbox, Robust Control Toolbox, Model Predictive Control
Toolbox, Signal Processing Toolbox, Signal Integrity Toolbox, DSP System Toolbox, DSP HDL Toolbox,
Audio Toolbox, Wavelet Toolbox, Antenna Toolbox, Phased Array System Toolbox, RF Toolbox,
RF Blockset, RF PCB Toolbox.

**Code & Model:** MATLAB Coder, Simulink Coder, MATLAB Compiler, MATLAB Compiler SDK, Embedded Coder,
GPU Coder, HDL Coder, HDL Verifier, Fixed-Point Designer, Simulink Check, Simulink Code Inspector,
Simulink Coverage, Simulink Design Optimization, Simulink Design Verifier, Simulink Test,
Simulink Report Generator, Simulink Variant Manager, Simulink Fault Analyzer, Requirements Toolbox,
System Composer, Simulink Control Design, Simulink PLC Coder, Simulink Desktop Real-Time,
Simulink Real-Time, Simulink Compiler, Simulink FMU Builder, Simulink 3D Animation, Simulink Copilot.

**Automotive & Aerospace:** Automated Driving Toolbox, Vehicle Dynamics Blockset, Powertrain Blockset,
Aerospace Blockset, Aerospace Toolbox, Navigation Toolbox, UAV Toolbox, Satellite Communications
Toolbox, Radar Toolbox.

**Hardware & IoT:** C2000 Microcontroller Blockset, STM32 Microcontroller Blockset, Raspberry Pi Blockset,
Motor Control Blockset, AUTOSAR Blockset, DDS Blockset, SoC Blockset, Mixed-Signal Blockset,
Industrial Communication Toolbox, Vehicle Network Toolbox, Instrument Control Toolbox, Data Acquisition
Toolbox, Database Toolbox, Datafeed Toolbox, Spreadsheet Link, Parallel Computing Toolbox, ROS Toolbox.

**Wireless:** 5G Toolbox, LTE Toolbox, WLAN Toolbox, Bluetooth Toolbox, Wireless Network Toolbox,
Wireless HDL Toolbox, Wireless Testbench, Communications Toolbox.

**Imaging & Vision:** Image Processing Toolbox, Computer Vision Toolbox, Image Acquisition Toolbox,
Medical Imaging Toolbox, Point Cloud Toolbox, Vision HDL Toolbox, Visual Inspection Toolbox.

**Other:** Bioinformatics Toolbox, Deep Learning Toolbox, Deep Learning HDL Toolbox,
Reinforcement Learning Toolbox, Predictive Maintenance Toolbox, Risk Management Toolbox,
Fuzzy Logic Toolbox, Mapping Toolbox, Text Analytics Toolbox, SimBiology, Financial Toolbox,
Financial Instruments Toolbox, MATLAB Report Generator, MATLAB Test, MATLAB Copilot, SerDes Toolbox.

### Python (3.11.9) — build123d CAD

- **build123d 0.13.0** — parametric CAD (the single source of truth for geometry).
- **ezdxf** — DXF export.
- Supporting: cadquery-ocp-novtk, ocp_gordon, numpy, scipy, sympy, svgpathtools, etc.

### FreeCAD — MCP server (addon v0.1.26, protocol v1)

MCP tools available (via `tools.freecad.*`):
- `get_rpc_status` — health check (running / GUI dispatch state).
- `list_documents` — list open FreeCAD documents.
- `create_document` — create a new document.
- `execute_code_async` — run Python inside FreeCAD without waiting (90 s default timeout,
  up to 1800 s). Used to run `freecad_build.py` / `freecad_mass_check.py`.
- `get_parts_list` — list parts in the parts-library addon.

Note: `detect_matlab_toolboxes` reports **installed** toolboxes. The full catalog above
(RF, Radar, Satellite, etc.) indicates a full/enterprise license where everything is both
licensed and installed.

## Sources of truth (keep docs in sync)

- `common/PROJECT_INPUTS.md` — user-supplied inputs only, not recommendations.
- `common/COMPONENTS.md` — frozen per-part values (source: executed sims).
- `common/MVP_ROTOR.md` — authoritative rotor dimensions.
- `common/GUIDE.md` — decisions + run order + shop package.
- `common/TRACK_MODEL_RULES.md` — track rules; **E = 22 mm is frozen by the user**.
- `ACETRAX - Construction Tracks (5).pdf` p.2 (Mini-Excavator table) is the dimensional
  authority for tracks. `E` (lug height) is **not** in the PDF — it's carried over/frozen at 22 mm.
- When a sim changes a frozen value, update the matching `.md`; docs and specs are expected
  to agree.
