# Wasserman: sources for econometrician-in-a-box

Reviewed: 2026-09-06. These are original source notes, not mirrored articles.
The implementation directions below are project proposals, not claims that the
corresponding methods are already implemented.

## What was already present

[PR #1: Implement checked Wasserman chi-square slice](https://github.com/bl4ckb4ll/econometrician/pull/1)
was opened on 2026-09-01 and was still unmerged when these notes were prepared.
Its implementation commit is
[`f693f8d99885eea1ae507b6573e1c79a4751dab6`](https://github.com/bl4ckb4ll/econometrician/commit/f693f8d99885eea1ae507b6573e1c79a4751dab6).

The existing [README](https://github.com/bl4ckb4ll/econometrician/blob/f693f8d99885eea1ae507b6573e1c79a4751dab6/README.md)
identifies the reference boundary as Pearson multinomial goodness of fit
(*All of Statistics*, section 10.4) and contingency-table independence
(sections 15.4 and 15.9). The branch contains code and tests, not a copy of the
chapter or book. This distinction matters: the chi-square work was started;
book-text ingestion was not established by the repository evidence.

## Book reference

Larry Wasserman, *All of Statistics: A Concise Course in Statistical Inference*,
Springer, first edition, copyright 2004.
[Publisher record](https://link.springer.com/book/10.1007/978-0-387-21736-9).

For the next uncertainty-estimation slice, add
[Chapter 8, The Bootstrap, pp. 107–118](https://link.springer.com/chapter/10.1007/978-0-387-21736-9_8)
as a reference alongside the chi-square sections. The publisher record identifies
the book as subscription content with Springer copyright; no permission to
mirror the book is being inferred here.

## Normal Deviate source entries

Author: Larry Wasserman. The blog's
[About page](https://normaldeviate.wordpress.com/about/) links to his CMU page.
Each entry below refers to the author's post, not to reader comments.

### ND-001 — Bootstrapping and Subsampling: Part I

Published: 2013-01-19.
[Original post](https://normaldeviate.wordpress.com/2013/01/19/bootstrapping-and-subsampling-part-i/).
Reuse status: `open_license_not_found`; action: `link_and_original_summary`.

Wasserman presents bootstrap uncertainty estimation by replacing an unknown
distribution with the empirical distribution and repeatedly recomputing the
estimator. He derives a basic/pivotal confidence interval rather than simply
taking the raw estimate quantiles as endpoints. His enthusiasm is qualified:
high dimension and irregular statistical functionals can invalidate coverage.
This is a foundation for general uncertainty estimation, not permission to
apply one bootstrap recipe indiscriminately.

Project implication: make resampling a first-class facility that accepts an
estimator and returns its resampling distribution, standard error, and explicitly
named interval method. Keep interval conventions and applicability visible.

### ND-002 — Bootstrapping and Subsampling: Part II

Published: 2013-01-27.
[Original post](https://normaldeviate.wordpress.com/2013/01/27/bootstrapping-and-subsampling-part-ii/).
Reuse status: `open_license_not_found`; action: `link_and_original_summary`.

Subsampling draws smaller samples without replacement and uses their estimator
distribution with the appropriate scaling. It can remain valid under weaker
conditions than the ordinary bootstrap. The post requires an appropriate
continuous, nondegenerate limiting distribution; its asymptotic subsample regime
has b increasing while b/n tends to zero. Choosing b remains a practical problem,
and asymptotic validity is not a finite-sample coverage guarantee.

Project implication: keep subsampling distinct from ordinary bootstrap. Record
subsample size and scaling, and assess sensitivity rather than silently choosing
an arbitrary b and presenting it as universally reliable.

### ND-003 — The Value of Adding Randomness

Published: 2013-06-09.
[Original post](https://normaldeviate.wordpress.com/2013/06/09/the-value-of-adding-randomness/).
Reuse status: `open_license_not_found`; action: `link_and_original_summary`.

The post distinguishes randomness already present in observations from
randomness deliberately introduced into a statistical procedure. Its examples
include randomized experiments, permutation tests, bootstrap computation,
randomized initialization, cross-validation, and posterior sampling. For the
bootstrap, repeated simulation makes an otherwise difficult conditional
sampling distribution computationally accessible.

Project implication: distinguish the statistical uncertainty being estimated
from the extra simulation variability introduced by a finite computational run.
Record the random seed, random-number generator, and number of draws.

### ND-004 — Modern Two-Sample Tests

Published: 2012-07-14.
[Original post](https://normaldeviate.wordpress.com/2012/07/14/modern-two-sample-tests/).
Reuse status: `open_license_not_found`; action: `link_and_original_summary`.

Wasserman describes kernel, energy, and cross-match approaches to comparing
distributions. A central point is that permutation calibration can handle
complicated statistics when the null makes group labels exchangeable. This is
a different inferential operation from estimating uncertainty with an ordinary
bootstrap, even though both involve repeated computation.

Project implication: give permutation testing its own interface and assumptions.
Validate finite-simulation p-value conventions independently before implementing
them; an informal blog derivation is not itself an executable correctness test.

### ND-005 — What Is Bayesian/Frequentist Inference?

Published: 2012-11-17.
[Original post](https://normaldeviate.wordpress.com/2012/11/17/what-is-bayesianfrequentist-inference/).
Reuse status: `open_license_not_found`; action: `link_and_original_summary`.

Wasserman separates inferential goals from computational machinery. In his
account, frequentist inference seeks repeated-sampling guarantees, while
Bayesian inference describes uncertainty through beliefs and their updating.
A posterior interval does not automatically have its advertised probability
as frequentist coverage; a confidence interval is not automatically a posterior
probability statement. He argues against treating either approach as uniformly
superior.

Project implication: distinguish confidence intervals from credible intervals
in the output schema. Attach the method, assumptions, and intended interpretation
to the numerical endpoints rather than calling every interval a CI.

## Implementation direction — not implemented by this documentation change

Bootstrap uncertainty estimation should be central rather than an afterthought.
The program should run an explicitly selected estimator on explicit resamples,
not have a language model invent interval endpoints. Preserve the original
estimate alongside the resampled estimates. Treat basic/pivotal, percentile,
studentized, and bias-corrected/accelerated intervals as distinct methods to
implement and validate, not interchangeable names.

Proposed acceptance work: deterministic fixtures for interval arithmetic;
reproducible resampling; coverage experiments under declared sampling models;
and negative cases in which the chosen method should warn or refuse a claim.
The resampling unit and dependence assumptions must be explicit. More resamples
should never be presented as a substitute for checking the sampling model.

A proposed result record includes the estimate, target quantity, sample size,
sampling/resampling scheme, interval kind and level, standard error where
available, seed and generator, draw count, failed-draw count, and applicability
warnings. Mark these as future capabilities until the corresponding code and
checks exist. The current executable remains the chi-square slice.

## Reuse decision

On 2026-09-06, no explicit open-content license was found on the five linked
posts or the blog's About page. This is a bounded inspection result, not a claim
that no permission could exist elsewhere. Public readability is not being
used as permission to mirror full text, figures, or comments.

Keep canonical links, bibliographic metadata, and these original summaries.
Mirror source material only after recording a verified license or permission,
its scope, and its attribution/redistribution requirements. A WordPress reblog
control or a repository license must not be treated as a license for the author's
articles. No article, comment, figure, or book PDF is mirrored by this change.
