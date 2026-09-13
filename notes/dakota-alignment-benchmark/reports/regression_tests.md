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

At package build time: **22 tests passed**.

Run from the package root:

```sh
python -m pytest -q
```

The sibling legacy `../dakota-caster-recheck/dakota_caster_recheck.py` also regenerates its saved JSON byte-for-byte in the current environment. That legacy receipt is deliberately separate from the new benchmark tests because it validates old implementation reproducibility, not source correctness.
