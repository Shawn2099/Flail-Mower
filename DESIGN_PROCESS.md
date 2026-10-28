# DESIGN_PROCESS.md — the five-stage workflow

Every design task in this repo follows the same five stages. No skipping. The AI
(and any human) must complete each stage before moving to the next.

```
Inspect → Specify → Build → Validate → Deliver
```

---

## Stage 1 — Inspect

**Goal:** Understand what exists and what's needed before touching anything.

- Read the relevant `BRIEF.md`, `specs/`, and CAD output (`*.json`, `*.step`).
- Read `MATERIALS.md` for stock sizes and constraints.
- Read `AGENTS.md` for thread boundaries and frozen values.
- If the task references a prior decision, find it in `GUIDE.md` or the sim that set it.

**Output:** A one-paragraph summary of what exists, what's missing, and what the
task actually asks for. If the task is ambiguous, stop and ask.

**Pass condition:** You can state the task in one sentence without referencing
the original prompt.

---

## Stage 2 — Specify

**Goal:** Convert the task into a measurable spec before building anything.

- **Function:** What must it do? (force, speed, travel, cut height, tip speed...)
- **Constraints:** What must it clear? (ground pressure, Indian stock, mass budget...)
- **Interface:** What does it connect to? (shaft dia, bolt pattern, wheel OD...)
- **Environment:** What does it see? (grass load, rain, dust, operator abuse...)

**Output:** A spec block like:

```
SPEC: <part name>
  function     : <what it does>
  constraints  : <must clear X, must not exceed Y>
  interface    : <connects to Z>
  environment  : <sees A, B, C>
```

**Pass condition:** Every constraint is a number or a stock size, not a vibe.

---

## Stage 3 — Build

**Goal:** Create the geometry or sim that satisfies the spec.

- **Sim first (MATLAB):** Sizing, stability, traction, torque — prove the numbers
  before drawing.
- **CAD second (build123d):** Model at the sim's dimensions. Use the parametric
  scripts (`cad/build_*.py`), not hand-editing.
- **Step-by-step (build123d-mcp):** For new mechanisms, build one feature at a time
  and check the result before adding the next.

**Output:** A sim that prints PASS/FAIL gates, and/or a `cad/build_*.py` script
that runs clean.

**Pass condition:** The sim's gates print PASS, and the CAD script runs without
error and produces the expected `*.step` / `*.json`.

---

## Stage 4 — Validate

**Goal:** Independently verify the design before calling it done.

- **FreeCAD verify:** Re-import the STEP, check mass/CG, run the interference
  check (`freecad_build.py`), confirm clearances.
- **Regression tests:** Run `tests/test_v0_specs.m` (or the relevant test) to
  confirm frozen numbers haven't drifted.
- **Cross-check:** Does the CAD mass match the sim mass? Does the CG match?
  Does the tank-turn torque match? If not, find the drift.

**Output:** A validation report:

```
VALIDATION: <part name>
  mass       : <CAD> vs <sim> → <delta> → PASS/FAIL
  CG         : <CAD> vs <sim> → <delta> → PASS/FAIL
  interference: <N> unintended → PASS/FAIL
  clearances : <list each gate> → PASS/FAIL
  regression : <N/N> tests pass → PASS/FAIL
```

**Pass condition:** Every check prints PASS. If any FAIL, return to Stage 3.

---

## Stage 5 — Deliver

**Goal:** Package the result so it can be built, tested, and tracked.

- **TechDraw drawing:** 2D shop drawing with dimensions (via FreeCAD MCP).
- **BOM update:** Add new parts to the buy list (`MATERIALS.md`).
- **Git commit:** Commit the sim, CAD script, and any docs together. Message
  follows: `<part>: <what changed> — <key numbers>`.
- **Open items:** Update `BRIEF.md` — close the item, note any new ones.

**Output:** A commit on `master`, a drawing, and an updated BRIEF.md.

**Pass condition:** `git log` shows the commit, the BRIEF.md item is closed,
and the drawing exists.

---

## How the AI uses this

When given a design task, the AI must:

1. State which stage it's in.
2. Name the pass condition before starting.
3. Stop if a pass condition fails — don't carry a failure forward.
4. Show the output of each stage before moving on.

No stage is optional. No "I'll just build it and see." The stages are the
difference between a part drawer and a design engineer.

---

## Application to the v0 open items

| # | Item | Stage 1 (Inspect) | Stage 2 (Specify) | Stage 3-5 |
|---|---|---|---|---|
| 5 | Cut-height adjust | BRIEF.md #5, deck 3.9 mm spare | 25-60 mm range, motor must not move up | Spacer sleeve or slotted bracket |
| 9 | Guard lip | BRIEF.md #9, guard band OD 244 | 15-20 mm downward lip, same strip | Add to `build_v0_frame.py` |
| 6 | Handle + controls | BRIEF.md #6, handle to 900 mm | Tank turn, two throttles, grip height | New CAD + layout |
| 10 | Rear axle retention | BRIEF.md #10, stub 57 mm | Shoulder at X=178.5 or spacer | D-flat clocking, weld check |

Each open item is a five-stage task. Pick one and we'll run it start to finish.
