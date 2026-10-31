# WEIGHT & EFFICIENCY — can the undercarriage buy a smaller motor?

Status: **option study, not frozen.** As-drawn v2 is 185.7 kg; target 165 kg.
All-up machine is **281.7 kg** (undercarriage 185.7 + deck 96, including the
mower motor and pack). Sim: `v2_weight_motor.m` (base MATLAB).

## 1. What the motor is actually sized by

The traction motor is sized by **wheel torque**, which is set by mass × grade,
not by efficiency. At 0.88 m/s, per side:

| Machine mass | 15° continuous | 20° burst |
|---:|---:|---:|
| 281.7 kg (as-built all-up) | 332 W | 438 W |
| 261.7 kg (after −20 kg) | 308 W | 407 W |
| 400 kg (design envelope) | 471 W | 622 W |

The sim's "250 kg continuous" case is **lighter than the as-built 281.7 kg
machine** (281.7 − pack 8 − mower motor 15 − traction motors 18 ≈ 241 kg). So the
real continuous case is ~282 kg, not 250 kg. It still sits inside the 600 W motor,
but the margin is 81%, not 100%.

The **400 kg case is 118 kg above the machine** — that is a payload/ballast
envelope, not the machine. If it is not a real load, the motor can be smaller.

## 2. Weight cuts that do not reopen the 6-8-40 freeze

| Cut | kg | Note |
|---|---:|---|
| Motors 2 × 9.0 → 2 × 5.4 kg | −7.2 | Proven by `MOTOR_SWAP.md`; also cuts cost |
| Side-plate pockets, 6 mm bosses kept | −6.0 | Laser pocket ~15%; keep 6 mm at UCFL/flange seats |
| Guards 2.0 → 1.5 mm | −3.0 | Already in BRIEF §2 |
| Flanges 8 → 6 mm | −1.0 | Friction-grip joint; margin survey util is low |
| Deck mounts solid → fabricated | −2.3 | 80 × 80 × 20 solid block → 6 mm plate + gusset |
| Bolts 28 → 20 M12 | −0.5 | Bolt util 0.005; 20 still gives 0.007 |
| **Total** | **−20.0** | **185.7 → 165.7 kg** |

Gross cut 20.0 kg. Two motor adapter plates (~0.7 kg each) make the net **18.6 kg
→ 167.1 kg**. The phase-2 30 mm axle closes the last 2 kg. This hits the target
without thinning the 6 mm side plates or changing the 40 mm axle. The plate
pockets are a CAD/laser change; the rest are trivial.

Phase 2, if a bigger cut is needed: **40 → 30 mm axle + UCFL206** saves ~5.8 kg.
Check: 30 mm at 250 Nm bending = 94 MPa (allow 150); parking torsion 155 Nm =
29 MPa. But it changes the side plates, bearing seats, collars, sprocket bore and
CAD, so it is not a quick win.

## 3. Does the weight cut buy a smaller motor?

At the as-built 281.7 kg, 0.88 m/s:

| Motor | 15° continuous margin | 20° burst margin (2× peak) |
|---:|---:|---:|
| 350 W | +6% | +60% |
| 450 W | +36% | +105% |
| 600 W | +81% | +174% |
| 850 W | +156% | +288% |

At 261.7 kg after the gross −20 kg cut (net ~263 kg with adapters):

| Motor | 15° continuous margin | 20° burst margin (2× peak) |
|---:|---:|---:|
| 350 W | +14% | +72% |
| 450 W | +46% | +121% |
| 600 W | +95% | +195% |
| 850 W | +176% | +318% |

So:

- **450 W is enough for the actual 282 kg machine** at 15°/0.88, with 36% margin.
  At the 400 kg/15° continuous case it is only 0-3% margin with an 8T pinion
  (and 8% short with a 9T), so it only works if 400 kg is a short-time overload.
- **600 W is the smallest that keeps the 400 kg/15° continuous case with margin**
  (14-28% depending on pinion). The 450 W is only 0-3% there. The 400/20 burst is
  not the limit for either: the 450 W has ~56% burst margin. The price difference
  to 450 W is only ~₹1,000, so there is no cost reason to drop below 600 W.
- **850 W is 37% over the 400/20 burst** (96.6 Nm at the wheel vs 70.7 needed).
  The competitor's 850 W is a standard 1 hp-class gearmotor, not a requirement.
  If that 850 W is **total** (one motor plus steering clutches), it is only
  425 W/side — below our 600 W; check whether the competitor is 2×850 W or
  1×850 W before using it as a benchmark.

Do not compare nameplate watts directly. An 850 W motor at 450 rpm makes
18 Nm; a 600 W at 480 rpm makes 12 Nm. The watt label differs because of the
speed/torque split; after gearing, the **wheel torque** is what decides. A 600 W
motor at 80% load is also more efficient than an 850 W motor at 56% load.

Concretely: an 850 W motor left at the existing 3.43 ratio gives ~59 Nm at the
wheel but runs at 1.45 m/s. The 600 W motor with the 8T pinion (6:1) gives ~68 Nm
at 0.88 m/s. The ratio, not the watt label, is doing the work.

The weight cut gives the 450 W more margin, but it does not change the 600 W
choice while the 400 kg envelope stands. It does improve runtime by ~7% and
reduces the load on every structural member.

## 4. Efficiency

| Lever | Effect | Comment |
|---|---|---|
| Mass, −20 kg | ~7% less traction energy on a 15° slope | 1.18 W per kg per side at 0.88 m/s |
| Speed 0.88 → 0.70 m/s | −20% traction power | Still in the mow band |
| Grade 15° → 10° | −33% traction power | sin ratio |
| Brushed 78% vs BLDC 85% | ~+9% battery draw | Cost swap, not an efficiency swap |
| Chain 95% | Already counted | Belt would be 97-98%, but wider |
| Track tension/bearing drag | Already optimised | 16 × 6205, single bearing/disc |

The important one: **the brushed swap loses ~9% efficiency, while the −20 kg cut
gains ~7%. They roughly cancel.** If efficiency is the priority, keep the BLDC
motor and use a cheaper BLDC controller instead (see `COST_DOWN.md` lever A
alternative); if cost is the priority, the brushed swap is the bigger win.

The motor size is not set by efficiency. Gearing does not change the power
required for a given wheel torque and speed: `P = T_wheel × ω_wheel`. A smaller
motor only comes from less mass, less grade, or less speed.

## 5. Recommendation

1. **Do the −20 kg cut.** It hits 165.7 kg gross (167.1 kg net), improves runtime
   ~7%, and is cost-neutral. Do not thin the 6 mm plates; pocket them.
2. **Keep the 600 W motor** while the 400 kg envelope stands. It is already
   smaller than the competitor's 850 W.
3. **If the real maximum is 300 kg**, the 450 W motor (8T, 0.83 m/s) becomes
   viable; the saving is small (~₹1k), so the battery current is the real reason
   to consider it.
4. **If 0.70 m/s is acceptable**, the 450 W gains another 20% margin and the
   battery runtime rises; this is a better lever than another 20 kg of steel.

## 6. Open questions

- Is the 400 kg / 20° case real, or a conservative envelope?
- Is 0.88 m/s the required mow speed, or is 0.70 m/s acceptable?
- Can the side plates be laser-pocketed without reopening the 6 mm seat issue?
