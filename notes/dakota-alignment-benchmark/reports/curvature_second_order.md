# Curvature and second-order structure

## Recovered second-order material

Two second-order objects are genuinely present in the recovered record:

1. For the candidate sweep basis `gamma(theta)=gamma0+B sin(theta)+K(1-cos(theta))`,
   - `gamma' = B cos(theta) + K sin(theta)`;
   - `gamma'' = -B sin(theta) + K cos(theta)`.
2. For a unit-speed planar attainable curve with signed normal offset `r` and signed curvature `kappa`, the nearest-point calculation gives
   - `E'' = 1-r kappa`;
   - `delta s = (T dot delta z)/(1-r kappa)` away from the singular denominator.

The latter was independently rechecked as mathematics. No truck-specific `r` or `kappa` was recovered.

## What residuals cannot yet establish

Departures from the simple sweep fit could be caused by geometric curvature, but the same residual pattern can also come from:

- wrong/uncertain steering angles;
- suspension settling or tire scrub;
- camber-gauge zero/drift;
- row transcription mistakes;
- compliance or hysteresis;
- an inadequate sine/even model.

Therefore unexplained residuals are not labeled curvature.

## First-order epsilon versus physical second order

An epsilon algebra may deliberately truncate perturbation products. That is an algebraic representation decision. The physical model can still have nonzero `gamma''`, Hessians, or other curvature. The benchmark keeps `epsilon.py` and `curvature.py` separate for that reason.
