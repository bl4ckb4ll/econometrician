# Dakota vehicle-context failure catalog

This note preserves car-specific history that is useful as test context for Econometrician in a Box. It is **not** a software backlog.

The software issues should describe changes to the inference system, type system, model, validation, or tests. The facts below are fixtures, examples, or provenance that may exercise those software requirements.

## Historical alignment states and measurements

- 2025 shop-alignment values were transcribed by the user as approximately:
  - LF caster +3.5 deg
  - RF caster +5.1 deg
  - LF camber +0.2 deg
  - RF camber -0.9 deg
  - LF/RF toe -1.73 deg / -1.08 deg
  - total toe -2.81 deg
- The original printout image has not been recovered in the current audit, so those are preserved as user-transcribed historical evidence, not as an inspected artifact.
- November 2025 direct/plumb caster work used physical length measurements including approximately LF 15.5 in / 1.5 in and RF 16.5 in / 1.0 in. Several assistant-derived caster values came from those experiments; the raw geometry, not the derived assistant number, is what matters as evidence.
- September 2026 contains multiple distinct notebook/sweep states. Their dates, completion times, interventions, and later corrections must not be collapsed into one configuration.

## Witness marks and cam state

- White paint marks were described as the then-current baseline.
- Purple marks were historical.
- A later LF state moved both cams to blue by about one-sixth rotation before the truck had been fully settled/retested.
- Later passenger-front and rear-cam photographs/witness marks identify other distinct physical states.
- Paint colors are state labels only. They do not mean good/bad/correct by themselves.

## Cam and adjuster complications

- Front and rear lower-control-arm eccentric cams are coupled caster/camber controls.
- Some historical adjusters were described as seized or difficult to move.
- Bolt rotation, eccentric rotation, pivot displacement, and final tightened witness-mark position are different observations.
- Clockwise/counterclockwise is meaningless without the viewing direction.
- Inward/outward physical pivot motion is not determined by wrench rotation alone near an eccentric extremum.
- A finite number of flats is not a constant degrees-of-caster conversion.

## Repairs and hardware state

Historical work mentions front-end repairs including tie-rod, bearing, ball-joint, bushing/control-arm, and seized-adjuster work. Those changes can matter when deciding whether two measurement generations belong to the same mechanical state. They are not separate Econometrician features.

## Steering, scrub, settling, and body motion

- Steering the wheels can jack the suspension and change body heave/roll/pitch.
- Ackermann/unequal left-right road-wheel angles therefore interact with the shared body attitude.
- Tire scrub, approach direction, jouncing/rolling, and whether the truck has settled can change the observed state.
- Repeated driver-side right-turn pullback across several sweeps is a useful regression pattern, but it is not by itself proof of one mechanical cause.

## Gauge and ruler context

- The magnetic camber gauge has a main angle reading and a perpendicular bubble; the direction of bubble motion can serve as sign/orientation evidence.
- Ruler/level measurements constrain specific body/reference states. A straight-ahead body measurement does not imply the body pose stays fixed through a steering sweep.
- A deliberate 46/49 in reference setup and a later 47.5/47.5 in state must not be treated as interchangeable measurements of the same thing.

## Toe-specific caution

- Tie-rod turns and toe angle are different quantities.
- Thread engagement is a mechanical constraint, not a calibration from turns to degrees.
- Caster/camber adjustments can change toe, so toe is normally evaluated after the caster/camber state is settled under the applicable service procedure.

## How this note should be used

These facts may be used as:
- provenance fixtures;
- historical state-transition examples;
- negative/regression tests;
- examples of sign/frame ambiguity;
- examples of stale recommendations that should be invalidated.

They should **not** each become Econometrician software issues. The software backlog should remain about generic machinery: typed evidence/state, physical forward model and Jacobian, steering/body coupling, state-transition identification, uncertainty conditioning, nonlinear inverse inference, executable receipts, dependent-type enforcement, and regression tests.
