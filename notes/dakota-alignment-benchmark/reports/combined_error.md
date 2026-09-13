# Combining multiple error sources

There is no universal combine rule.

## Independent numerical components

If two numerical errors are justified as independent and stochastic, their covariance contributions may be added. The library requires the caller to make that independence choice explicitly.

## Correlated numerical components

Use the full covariance including cross terms. A regression test uses two unit-variance errors with correlation `0.8`; for output `x1+x2`, the variance is `3.6`, not the independent-RSS value `2.0`.

## Shared systematic sources

Represent a common source once with a loading vector/matrix. Seven readings sharing one level zero do not create seven independent level-zero errors, and repeating the sweep does not automatically reduce that source.

## Nested derived errors

Dependency provenance matters. If a caster estimate and a fitted coefficient both use the same camber reading, their errors are correlated by construction. They must not be treated as two independent summaries of evidence.

## Intervals and feasible sets

Bounds propagate as sets. First-order interval boxes use `|J|r`; nonlinear inverse work should instead propagate through the actual constraints when possible.

## Symbolic epsilons

Unknown tolerances stay as named epsilon terms. A symbolic level-zero epsilon and steering-angle epsilon are carried separately; no numerical variance is invented, and no ordering is assumed.

## Model uncertainty

Uncertainty in the eccentric-response coefficients, Ackermann approximation, or hysteresis law stays in a separate model-uncertainty layer. It is not repaired by adding more decimal places to a measurement covariance.
