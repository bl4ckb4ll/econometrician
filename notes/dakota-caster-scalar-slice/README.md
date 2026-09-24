# Dakota caster: verified scalar anchor and stagewise reconstruction

This directory starts from one checked scalar result and only expands the
reconstruction where the preserved evidence supports the next row.

## Verified anchor

The anchor remains the timestamped Sep 10 `G2` passenger half-turn pair:

- `E-026`: `+0.5°` camber at `0.5 turn right`.
- `E-028`: `+2.5°` camber at `0.5 turn left`.

The road-wheel angles were not directly measured in the recovered record.
Using the documented nominal conversion

```text
theta = 360 * steering-wheel turns / 17.4
```

gives nominal road-wheel angles `+/-10.3448275862°` and

```text
signed odd coefficient = -5.5687987431°
reported magnitude     =  5.5687987431°
```

`scalar_slice.py` and `test_scalar_slice.py` remain the acceptance gate for
that exact result. The first magnitude Jacobian row is

```text
[-0.2662274832, +0.2662274832, -2.7843993716, +2.7843993716]
```

with columns

```text
[theta_right, theta_left, gamma_right, gamma_left]
```

and all perturbations expressed in degrees.

## Stagewise expansion

`stage_reconstruction.py` extends from that anchor without importing the old
all-data fit as a prior.

### G2 Sep 10 passenger

Three timestamped equal-and-opposite pairs can be formed under the same
nominal steering conversion:

| pair | evidence | nominal magnitude |
|---|---|---:|
| half turn | E-026 / E-028 | 5.5687987431° |
| full turn | E-025 / E-029 | 5.6608161938° |
| lock | E-024 / E-030 | 5.5236013430° |

The range is only about `0.1372°` under the nominal-angle model. A direct
least-squares combination of the three raw symmetric differences gives an odd
sine coefficient of `-5.5647142714°`, magnitude `5.5647142714°`.

This is useful internal consistency. It is not permission to claim a
service-grade physical caster value: actual road-wheel angles were not
measured, the historical passenger direction labels conflict with the
timestamped sequence, and setup/calibration/model terms remain unresolved.

### Driver history

The old driver values near `8°` are explicitly rejected as physical evidence.
They came from a lower-provenance/transcription path with conflicting
half-left and full-lock readings. They are retained only as historical
regression fixtures and are not a prior, target, calibration point, or
ingredient in the reconstructed estimates.

The partial timestamped G2 driver record is insufficient for a trusted
symmetric sweep. G3 contains changed-state spot measurements, not a complete
symmetric pair set.

### G4 Sep 12 driver

The corrected same-session G4 driver table is a separate generation after
documented cam work and passenger-front settling. Under the same nominal angle
conversion its symmetric-pair magnitudes are:

| pair | evidence | nominal magnitude |
|---|---|---:|
| half turn | E-059 / E-057 | 3.4804992144° |
| full turn | E-060 / E-056 | 3.5380101211–3.8918111332° |
| lock | E-061 / E-055 | 2.5316506155° |

Combining the three symmetric differences gives a nominal odd-coefficient
magnitude interval of `2.8772184054–2.9749128589°`, where the interval is from
the recorded `E-056` camber range rather than an invented statistical error
bar.

Do not read the G2 passenger-to-G4 driver difference as a clean causal caster
change. They are different sides, generations, intervention states, steering
paths, and setup states.

The G4 passenger seven-position table remains provisional because its corrected
canonical transcription was not recovered. No passenger G4 caster is promoted.

## Intervention/state sequence

The reconstruction keeps the stages separate:

```text
I0 -> G2 -> G3 -> I1 -> G4 -> I2 -> G5
```

- `I0`: rear-driver cam one-flat experiment, then approximately returned;
  historical rotation viewpoint/witness mark unresolved.
- `G2`: Sep 10 timestamped sweep.
- `G3`: Sep 11 changed-state spot readings.
- `I1`: driver-rear movement is state/baseline-ambiguous; passenger-front was
  moved substantially outward; passenger front then visibly settled about
  0.5–1 cm after the move/steering path.
- `G4`: Sep 12 sweep before the first reverse passenger-front move.
- `I2`: passenger-front pivot moved back inward from near fully outboard.
- `G5`: Sep 16 reset-state sweep after the passenger-front cam was returned;
  only the rear-driver cam was reported displaced.

There is no preserved full sweep immediately after `I2`. A later reset-state
`G5` sweep was recovered from the Sep 16 conversation and is kept as a new
generation rather than retroactively filling that gap.

### G5 Sep 16 reset-state sweep

The user reported that the passenger-front cam had been returned and only the
rear-driver cam remained displaced. Hood/reference endpoints were restored to
`47.5 in / 47.5 in`; a deliberate reference test produced `46 in / 49 in`.
The ordered sweep ran maximum-left to maximum-right.

Under the same nominal equal-angle steering conversion, the symmetric-pair
magnitudes are:

| side | half turn | full turn | lock |
|---|---:|---:|---:|
| driver | 3.4805° | 4.9532–5.3070° | 3.2221° |
| passenger | 1.3922° | 2.1228° | 2.0714–2.3015° |

The change with steering scale is not independent confirmation and is not
sampling scatter. All three pairs share the same commanded-steering conversion,
setup, state, gauge, and sweep path. The full raw rows are in
`g5_reset_sweep.csv`.

The later conversational result `driver 4.6±1.0°`, `passenger 1.9±0.5°`,
`cross-caster +2.7±0.7°` used a two-to-one weight toward the one-turn pair and
described its bars as practical rather than formal. No covariance calculation
or coverage meaning for those bars was recovered. It is retained in the
failure ledger, not promoted as the G5 result.

For present/future cam descriptions, clockwise/counterclockwise means looking
from the rear of the truck toward the front. Historical labels are not
retroactively converted when their viewpoint was not preserved.

## Uncertainty boundary

Each accepted symmetric pair exposes its own checked first-order Jacobian with
respect to

```text
theta_right
theta_left
gamma_right
gamma_left
```

The actual road-wheel angles remain explicit unknown inputs rather than hidden
constants.

No independence assumption is made. In particular:

- a common additive steering-zero shift cancels at first order for a nominal
  equal/opposite pair;
- equal/opposite steering-magnitude error does not cancel;
- a common additive camber-zero shift cancels in the pair difference;
- calibration, gauge placement, setup, settling, and hysteresis are not thereby
  eliminated.

The legacy `0.25°` camber and `15°` steering-wheel sigmas remain excluded
because they were illustrative assumptions, not measured tolerances. No RSS or
single-sigma collapse is produced.

The unresolved symbolic terms remain

```text
epsilon_setup_hysteresis
epsilon_gauge_calibration
epsilon_cam_state_model
```

with `epsilon^2 = 0` for each named first-order object. No mixed-product rule
between distinct epsilons is assumed.

## Run

```sh
python3 scalar_slice.py > scalar_slice_result.json
python3 stage_reconstruction.py > stage_reconstruction_result.json
python3 -m unittest -v test_scalar_slice.py test_stage_reconstruction.py
```

The stage reconstruction is deliberately not a monolithic inverse suspension
fit. It preserves the complete recoverable stage history while refusing to
manufacture missing road-wheel angles, missing cam positions, an independent
Gaussian covariance, or a post-I2 measurement.
