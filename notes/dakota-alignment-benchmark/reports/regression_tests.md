# Regression and invariant tests

The suite is designed to fail if the benchmark silently changes a convention or erases a known failure mode.

Current checks:

- nominal steering-angle and caster-multiplier recomputation;
- ideal Ackermann reference angles under the recovered nominal geometry;
- nonlinear sensitivity of the multiplier to bounded steering-angle error;
- `epsilon_i^2=0` in both explicit epsilon algebras;
- distinct mixed-epsilon behavior between the two algebras;
- refusal to accept an unspecified epsilon algebra;
- correlated covariance propagation versus naive RSS;
- preservation of named shared/systematic loadings;
- separation of interval and symbolic propagation;
- 14×26 Jacobian dimensions and labels;
- hybrid analytic/numerical Jacobian agreement with an all-finite-difference calculation;
- structural nullity of the large inverse problem;
- exact calibration-column dependencies;
- nearest-curve `1-r*kappa` formula;
- refusal to invert the nearest-curve singular denominator;
- recovered sweep second derivative;
- refusal to invent a project-specific curvature Jacobian;
- source-manifest hash/size/source-ID integrity;
- evidence-ledger source-reference and category integrity;
- preservation of named unresolved discrepancies;
- fixed rear-looking-forward cam-rotation convention;
- benchmark refusal to claim unrecovered full-physical Jacobian, truck curvature, curvature Jacobian, or epsilon mixed-product rule.
- exact reproduction of the historical `12.0292°`, `8.0643°`, `5.5688°`, and
  `4.6±1.0°` failure-ledger entries;
- rejection of measurements from incompatible adjustment states;
- rejection of a covariance whose variable order differs from the Jacobian;
- source-by-source covariance receipts with units and provenance;
- refusal to add separate covariance sources without an independence assertion;
- refusal to count one atomic uncertainty effect twice;
- shared systematic error that does not shrink as independent pair noise;
- the historical half-turn `±5°` nonlinear interval, including its asymmetric
  `-1.7899/+5.1666°` deviations;
- refusal to bootstrap the seven designed steering positions as IID units;
- refusal to cover the same gauge-repeatability effect in both a bootstrap and
  an explicit measurement-error source;
- preservation and recomputation of all fourteen G5 reset-sweep rows.

At failure-audit build time: **36 tests passed**.

Run from the package root:

```sh
python -m pytest -q
```

The sibling legacy `../dakota-caster-recheck/dakota_caster_recheck.py` must preserve exact JSON structure and nonnumeric values while reproducing every float within `rtol=1e-7`, `atol=1e-9`. The tolerance admits cross-runner linear-algebra variation without admitting a change at the four-decimal precision used by the historical conclusions. That legacy receipt is deliberately separate from the new benchmark tests because it validates old implementation reproducibility, not source correctness.
