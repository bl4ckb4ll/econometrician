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

## Error-source isolation: steering input map

A 2026-09-17 steering-sweep diagnostic isolates one important uncertainty source from generic camber-reading noise: the map from commanded steering-wheel rotation to actual road-wheel angle.

The diagnostic compared the odd camber signal at half-turn and one-turn steering commands. The working values recorded in the conversation were:

- driver: `1.81 / 0.625 ≈ 2.90`;
- passenger: `0.75 / 0.25 = 3.00`.

A simple proportional steering-command model would make the one-turn signal roughly twice the half-turn signal over this range. Both sides instead gave nearly the same ratio near three. That bilateral agreement is evidence against explaining the discrepancy solely as one bad camber reading on one wheel. It is not enough to identify the mechanical cause.

Keep the following distinction explicit in later caster work:

`steering-wheel command -> actual road-wheel angle -> camber/caster observation`.

The first arrow is an input-calibration problem. Do not silently replace actual road-wheel angle with a fixed steering ratio, and do not dump disagreement from that map into a generic output-noise sigma. A useful model should allow

`theta_actual = G(steering_command, side, direction/history, state)`

with `G` potentially nonlinear. Shared steering geometry, Ackermann effects, rack/steering-arm geometry, compliance, body/setup attitude, and path-dependent settling are candidate explanations or nuisance terms; this diagnostic does not choose among them.

The two sides also should not automatically be treated as independent replications of the steering-angle error. They share the steering command and much of the mechanism, so a common or correlated input-error component is plausible. Inverse-variance weighting is not justified without an established dependence structure for the steering-map error.

What this diagnostic establishes is narrower: steering-angle calibration/model error is a structurally distinct source that should be represented separately in the Jacobian/error-in-variables analysis. It does not by itself establish actual road-wheel angles, a corrected caster value, or a probability distribution for the error.

A direct road-wheel-angle calibration sweep would turn part of this source from an unresolved model/input error into measured input data, but it is optional rather than a prerequisite. When yaw cannot be measured, preserve a named steering-map epsilon or bounded/function-valued feasible family and use multi-scale, bilateral consistency checks rather than inventing a narrow Gaussian error bar.

## Combination receipt and dependence

The audited API does not infer independence from a list of covariance objects.
Adding more than one source requires a written zero-cross-covariance assertion.
Every source has a stable ID and a set of atomic effects it covers; duplicate
effects are refused.

When several caster estimates are combined, use their complete estimate
covariance. A shared unit-variance systematic plus independent variance `0.25`
on each of three pair estimates gives variance

```text
1 + 0.25/3 = 1.083333...
```

for their equal-weight mean. Treating each total variance `1.25` as independent
would instead report `1.25/3 = 0.416667`, incorrectly shrinking the shared
source. This regression is based on the dependence structure of the three G2
pairs; it does not assign those illustrative numbers to the truck.
