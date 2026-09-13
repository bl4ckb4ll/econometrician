# Inverse uncertainty

The benchmark uses “inverse uncertainty” in the broad inverse-problem sense:

Given an uncertain observation set `Y`, determine the state set compatible with it, `f^{-1}(Y)`.

It does not define inverse error bars as `1/sigma` or assume a precision matrix `Sigma^{-1}` unless a separate statistical model justifies that operation.

## Linearized tools

`src/dakota_benchmark/inverse.py` provides:

- singular-value/rank/nullity diagnostics;
- a pseudoinverse solution that returns the nullspace and says whether the solution is unique;
- coordinate-wise interval feasibility for `|J x - y_center| <= y_radius` using linear programming.

The pseudoinverse routine labels its output `minimum_norm_dx`; it never labels an underdetermined result “the inferred state.”

## Dakota consequence

For the 14×26 candidate Jacobian, nullity is 12 at the diagnostic reference. Therefore no unique linearized inverse exists. Even the smaller coefficient/geometry/calibration model has exact and near dependencies. A narrow inverse error bar produced by blindly inverting a square submatrix would be a property of the chosen submatrix/regularizer, not evidence that the suspension state is identified.

## Nonlinear and branch issues

The real inverse must eventually account for:

- eccentric periodicity/clock phase;
- steering geometry and actual road-wheel angles;
- suspension constraints;
- settling/hysteresis state;
- multiple possible physical states producing similar camber sweeps;
- bounds and witness marks;
- symbolic unresolved tolerances.

Those effects make the natural object a constrained feasible set or collection of branches, not necessarily an ellipsoid.
