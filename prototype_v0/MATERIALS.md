# MATERIALS.md — prototype_v0: what to buy, and why that thickness

Source of truth for **material + thickness** on the v0 machine.
Generated from `sim_v0_structure.m` (all gates PASS) and checked against
`cad/build_v0_frame.py` by `tests/test_v0_specs.m`.

Everything below is **mild steel (MS)** in sizes a local Indian steel shop
actually sells. Nothing on the drawing is an invented size.

---

## 1. The rule this machine obeys

`sim_v0_frame.m` shows the chassis is nowhere near its stress limit (tube
SF ~17). So thicknesses here are **not** picked by stress. Each part is set by
whichever of these really binds, and the table says which:

| # | Constraint | What it sets |
|---|------------|--------------|
| a | **Indian shop stock** | the actual size list (§2) — no 1.5 mm sheet, no Ø22 tube |
| b | **A joint / MFG need** | the frame must clear the hub axle stack (lifted to Z 104) and the handle wants the bigger section |
| c | **Thread engagement** | M5/M6 bolts → 5 mm plate minimum |
| d | **Impact energy** | the guard band vs a thrown stone — *the only strength-driven thickness* |
| e | **Platform load** | the deck under the battery + an accidental press |
| f | **Operator push/pull** | the handle — and it is *tipping*, not bending, that limits it |

Consequence: on a machine this small, **one tube size and three sheet sizes**
cover the whole build. Buying is simpler than engineering it.

---

## 2. What a local steel shop stocks (confirm at the counter)

| Product | Sizes to ask for | Notes |
|---|---|---|
| MS square tube (SHS) | 20×20, 25×25 in **1.2 / 1.6 (16g) / 2.0** mm wall; 32×32×1.6; 40×40×2 | sold **by the length (6 m)**; ask for *"square pipe 16 gauge"* |
| MS sheet — CRCA / HR | 0.8 / 1.0 / 1.2 / **1.6 (16g)** / 2.0 / **2.5** / 3.0 mm | 8×4 ft sheets, or ask for an offcut |
| GI / GP sheet | same gauges, zinc coated | rust option for the deck; **do not** weld without ventilation |
| MS round bar (gol) | 6 / 8 / 10 / 12 / 16 / **20** / 25 mm | any steel shop |
| MS plate (patra) | 3 / 4 / **5** / 6 / **8** / 10 / 12 mm | sold by weight or an offcut |
| MS flat (patri) | 25×5, 25×6, 40×6, 50×8 | for tabs/brackets if needed |
| MS pipe (IS 1239) | 15 NB (21.3 OD), 20 NB (26.7 OD), 25 NB (33.4 OD) | alternative handle stock |
| Aluminium 6061 / HE30 | angle, flat, tube, 2–3 mm sheet | **2–3× the price, city suppliers only** |
| SS 304 / 202 | sheet 1.0–2.0 mm | 3–4× the price |

> **1.5 mm is not an Indian sheet thickness.** The original CAD had the deck at
> 1.5 mm; that alone forced the move to 1.6 mm.

---

## 3. Member schedule — the actual pick for every part

| Part | Material & size | Governing constraint | Check / SF | Qty |
|---|---|---|---|---|
| Long rails, cross members | **MS SHS 25×25×1.6** | one tube size + the handle (bending a non-issue; the frame is lifted to clear the hub axles) | 9.8 MPa static, **29.5 MPa at a 3 g kerb → SF 5.6** | 2 × 235 mm, 2 × 345 mm |
| Deck posts (4) | **MS round bar Ø16, solid, M6 tapped 10 deep** | thick-on-thin joint + thread (c) | Euler buckling 25.1 MN → SF >1000 | 4 × 16 mm |
| Handle legs + brace | **MS SHS 25×25×1.6** (as above) | operator push, braced | 45 MPa at 250 N → **SF 3.7** | 2 × 790 + 1 × 300 mm |
| Deck lid | **MS/CRCA sheet 1.6 mm** | platform load (e) | 50 N press → **SF 11**, 0.79 mm sag | 355 × 350 |
| Guard band | **MS sheet 2.5 mm** | impact energy (d) | 94 J vs a 46 J stone → **SF 2.0** | 244 OD × 55 tall + 20 mm lip |
| Guard mount tabs | **MS sheet 2.5 mm** (same strip) | cantilever from the band's rim | 18 MPa at 200 N → **SF 9** | 2 × 30 × 34 |
| Corner brackets (4) | **MS plate 6 mm** | wheel load + D-flat bearing | 26 MPa at a 3 g kerb → **SF 6.4** | 4 × 60 × 60 |
| Front stub axles | **MS round bar Ø20** | cantilever from the bracket | 12 MPa at a 3 g kerb → **SF 14** | 2 × 70 mm |
| Rear axle stack | hub motor's own **Ø16 × 57 D-stub** + M16 nyloc + Ø30 washer | bought (the hub motors ship them) | clears the raised frame by 4–5 mm | 2 sets |
| Motor carrier ring | **MS plate 5 mm** | M5 thread engagement (c) | ring OD only needs 85 mm; Ø120 chosen | 1 × Ø120 |
| Carrier arms | **MS plate 5 mm** (from the ring blank) | bolt/bracket rigidity | the 775's 0.6 Nm stall reaction over a 215 mm couple ≈ 3 N per arm | 2 × 60 × 95 |
| Fasteners | **8.8 grade, nyloc** | — | M5×16 (4), M6×20 (4), M8×25 (8), O4 split pin (2), M16 nyloc (2) | — |
| Finish | red-oxide primer + enamel, **or** GI sheet for deck/guard | rust | — | — |

---

## 4. Buy list (walk into the shop with this)

```
1 x  MS square tube 25x25x1.6 (16 gauge)      1 length (6 m)
       uses 3.04 m: 2 rails 235, 2 cross 345, 4 posts 16,
                    2 handle legs 790, 1 brace 300
1 x  MS / CRCA sheet 1.6 mm (16g)             400 x 400 mm offcut  (deck 355 x 350)
1 x  MS sheet 2.5 mm                          800 x 60 mm strip   (guard band + lip + 2 x 30 x 34 tabs)
1 x  MS round bar O20                         0.2 m               (2 x 70 mm front stubs)
1 x  MS round bar O16                         0.1 m               (4 x 16 mm posts, M6 tapped 10 deep)
1 x  MS plate 6 mm                            4 x 60 x 60         (the FOUR corner brackets)
1 x  MS plate 5 mm                            170 x 230           (carrier ring + arms)
4 x M5 x 16, 4 x M6 x 20, 8 x M8 x 25 + 2 x O4 split pins + 2 x M16 nyloc - all 8.8, + nylocs
paint: red oxide primer + enamel  (or GI sheet for the deck and guard)
```

**One 6 m tube covers the frame, the standoffs and the handle.** That is the
main practical win of standardising on 25×25×1.6.

---

## 5. What the sizing changed, and what it cost in mass

| Change | Reason | Mass |
|---|---|---|
| deck 1.5 → **1.6 mm** | 1.5 mm is not an Indian stock thickness | +0.10 kg |
| standoffs 20×20×1.6 SHS → solid Ø16 bar, 16 mm (raised frame) | thick-on-thin joint + thread; posts got shorter with the raised frame | −0.04 kg vs SHS |
| guard 2.0 → **2.5 mm** | thrown-object margin (SF 1.30 → 2.03) | +0.17 kg |
| carrier ring Ø160 → **Ø120** | the OD was never bound by anything | −0.35 kg |
| carrier arms 75 → 95 mm | arms must reach the smaller ring | +0.09 kg |
| front dead axle Ø20×420 → 2 × Ø20×70 stubs | the axle notch is gone (MfD pass) | −0.69 kg net |
| rear dropouts 8 → **6 mm** | 6 mm clears the load | −0.11 kg |
| 4 identical 6×60×60 corner brackets | one part for all four corners | +0.30 kg (front pair) |
| guard mount tabs 2 × 30×2.5×34 | tie the guard to the raised frame | +0.04 kg |
| | **net MfD change** | **−0.42 kg** |

- Fabricated steel: **6.13 → 5.64 kg** (CAD-measured, both sides).
- All-up: **20.9 → 20.5 kg** as modelled, but only −0.42 kg of that is the MfD pass above.
  The rest is the **handle allowance being corrected from 1.5 → 2.2 kg** — 1.58 m of
  25×25×1.6 legs plus a brace is 2.2 kg of tube *before* grips and throttles, so the
  old allowance was simply too light.
- **Design mass stays 21 kg**, so no other sim needed to move.

---

## 6. Why not aluminium or stainless

| Material | Density | E (GPa) | fy (MPa) | Rel. cost | Availability |
|---|---|---|---|---|---|
| MS / CRCA | 7850 | 200 | 250 | 1.00 | every steel shop |
| GI / GP sheet | 7850 | 200 | 250 | 1.15 | every hardware shop |
| Alu 6061-T6 | 2700 | 69 | 240 | 3.00 | city suppliers |
| SS 304 | 8000 | 193 | 215 | 3.50 | city suppliers |

- Aluminium saves ~60 % of the mass but needs **~2.9× the thickness to match
  stiffness** (E is a third). On a stiffness-driven frame the saving mostly
  evaporates — at 3× the cost, and it is not a local-shop material.
- It only really suits the **deck** (mass matters there), and even then GI sheet
  is the better Indian answer: same thickness, no paint, survives a wet
  underside.
- **The guard must stay steel.** Aluminium or plastic is not an option for a
  part whose job is stopping a stone.

---

## 7. Sizing notes that are easy to forget

- **The deck is a gear platform, not a step.** Standing on it (700 N) gives
  ~208 MPa → it will dent permanently. Brace the centre, or go 2.0 mm, if feet
  ever go on it.
- **Guard lip.** Add a 15–20 mm downward lip on the guard band (free — cut it
  from the same strip). A plain band lets debris leave sideways, which is the
  usual failure.
- **The front wheel bore must match the stub.** Bore Ø20 for the Ø20 front stubs; the rear
  pair are the hub motors' 16 mm D-shafts.
- **The handle's real limit is tipping, not bending.** A push *along* the
  (27°-leaned) handle cannot lift the front wheels — 89 % of the force is
  downward. A straight-back push lifts them at only **38 N**, against the ~34 N
  needed to roll up a 5° grade: margin 1.1. So keep the grip low and well back,
  and let the drive pull the machine rather than shoving it by hand.
- **The guard's impact model is deliberately harsh** — it assumes a 20 g stone
  leaves at the *full* 68 m/s tip speed. A stone realistically leaves at
  30–50 % of that (5–12 J), so 2.5 mm sits comfortably inside the bound.

---

## 8. Re-running the checks

```
matlab:  run('prototype_v0/sim_v0_structure.m')      % the sizing + buy list
python:  python prototype_v0/cad/build_v0_frame.py   % CAD at those sizes
mw:      runtests('prototype_v0/tests/test_v0_specs.m')   % 12/12 locks it
```

`tests/test_v0_specs.m` fails if a CAD thickness stops being an Indian stock
size, or if the sim's picks and the CAD's constants drift apart.
