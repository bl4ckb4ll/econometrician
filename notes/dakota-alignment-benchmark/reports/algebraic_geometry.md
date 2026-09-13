# Algebraic-geometric structure

The benchmark contains a small amount of genuine constraint structure, but not enough to claim a global algebraic model of the Dakota suspension.

## Candidate sweep constraints

Introduce `s_i = sin(theta_i)` and `c_i = cos(theta_i)`. Each row of the recovered sweep model satisfies

`s_i^2 + c_i^2 - 1 = 0`

and

`gamma_i - gamma0 - B s_i - K(1-c_i) - biases = 0`.

For ideal Ackermann with `t=tan(delta)` and local wheel angle `(s,c)`, the recovered rational relation can be written locally as

`(1 + k t) s - t c = 0`

for the appropriate side sign of `k`, together with `s^2+c^2=1`.

These equations define a useful lifted constraint set for the **candidate measurement model**. Their tangent map is directly related to the implemented Jacobian.

## Eccentric constraint

The paper eccentric model `x=e cos(phi)` can similarly be lifted with `c=cos(phi), s=sin(phi), c^2+s^2=1`. But `e`, clock phase, slot geometry, and the physical link from pivot displacement to wheel alignment are not calibrated in the recovered record.

## Identifiability and singularity

The 14×26 candidate observation map is non-identifiable by dimension. Calibration biases add exact tangent dependencies. The nominal geometry block is also nearly dependent for this experimental design. These are real tangent-space/identifiability results; they do not require decorative algebraic geometry.

No supported claim is made yet about a global suspension variety, its dimension, singular loci, or elimination ideal. Establishing those requires a physical constraint model or enough controlled interventions to identify one.
