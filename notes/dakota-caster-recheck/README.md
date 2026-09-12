# Dakota caster sweep: geometry-aware robust recheck

Conversation date: 2026-09-11. **Status: retained numerical experiment. Actual vehicle caster remains UNKNOWN under ASE's measurement-validity gate.** These are model coefficients under stated assumptions, not accepted alignment values, confidence intervals, or cam-adjustment instructions.

## Files and scope

- [Calculation](dakota_caster_recheck.py): the conversation's Python script, unchanged.
- [Complete results](dakota_caster_recheck_results.json): all 22 fits, observations used in each scenario, predicted camber, residuals, derivative-based uncertainties, Huber factors, inclusion masks, and iteration counts. Only JSON whitespace was compacted; no keys or values were changed.
- [Reproduction receipt](verification.json): source/result identities, runtime versions, and the host-side rerun result.

This snapshot is kept in both [Econometrician](https://github.com/bl4ckb4ll/econometrician/tree/main/notes/dakota-caster-recheck) and [ASE's existing A4 branch](https://github.com/the-twin-pines/ASE/tree/a4-suspension-steering/notes/dakota-caster-recheck). It follows [Econometrician #2](https://github.com/bl4ckb4ll/econometrician/issues/2) and [ASE #4](https://github.com/the-twin-pines/ASE/issues/4). It does not add a method to the Econometrician dispatcher, alter its IID-mean bootstrap, or relax ASE's alignment gates. NumPy and SciPy are optional dependencies of this standalone experiment only.

## What is being compared

Let alpha be steering-wheel rotation, theta the individual road-wheel yaw, and gamma the camber reading. Angular inputs to sine, cosine, and their derivatives are radians; camber and the fitted coefficients are reported in degrees. Right steering is positive.

The candidate curve is:

$$f(\theta)=\gamma_0+B\sin\theta+K(1-\cos\theta).$$

The sign-adjusted caster-related coefficient is `-B` on the driver side and `+B` on the passenger side. Neither B nor K is asserted to be an exact physical caster or steering-axis-inclination parameter. The odd/even split is a candidate model, not a validated suspension derivation.

The experiment compares equal road-wheel angles with an ideal Ackermann map. The latter assumes wheelbase 131.3 inches, front track 62.8 inches, ratio 17.4:1 interpreted as an equivalent centre-wheel angle, and symmetric stops at 1.59 steering-wheel turns. These are working inputs, not new measurements or a calibration of the Dakota rack/linkage.

The uncertainty propagation retains the full chain:

$$\sigma_i^2=\sigma_\gamma^2+\left[(B\cos\theta_i+K\sin\theta_i)g'(\alpha_i)\sigma_\alpha\right]^2,\qquad\theta=g(\alpha).$$

The main comparison assumes independent errors with standard deviations 0.25 degrees camber and 15 degrees steering-wheel rotation. The scale sweep tries 5, 15, 30, and 45 degrees for the latter. These scales are assumptions, not measured tolerances.

Each inner fit uses Huber loss on standardized residuals, with transition 1.345; effective variances are recomputed between fits. This is robust regression, not a median or IQR rule. For residual r, its local reweighting factor is `min(1, 1.345 / abs(r/sigma))`, in addition to the inverse-variance factor. It is an iterated effective-variance approximation, not a full errors-in-variables likelihood or a bootstrap.

## Reproduced comparison

Values below are caster-related coefficients in degrees. Extra decimals identify computations, not measurement precision.

| Steering model | Transcription scenario | Driver | Passenger |
|---|---|---:|---:|
| Equal angles | Earlier +1.25 / +4 readings | 8.50 | 5.47 |
| Equal angles | Proposed +0.25 / +0.25 readings | 8.50 | 5.56 |
| Ideal Ackermann | Earlier +1.25 / +4 readings | 8.06 | 4.91 |
| Ideal Ackermann | Proposed +0.25 / +0.25 readings | 8.06 | 5.05 |

The disputed entries are driver half-left and passenger full-left. The proposed quarter-degree readings are separate scenarios, not silently corrected raw observations. Reported ranges are represented by explicitly chosen midpoints; the program does not have a complete log of every repeat or its approach direction.

The driver's alternative -1 degree half-left reading gives 7.63 with ideal Ackermann and the photo-derived -5 degree maximum-right value included. That maximum-right value remains unconfirmed. Omitting it gives 9.32, 9.75, or 7.86 depending on whether the half-left input is +0.25, +1.25, or -1 degree. These existing omission runs matter: robustness to two disputed response values is not robustness to every input, endpoint, or calibration choice.

All primary comparisons use seven positions. Explicit omission scenarios set `included_rows` false for the omitted position. The output still lists its residual and nominal weight for inspection; it was not used in the fit. Apply the inclusion mask when interpreting `total_weights`.

## Reproduce

Use Python 3.10 or later with NumPy and SciPy. From this directory:

```sh
python3 dakota_caster_recheck.py > rerun.json
python3 - <<'PY'
import json
from pathlib import Path
saved = json.loads(Path('dakota_caster_recheck_results.json').read_text())
rerun = json.loads(Path('rerun.json').read_text())
assert saved == rerun, 'Results differ; inspect environment and numerical differences'
print('PASS: complete parsed JSON matches')
PY
```

The recorded rerun used Python 3.13.5, NumPy 2.3.5, and SciPy 1.17.0. Before compacting the saved JSON, its entire byte stream matched a fresh run. The script's finite-difference steering-derivative checks and noise-free synthetic coefficient-recovery checks also passed. Other numerical-library versions may require a documented numerical-tolerance comparison rather than byte-for-byte equality; do not silently relax a failed check.

## What remains open

A reproducible fit establishes the calculation, not actual road-wheel angles, gauge/reference validity, physical caster, or the signs and sizes of eccentric adjustments. Robust residual loss does not resolve shared steering calibration error, floor/reference error, or hysteresis. No new physical measurements or device-runtime acceptance were produced by uploading this snapshot.

Revisit the actual per-wheel steering map; covariance and repeat/approach-direction records; errors-in-variables fitting; physical justification and identifiability of the odd/even model; and uncertainty coverage under an explicit sampling process. The general ideas to retain are derivative/Jacobian propagation, robust fitting without silently discarding discrepancies, and separating response outliers from systematic geometry error. The larger cam-response Jacobian is a different experiment and is not identified by this steering sweep.
