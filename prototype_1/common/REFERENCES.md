# Design References — Flail Mower (books, standards, real products)

## Books / principles
1. **Persson, S. (1987), *Mechanics of Cutting Plant Material* (ASABE)** — foundation of
   specific-energy cutting models. Impact cutting of grass sits in the low kJ/m² range.
2. **ASABE D497 (Ag Machinery Management Data)** — industry framework for rotary/draft power.
   Rotary power reported at PTO; add motion resistance separately (we follow this split:
   cutting + windage + traction allowance).
3. **Rotz & Muttira (1992), rotary power requirements model** — predicts average rotary power
   for harvest machines; basis of D497 Table 2 coefficients.
4. **Lab flail studies (e.g., RRIJM 2019 review)** — measured blade velocities 33–52 m/s;
   specific energy rises with depth of cut and feed rate. Our 36–41 m/s band sits inside it.
5. **Safety: ISO 12100 + ISO 4254 + ISO 5395 + ISO 17101-2 (flail thrown-object test)** — risk assessment, ag-machinery and mower safety;
   basis of our housing, flap, exclusion-zone and dead-man requirements.
6. **Fan/volute: Eck (1973) *Fans*, Carolus *Ventilatoren*, Gjeta et al (2019, 5.5% gap rule), Patil (tongue 6–12.5%)**
   — volute area law + clearance practice behind the (superseded) volute design.
7. **Flail shredding: Savoie (ASABE 2011)** — hammer-hood spacing + counter-knife set energy vs shred quality.

## Real products (benchmark anchors)
| Machine | Width | Power | kW/m | Rotor/tip | Blades | Duty |
|---|---|---|---|---|---|---|
| **Orec Cyclone track flail** | 650 mm | 8.4 hp (6.3 kW) Honda | 9.7 | ~3000 rpm drum | 38 Y-flails (58/m) | brush + saplings, 0.27–0.94 m/s |
| **Great Plains flail (spec sheet)** | — | — | — | Ø165 mm @1858 rpm = **43 m/s** | — | tractor flail |
| **Tractor flail rule of thumb** | per foot | 5 PTO hp/ft | ~12 | — | — | heavy/brush rating |
| **Spider ILD02 (rotary ref)** | 1230 mm | 24 hp | 14.5 | 4 spindles | 4 mulching | slopes to 41° |
| **Striker 7 (Kovai Classic)** | 550 mm | 9 hp gas | — | 5-axis flail, 48 blades | 48 small | stubble, 20–150 HT, 45° claim, ~150 kg |
| **Farmrobo R5** | 610 mm front | electric | — | front mower | — | orchard weeds, 5 km/h |
| **JD 25A flail** | — | 30–75 hp tractor | — | Ø114 @1850 = **42.5 m/s** | cupped pairs | finish cut, roller 140 |
| **OUR MVP** | 500 mm | 3 kW (0.56 shaft) | 6.0 inst / 1.1 used | Ø60 +108 @2200 = **36.4 m/s** | 10 (20/m) | light grass 1 m/s |

Reading: our *installed* 6 kW/m sits below brush-rated machines (9–12) and far above our
*used* 1.1 kW/m in light grass — exactly where an MVP with brush ambitions should be.
Our tip speed is below the 43 m/s tractor-flail anchor (we trade speed for mass, same energy).
Our blade density is lower because 58 mm hemispheres cover more per blade than Y-flails.
