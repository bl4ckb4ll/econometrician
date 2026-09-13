# Sequential inference and system identification

## Sequential inference

The chronological record should be processed as constraints with changing quality, not as exchangeable samples.

- **G0/G1:** broad constraints. Steering angle is largely model-derived; handwriting/transcription and uncontrolled state are important. Numeric posterior variances would be misleading.
- **G2:** timestamped passenger observations improve row provenance, but they expose a row-direction conflict with the saved script. The admissible state should split into alternative source mappings rather than average them.
- **G3:** substantially different spot readings indicate changed state or an earlier mapping error. They should widen the model class to include state/path dependence rather than be treated as outliers automatically.
- **G4:** later driver values are better reconciled within-session, but the passenger canonical table and exact steering-angle metrology remain missing. They sharpen some constraints without retroactively improving G1/G2.

A sequential implementation should therefore carry a set/mixture of source hypotheses plus numerical and symbolic uncertainty. Evidence quality is attached to the observation at acquisition time.

## System identification

The deliberate cam moves are inputs and the alignment/suspension responses are outputs. The current intervention record is enough to define an identification problem but not enough to identify a global suspension model.

Potential local input vector:

`u = [driver front cam move, driver rear cam move, passenger front cam move, passenger rear cam move, steering path]`.

Potential output vector includes camber sweep coefficients/readings, direct road-wheel angles, ride height, and witness-mark/pivot coordinates.

The generated paper model predicts a local cam response, but it was not calibrated from controlled before/after interventions. The observed passenger-front settling after an outward move is direct evidence that a latent state/path term may be needed. Therefore a static linear map `Delta y = A Delta u` is a hypothesis to test, not an accepted model.

## Econometrics-in-a-box

The Dakota record already contains real examples of:

- errors-in-variables: road-wheel angle is uncertain while used as a regressor/input;
- common-mode error: level/gauge/steering calibration can affect many rows;
- latent state: settling/hysteresis is only partly observed;
- interventions: cam moves are deliberate inputs;
- confounding: cam movement and suspension settling can occur before a sweep;
- changing measurement quality: later procedure is better than early nominal-angle work;
- identification failure: the candidate 14×26 Jacobian has a 12-dimensional nullspace;
- model misspecification: residuals need not be stochastic noise or curvature;
- designed observations: seven steering positions are not IID draws and should not be bootstrapped as if they were.

The physical mechanism should stay in the benchmark. The point is not to turn the truck into a generic regression table; it is to have a compact real experiment where the assumptions behind statistical machinery are visible.
