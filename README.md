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
