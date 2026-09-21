# State and observation vectors

## Physical-state ontology

The evidence supports the need for a state larger than caster, but it does not support a single fully numeric state vector yet. A physically meaningful ontology includes, when measured or modeled:

- driver/passenger camber and caster;
- road-wheel steering angles / toe state;
- four lower-control-arm eccentric positions and clock phases;
- control-arm/pivot geometry;
- ride-height/suspension displacement;
- calibration parameters for level/inclinometer and steering angle;
- latent settling/hysteresis state;
- nuisance geometry such as wheelbase/track when a steering model uses them.

Unknown components remain unknown. They are not inserted merely to make a matrix large.

## Recoverable candidate measurement-model state

The existing sweep code provides a concrete model that can be enlarged honestly by adding observed nuisance sources. The implemented 26-component state is:

`[driver gamma0, driver B, driver K, passenger gamma0, passenger B, passenger K, steering ratio, wheelbase, track, level bias, driver gauge bias, passenger gauge bias, 7 driver steering offsets, 7 passenger steering offsets]`.

The observation vector has 14 components: seven driver camber observations followed by seven passenger camber observations.

This is a **measurement-model state**, not a recovered suspension configuration. `B` is called a caster-related odd coefficient because the recovered script itself says equating it to physical caster is approximate.

## Why steering offsets are explicit

The experiment currently lacks a verified table of actual road-wheel angles. Giving each row a steering-angle nuisance variable makes that missing information visible rather than burying it in a nominal ratio. This makes the inverse problem intentionally underdetermined, which is the correct diagnostic until the angle metrology is recovered.

Direct yaw is not a procedural prerequisite. When it cannot be measured, the
steering angles remain latent outputs of a declared command map
`G(command, side, path, state)`. The manual-derived 17.4:1 conversion is the
nominal member of that map family; its per-wheel and nonlinear discrepancy is a
named model/input uncertainty. Half/full/lock odd-signal consistency and the
two sides constrain or reject candidate `G` maps without pretending to observe
yaw. The result is model-conditional or set-valued caster, not an unsupported
point identification.

## Future observations that would narrow physical and measurement state

Repeated inclinometer readings, actual eccentric witness-mark
coordinates/angles, controlled ride height, and post-intervention before/after
pairs can narrow the present model. A one-time or external road-wheel-yaw
calibration would also narrow the steering-map family if it ever becomes
available, but the procedure does not require the user to make that
measurement. Until enough of these constraints exist, the finite geometric map
and its Jacobian remain a conditional family rather than one calibrated truck
map.
