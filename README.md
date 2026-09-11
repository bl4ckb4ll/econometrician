# econometrician

A narrow, inspectable statistics program.  The first slice implements the two
Pearson chi-square procedures treated in Larry Wasserman's *All of Statistics*:

- multinomial goodness of fit (section 10.4), and
- independence in a contingency table (sections 15.4 and 15.9).

The statistical calculation is deterministic.  A language model may eventually
translate an ordinary-language question into the input record, but it does not
choose the test, alter the data, or calculate the answer.

## Run it

Python 3.10 or later is sufficient; there are no third-party dependencies.

```sh
python3 econometrician.py <<'EOF'
{"test":"goodness_of_fit","observed":[315,101,108,32],"probabilities":[0.5625,0.1875,0.1875,0.0625],"alpha":0.05}
EOF
```

```sh
python3 econometrician.py <<'EOF'
{"test":"independence","observed":[[90,165],[84,307]],"alpha":0.05}
EOF
```

Output is JSON and includes observed and expected counts, each cell's
contribution, the statistic, degrees of freedom, p-value, decision, and warnings.
The decision is deliberately written as `reject` or `do_not_reject`; failure to
reject is not reported as evidence that the null is true.

## Input contract

Counts must be nonnegative finite numbers.  Goodness-of-fit probabilities must
be strictly positive and sum to one (within `1e-9`).  Independence tables must be
rectangular and have at least two nonempty rows and columns.  Zero expected
counts are rejected.  Expected counts below five are reported because the
chi-square reference distribution is an asymptotic approximation.

## Test

```sh
python3 -m unittest -v
```

The book is a boundary and reference, not training data checked into this
repository.  Fixtures here are independently written numeric cases, with a
single well-known Mendel calculation used as a regression check.

## Wasserman bootstrap conformance slice

[`bootstrap_conformance.py`](bootstrap_conformance.py) is a deliberately small,
deterministic reference implementation of the ordinary nonparametric bootstrap
for one estimator: the scalar arithmetic mean.  It exists to give models and
other implementations a numerical oracle, not to pretend that arbitrary
bootstrap inference is solved.

The caller must explicitly state `sampling="iid"` and
`resampling_unit="observation"`.  The slice implements only the basic/pivotal
interval, only exact enumeration of the empirical bootstrap distribution, and
refuses dependent/time-series data, cluster resampling, weighted observations,
other estimators, other interval methods, and exact state spaces above 100,000
resamples.  It never silently substitutes a Monte Carlo method.

Example:

```sh
python3 bootstrap_conformance.py <<'EOF'
{"observed":[1,2,3,4],"sampling":"iid","resampling_unit":"observation","estimator":"mean","interval":"basic_bootstrap","mode":"exact","alpha":0.05}
EOF
```

For `[1,2,3,4]`, the exact 4^4 empirical-bootstrap oracle is: estimate `2.5`,
bootstrap standard error `0.5590169943749475`, 0.025/0.975 bootstrap-estimate
quantiles `[1.5,3.5]`, and basic interval `[1.5,3.5]`.  Exact enumeration removes
finite-`B` Monte Carlo error; it does **not** establish that bootstrap coverage is
valid for an arbitrary estimator or sampling process.

[`test_bootstrap_conformance.py`](test_bootstrap_conformance.py) checks that
numeric oracle plus negative-valued observations and refusal cases for unstated
IID sampling, dependence, non-observation resampling units, unsupported interval
methods, and an excessive exact state space.

## Wasserman bootstrap model acceptance

[`wasserman_bootstrap_cases.jsonl`](wasserman_bootstrap_cases.jsonl) contains
small prompt-to-oracle cases derived from the linked Normal Deviate bootstrap and
subsampling posts plus explicitly labeled project conformance boundaries.  They
test formula and interpretation boundaries rather than prose similarity:
pivotal interval endpoint order, the empirical bootstrap CDF, with- versus
without-replacement resampling, finite-B Monte Carlo error, bootstrap validity,
subsampling scaling, the `b_n` asymptotic regime, frequentist coverage
interpretation, the exact small-mean oracle above, and refusal of unsupported
dependence.

A model runner should emit one JSON object per case in this form:

```json
{"id":"bootstrap_basic_interval_endpoint_order","answer":{"method":"basic_bootstrap","interval":[9.7,10.2]}}
```

Then check the complete sweep with:

```sh
python3 check_wasserman_bootstrap.py model_answers.jsonl
```

The checker accepts declared numerical tolerances, requires every case exactly
once, and prints `PASS`, `FAIL`, and a final `RESULT`.  It does not call a model
or the network.  The general `econometrician.py` dispatcher remains the chi-square
slice; the exact bootstrap reference is intentionally separate until a broader
runtime contract is justified.

## Sources and next methods

[WASSERMAN.md](WASSERMAN.md) links and summarizes five Normal Deviate posts on
bootstrap, subsampling, randomized computation, permutation tests, and
Bayesian/frequentist interpretation. It also links the book's bootstrap chapter
and records the source-reuse decisions.  The repository links and summarizes
these sources; it does not mirror the book chapter or blog article text.

## Research notes — not implemented methods

[Identifying a suspension response map](notes/suspension-response-identification.md)
uses the Dakota eccentric-cam example to separate experimental identification,
inverse conditioning, nuisance effects, input error, correlated observations,
and geometric curvature. Cross-linked with ASE, Fulton, and Coxeter. No new
runtime method, general-purpose bootstrap, or measured truck calibration is
claimed.
