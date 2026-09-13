# Recomputed calculations and sensitivity audit

## Nominal steering conversion

The recovered reference uses a nominal overall ratio `17.4:1`. Under the equal-angle model,

`theta = 360 t / 17.4` degrees,

where `t` is steering-wheel turns from center.

For symmetric road-wheel positions `±theta`, the recovered small-camber sweep multiplier is

`m(theta) = 1 / (2 sin(theta))`.

Fresh recomputation gives:

| steering-wheel turns | nominal road-wheel angle | multiplier |
|---:|---:|---:|
| 0.50 | 10.344827586° | 2.784399372 |
| 1.00 | 20.689655172° | 1.415204048 |
| 1.50 | 31.034482759° | 0.969830781 |
| 1.59 | 32.896551724° | 0.920600224 |

The older documents' four-decimal values are consistent with these. The exact values above are generated from the formula; no rounded table is used as a computational oracle.

## Steering-angle sensitivity

For `C = Delta_gamma / (2 sin theta)`, holding the camber difference fixed,

`dC/dtheta = -C cot(theta)`

when `theta` is in radians. Therefore a one-degree road-wheel angle perturbation changes `C` locally by the fraction

`|cot(theta)| pi/180`.

At the nominal half-turn angle `10.3448°`, this is about **9.56% per road-wheel degree**. At one turn it is about 4.62%/degree; at 1.5 turns about 2.90%/degree.

The nonlinearity matters. If the half-turn road-wheel angle were only known to lie within `10.3448° ± 5°`, the multiplier ranges from about `1.890` to `5.367` instead of `2.784`: approximately **−32.1% to +92.8%** relative to nominal. Even `±3°` produces a large asymmetric change.

This is why an early caster estimate based on poorly known small steering angles cannot receive a narrow numerical error bar merely from repeated inclinometer readings. If “several degrees” of road-wheel uncertainty is all that is justified, the result should be a broad interval/feasible set or symbolic epsilon, not a fabricated Gaussian `sigma`.

The full table for `±1°, ±3°, ±5°` is in `data/caster_angle_sensitivity.csv`.

## Camber-reading sensitivity

For the same symmetric formula,

`partial C / partial Delta_gamma = m(theta)`.

Thus a one-degree error in the **difference** of the two camber readings changes the inferred coefficient by 2.784° at the nominal half-turn sweep, 1.415° at one turn, and 0.970° at 1.5 turns.

Whether two endpoint reading errors add, cancel, or correlate depends on source:

- independent read noise contributes to the difference stochastically;
- a truly common additive zero cancels from a difference;
- a zero that drifts between endpoints does not;
- steering/path/settling errors enter through different derivatives and cannot be folded into the same scalar without assumptions.

## Ride-height arithmetic

From the recovered component values:

Passenger pivot average `(265+225)/2 = 245 mm`; spindle minus average `330-245 = 85.0 mm`.

Driver pivot average `(250+295)/2 = 272.5 mm`; spindle minus average `355-272.5 = 82.5 mm`.

The arithmetic is correct. The measurement validity is not established: the individual front/rear pivots differ by 40–45 mm and the truck was photographed on irregular ground. These derived numbers are therefore retained as low-quality constraints, not settled ride height.

## Eccentric one-flat geometry

For eccentric offset `e` and cam clock phase `phi`, the paper model uses

`x = e cos(phi)`

so one 60° flat gives

`Delta x = e[cos(phi+60°)-cos(phi)] = -e sin(phi+30°)`.

A one-flat bolt rotation therefore does **not** imply a fixed linear pivot displacement. Without `phi`, magnitude and sign cannot be inferred solely from “one flat.”

## Old fit reproducibility

The saved `dakota_caster_recheck.py` regenerates its saved JSON byte-for-byte. That establishes implementation reproducibility, not correctness of the disputed row mapping or its illustrative uncertainty assumptions.
