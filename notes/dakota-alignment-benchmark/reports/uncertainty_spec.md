# Uncertainty taxonomy and representation

The benchmark keeps uncertainty kinds distinct. `src/dakota_benchmark/uncertainty.py` implements the first-order containers; it does not coerce them into one scalar error bar.

## Numerical stochastic uncertainty

Use a covariance only when a numerical stochastic interpretation is justified. The old script's `sigma_gamma=0.25°` and `sigma_alpha=15°` are **illustrative assumptions explicitly labeled as such in the source**, not empirical Dakota tolerances. They are retained as model-history evidence, not promoted into the benchmark's measured covariance.

For a justified numerical covariance `Sigma_x`, first-order propagation is

`Sigma_y ≈ J Sigma_x J^T`.

This operation is valid only for the numerical covariance component and only near a linearization point where the model and error interpretation are adequate.

## Shared and correlated uncertainty

A shared source is represented by loadings `L` from latent errors `u` into the state. If `Cov(u)=S`, its numerical covariance contribution is `L S L^T`, but the benchmark also retains the source label and loading. This prevents repeated observations from pretending a common level zero or steering calibration is independent row noise.

Cross-correlation belongs in a joint covariance. Ordinary root-sum-of-squares is used only after independence has been asserted, never inferred from separate files or repeated readings.

## Bounded uncertainty

A bound remains a bound. For a first-order interval box with state radii `r`, the conservative output box radius is `|J| r`. This is not a probability statement.

Examples in this record include dictated ranges such as straight passenger `+1.125° to +1.25°`, driver full-right `−6° to −6.5°`, and several Sep12 row ranges.

## Feasible-set / geometric uncertainty

Some uncertainty is a region defined by equations and inequalities. It should be represented by constraints, not independent per-coordinate error bars. Examples include uncertain steering geometry, normalized eccentric position plus unknown clock phase, and inverse images `f^{-1}(Y)`.

## Model uncertainty

Uncertainty about the physical map is not measurement noise. The working eccentric map

`delta camber ≈ -1.3 u_front - 0.7 u_rear`

`delta caster ≈ -1.0 u_front + 1.0 u_rear`

is an uncalibrated model. Its coefficient uncertainty is model uncertainty until actual before/after cam moves calibrate it.

Likewise, ideal Ackermann geometry is a model choice, not a measurement of the Dakota rack/tires/compliance.

## Symbolic epsilon uncertainty

Unknown tolerance without a justified magnitude is represented symbolically. A term such as

`x + epsilon[level_zero] + epsilon[unresolved_steering]`

records the existence and provenance of uncertainty without inventing a variance or interval. Distinct epsilon labels are not ordered.

## Mixed representations

Forward propagation returns separate components:

- covariance parts;
- shared/systematic parts;
- interval parts;
- symbolic epsilon coefficient maps;
- feasible-region constraints;
- model-uncertainty notes.

They are not collapsed into a single `±sigma` by the library.

## Audited final-bar path

`build_covariance_receipt` is the stricter path for a reported numerical error
bar. It requires:

- a Jacobian with named inputs/outputs and units;
- covariance labels in exactly the same order as the Jacobian inputs;
- a stable source ID and provenance for every contribution;
- an explicit independence assertion before separate covariance sources are
  added;
- non-overlapping atomic effect IDs, so one physical uncertainty is not entered
  twice under different names.

Shared systematics enter through one latent loading/covariance block. The
receipt retains every propagated contribution and the total rather than only a
final square root.

`nonlinear_box_receipt` compares the local `|J|r` interval with direct nonlinear
evaluation. It reports asymmetric lower/upper deviations. A corner envelope is
labeled a complete box interval only when the caller separately establishes
that the extrema occur at corners; otherwise it remains a diagnostic sample.

`require_compatible_observations` rejects estimates assembled across different
generations, adjustment states, sides, sweeps, or approach directions.
`audit_resampling_plan` rejects designed steering positions as IID units and
refuses a bootstrap effect that is already covered by an explicit error source.
