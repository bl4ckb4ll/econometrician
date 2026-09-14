# Dakota caster: first trustworthy scalar slice

This directory implements the first stopping point before any large Dakota
Jacobian is allowed to inherit unverified signs or observations.

## Selected slice

The calculation uses the timestamped Sep 10 `G2` passenger half-turn pair from
the recovered evidence ledger:

- `E-026`: `+0.5°` camber at `0.5 turn right`, 2026-09-10 16:50:13Z.
- `E-028`: `+2.5°` camber at `0.5 turn left`, 2026-09-10 16:59:33Z.

These are at-time user verbal readings. They avoid the known passenger
left/right relabeling in the later seven-position Python transcription.

The road-wheel angles were **not measured directly** in the recovered record.
The default execution therefore uses the documented nominal conversion
`theta = 360 * steering-wheel turns / 17.4`, while exposing both road-wheel
angles as command-line inputs.

The exact eccentric-cam state at these two readings was not recovered. The
record says so rather than inferring it from nearby adjustment notes. The
current CW/CCW convention is "rear looking forward"; it is preserved as a
current convention and is not retroactively assigned to the selected readings.

## Recomputed scalar

For right-positive road-wheel steering,

```
C = (gamma_R - gamma_L) / (sin(theta_R) - sin(theta_L))
```

At the nominal `theta_R = +10.3448275862°`,
`theta_L = -10.3448275862°`, with `gamma_R = +0.5°` and
`gamma_L = +2.5°`,

```
signed odd coefficient C = -5.5687987431°
reported magnitude |C| = 5.5687987431°
```

The historical ASE checkpoint reported the passenger symmetric-pair estimates
as roughly `5–6°`, so this recomputation agrees with that historical range. The
separate all-data robust fit (`5.4–5.5°`) is recorded but is not treated as the
same calculation.

The older printed reference rounded the multiplier to `2.784`; applying that
printed value to the `2.0°` camber difference gives `5.568°`. The exact
formula is `0.0007987431°` higher, a rounding discrepancy rather than a
measurement discrepancy.

## First-order row

For caster **magnitude**, using degrees for all four input perturbations,

```
|C| ≈ 5.5687987431
      - 0.2662274832 delta_theta_right
      + 0.2662274832 delta_theta_left
      - 2.7843993716 delta_gamma_right
      + 2.7843993716 delta_gamma_left
      + epsilon_setup_hysteresis
      + epsilon_gauge_calibration
      + epsilon_cam_state_model
```

and

```
J_|C| =
[ -0.2662274832, +0.2662274832, -2.7843993716, +2.7843993716 ]
```

The first two entries are degrees of caster per degree of road-wheel steering;
the last two are degrees of caster per degree of camber.

The perturbations are **not** declared independent. In particular, a common
additive steering zero shift cancels at first order, whereas an equal increase
in the magnitudes of the two opposite steering angles does not. No RSS or
single `sigma` is produced.

The old `0.25°` camber and `15°` steering-wheel sigmas from
`dakota_caster_recheck.py` are deliberately excluded from propagation because
that script labels them illustrative assumptions, not measured tolerances.

Each unresolved epsilon is retained as a first-order Edriç-style object with
`epsilon^2 = 0`. No mixed-product rule between distinct epsilons is assumed.

## Run

```sh
python3 scalar_slice.py > scalar_slice_result.json
python3 -m unittest -v test_scalar_slice.py
```

Measured road-wheel angles can replace the nominal ones without editing code:

```sh
python3 scalar_slice.py \
  --theta-right-deg RIGHT \
  --theta-left-deg LEFT
```

## Stop rule

This slice checks provenance, arithmetic, sign handling, units, the local
Jacobian, and centered finite-difference derivatives. It makes no claim that
the nominal steering conversion is the true wheel angle and no claim that the
result is a service-grade physical caster measurement.

Do not use this directory as permission to construct or trust the larger
Jacobian. The next row must earn the same provenance and derivative checks.
