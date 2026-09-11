# Identifying a suspension response map

Date: 2026-09-11.

**Status: research/design note, not an implemented statistical method or a calibrated truck model.** The program's existing chi-square dispatcher and narrowly specified bootstrap slice are unchanged. Neither accepts the experiment described here.

This is the Econometrician in a Box companion to the owner's discussion of how intentional eccentric-cam adjustments and unintended variations reach caster, camber, and other observations.

## Source trail and companion notes

The [ASE derivation](https://github.com/the-twin-pines/ASE/blob/a4-suspension-steering/notes/dakota-cam-jacobian-curvature.md) supplies the suspension setting and existing mathematical model. Its inspected source blob at this cross-post was `4e0e47d6813db3c4dc5bc1dd68f23f9c98fe9287`. [ASE's evidence plan](https://github.com/the-twin-pines/ASE/blob/a4-suspension-steering/notes/suspension-response-cross-repository.md) owns physical and measurement validity.

[Fulton](https://github.com/walnut-burgundy/fulton/blob/main/references/mikhail-gromov/suspension-response-geometry.md) separates response nonlinearity from geometric curvature. [Coxeter](https://github.com/isomorphismes/coxeter/blob/main/notes/suspension-response-structure.md) records the mathematical structures and transformation laws. The inference formulas below are derived for their stated models; they are not a claim that Gromov studied econometric identification or this truck.

## 1. Define the estimand before fitting anything

For one front wheel, let `q=(q_f,q_r)` denote actual front/rear eccentric rotations. Let `u=c(q)` denote measured or modeled pivot displacements, and let `eta` contain independently specified conditions such as loading, pad geometry, and measurement reference. A repeatable settled branch gives

$$y=F(q;\eta)+\epsilon,\qquad y=(\gamma,\chi),$$

where `F` here includes the cam-to-pivot map. The local target is

$$J_q=\left.\frac{\partial F}{\partial q}\right|_{q_0,\eta_0}.$$

A derivative with respect to pivot displacement is a different estimand. Record units, coordinate directions, operating point, and what is held fixed. A road-wheel steering sweep estimates a different response and cannot replace cam variation.

Loading may alter ride height, which then alters alignment. Conditioning on observed ride height is not equivalent to holding the truck at an externally controlled ride height. It may remove part of the total load effect. Decide whether the desired derivative is a total settled response or a direct response with a specified state constrained.

If approach direction and settling history change the result, model or restrict that history. A single-valued smooth response is an assumption, not a consequence of having two recorded settings.

## 2. Two distinct rank questions

**Identification from an experiment:** can the observations distinguish the coefficients of a local response model? For increments around a fixed operating point,

$$\Delta y_k\approx J_q\Delta q_k+B\Delta\eta_k+\epsilon_k.$$

The experimental design must distinguish the two cam directions from each other and from included nuisance changes. Varying both cams only in one fixed ratio identifies at most their response along that direction. Repeating that ratio does not supply the missing direction.

**Inversion of an identified response:** can a desired output change be achieved stably using the cams? This depends on the rank and scaled singular values of `J_q` itself. A well-designed experiment can identify a nearly singular response accurately. Conversely, an invertible physical response can be poorly estimated from a deficient experiment. Do not collapse these failures into one label.

For a quadratic two-input fit, the columns are `1, delta q_f, delta q_r, (delta q_f)^2/2, delta q_f delta q_r, (delta q_r)^2/2`. Six independent design columns are needed per output; six distinct settings do not guarantee rank, and an exact six-point fit leaves no residual information for assessing noise. Repeats, returns to baseline, and separate prediction checks are needed beyond algebraic solvability.

Physical execution remains subject to ASE's service and measurement gates. This note does not prescribe an adjustment sequence or justify forcing an immovable component.

## 3. Correlation, input error, and systematic error

Caster and camber derived from shared observations are paired outputs. Preserve the raw readings and their common references. If `d=D r` forms differences of a raw observation vector `r`, then

$$\operatorname{Cov}(d)=D\operatorname{Cov}(r)D^T.$$

All pairwise differences of `n` scalar readings have rank at most `n-1`; pair count is not independent sample size. A reused baseline correlates subsequent differences. Repeating measurements does not average away an unknown fixed gauge offset.

Unknown actual cam/pivot movements create an errors-in-variables problem. Ordinary output-noise-only regression treats its inputs as known; it does not become appropriate merely because the commanded wrench movements were carefully counted. Retain input uncertainty or specify and justify a latent-input model.

A trend correlated with cam settings is not automatically an intervention effect. Load drift, settling order, or changing supports can be confounded with the settings. Controlled interventions or explicit identifying assumptions are needed. Fitting a flexible curve does not supply those assumptions.

## 4. Uncertainty propagation and inverse sensitivity

For small centered variations in `x=(q,eta)`, with independent residual sensor noise,

$$\Sigma_y\approx D_xF\,\Sigma_x\,D_xF^T+\Sigma_\epsilon.$$

The full covariance retains correlations among inputs. If sensor noise is correlated with them, the corresponding cross-covariance terms must also be included. For component `a`, the second-order mean shift is

$$\mathbb E[F_a(x+\delta x)]-F_a(x)\approx\tfrac12\operatorname{tr}(H_a\Sigma_x).$$

These are local Taylor approximations. They do not model stick-slip transitions or unidentified systematic bias.

Choose fixed output whitening/scaling `L` and input scales `S`, so `delta q=S delta v`. Then the scaled response is `J_bar=L J_q S`. A small singular value means weak output change per unit of the declared input scale, and potentially large inverse uncertainty. Scaling by tolerances expresses adjustment priorities; scaling by noise expresses statistical distinguishability. They need not be the same metric.

For a **declared Gaussian observation model with known constant nonsingular covariance** `Sigma`, differentiating its log likelihood gives expected local information

$$I_q=J_q^T\Sigma^{-1}J_q.$$

This equality has hypotheses. Do not label arbitrary tolerance weighting as Fisher information, or omit covariance-derivative terms in a model whose covariance depends on the unknowns. An inverse-information approximation also omits uncertainty in an estimated Jacobian unless that uncertainty is separately propagated.

### Unknown conditions can remove information

For the local Gaussian mean model `J_q delta q+B delta eta`, put `W=Sigma^{-1}`. When `B^T W B` is invertible, eliminating freely fitted nuisance increments gives the information for `q`

$$I_{q\mid\eta}=J_q^T WJ_q-J_q^T WB(B^T WB)^{-1}B^T WJ_q.$$

This is the Schur complement of the joint information matrix. It is **not** the same as knowing `eta` and holding it fixed. A cam-induced observation direction that an unknown condition can reproduce is not distinguishable in that local observation model. Repeated experiments with controlled conditions or additional observations can change this situation; a regularization penalty only adds assumptions or preferences, not new observations.

## 5. Curvature of the fitting problem

For fixed `W` and residual `r=F(q)-y_star`,

$$E=\tfrac12r^TWr,\qquad
\nabla^2E=J_q^TWJ_q+\sum_a(Wr)_a\nabla^2F_a.$$

The second term vanishes at an exact fit but can affect the inverse away from it. This objective Hessian is not automatically intrinsic curvature.

One particularly transparent geometric case is a standardized, unit-speed attainable curve `z(s)` with a normal residual `y_star=z(s_0)+r N(s_0)`. With `T'=kappa N`, the nearest-point objective satisfies

$$E''(s_0)=1-r\kappa,\qquad
\delta s=\frac{T\cdot\delta y_{star}}{1-r\kappa}.$$

The sensitivity formula concerns a regular local minimum with positive denominator. Global nearest-point uniqueness is a separate condition. This is a useful inverse-problem example, not an observed instability of the Dakota.

## 6. Requirements before any runtime implementation

A future deterministic method would need an explicit input contract for coordinate units, raw versus derived observations, input error, output covariance, dependence/repeated-measurement blocks, design rank, model neighborhood, and held-fixed conditions. It should return estimand, fit, uncertainty assumptions, prediction residuals, and rank/conditioning without converting invalid data into adjustment advice.

The existing IID arithmetic-mean bootstrap must not be reused for this dependent multivariate experiment by changing its label. Any future resampling method must justify its sampling and resampling units. Documentation of a possible method is not implementation or coverage evidence.

**Current result:** the statistical problem and its failure modes are specified; no truck-specific Jacobian, coefficient confidence interval, causal effect, or valid adjustment has been estimated.
