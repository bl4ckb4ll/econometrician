# Measurement generations

The generations are deliberately not pooled. A generation boundary means the measurement method, physical state, or both changed enough that common error assumptions are unsafe.

| Generation | Approx. period | Evidence quality | What survives | Dominant uncertainty |
|---|---|---|---|---|
| G0 | before/around Sep 7 | low-to-medium | ride-height component measurements; spirit-level/ground photographs | ground irregularity, reference height definition, repeatability not recovered, possible suspension state |
| G1 | Sep 7 | medium for existence/order, mixed for exact numerals | handwritten seven-position driver/passenger sweep and later script transcription | handwriting/transcription, nominal rather than measured road-wheel angle, gauge zero, settling/path |
| G2 | Sep 10 | relatively strong for timestamped passenger sequence | direct passenger sequence max-right 0° through max-left +6°; several direct driver statements; handwritten table | still no recovered actual road-wheel angles; gauge/systematic errors; steering/state path; row conflict with saved script |
| G3 | Sep 11 | strong as spot observations, not comparable as same state | straight: driver −2°, passenger +2.5°; full-left: driver −6°, passenger +1° | different state/generation; cause of change unknown |
| G4 | Sep 12 after additional passenger-front outward move/settling | improved transcription for driver | corrected driver seven-position sweep; provisional passenger transcription | passenger canonical correction missing; actual angle table missing; settling/hysteresis/common calibration |
| I0–I2 | interventions interleaved with sweeps | qualitative-to-medium | which cams were deliberately touched; passenger-front outward then farther outward then reverse inward; witness marks | exact eccentric phase/rotation, driver-rear baseline contradiction, suspension settling |

## Independence structure

Repeated readings only reduce a component that is genuinely repeatable and independent. The following are plausible shared/common-mode sources and must not be reduced by `1/sqrt(n)` merely because seven readings or seven estimates exist:

- level or inclinometer zero used across a sweep;
- steering-angle calibration or steering-ratio model used across multiple rows;
- ground/body attitude for a setup;
- one suspension settling/hysteresis state shared by nearby readings;
- one transcription convention or row-order error;
- one eccentric-cam witness-mark interpretation.

Row-to-row scatter, if measured from genuinely repeated reads at unchanged state, can support a stochastic component. None of the recovered seven-position tables by itself proves seven independent realizations.

## Chronology and path dependence

The record contains direct evidence of state change: after the passenger-front cam was moved farther outward, the passenger-front corner was observed to settle downward by roughly 0.5–1 cm, possibly during subsequent steering. That magnitude is a rough observation, not a photogrammetric result. It is enough to reject a purely memoryless interpretation of every sweep.

A future sequential model should therefore allow a latent state `h_t` for settling/hysteresis and use a transition such as

`x_(t+1) = F(x_t, intervention_t, steering_path_t, h_t)`

rather than treating all measurements as samples of one static `y=f(x)`.
