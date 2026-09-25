# Low-precision Jacobian residual diagnostic

This diagnostic asks a narrower question than the Dakota physical-model work:

> If the existing candidate Jacobian is stored in one of the compact numeric
> formats, what residuals appear when the matrix is used forward and backward?

It is a numerical representation experiment. It does not promote the candidate
14×26 Jacobian to a verified physical suspension Jacobian and does not turn its
pseudoinverse into an identified truck state.

## Inputs

The diagnostic reads the existing
`data/candidate_large_jacobian.csv` rather than inventing a toy matrix.

Two matrix slices are exercised:

- the full 14×26 candidate Jacobian, which has row rank 14 but is
  underdetermined as a state inverse;
- the first six coefficient columns, a 14×6 full-column-rank block with much
  better conditioning.

The binary32-parsed CSV is the arithmetic reference for this experiment.

## Formats

The executable uses the numeric implementations from ICK merge
`90c003e042fa967872ed3408c25c55ec59315b9b`:

- binary32 control;
- Float16;
- E4M3;
- E5M2;
- E3M2;
- E5M3.

E5M3 itself is unsigned and has no zero encoding. A signed Jacobian therefore
cannot be represented by E5M3 alone. For this diagnostic only, each nonzero
entry is stored as an E5M3 **magnitude** plus an external sign; exact zero is
carried by the sidecar. The report names this path `E5M3+sign` so it is not
mistaken for a new signed E5M3 type. Values outside E5M3's source domain are
counted and mapped to zero for the purpose of completing the diagnostic rather
than aborting the whole sweep.

## Forward paths

For each format the matrix and state vector are quantized to storage and then
decoded.

The primary path is:

```text
compact storage -> binary32 -> matrix multiplication
```

That is the path intended to test computational headroom: compact values are
not repeatedly rounded during multiply/accumulate.

For Float16, E4M3, E5M2, and E3M2 a second diagnostic deliberately performs
each multiply and add through the narrow arithmetic contract and requantizes
after every operation. This is included as a contrast, not as the preferred
matrix algorithm.

E5M3 has no arithmetic contract, so there is no requantize-each-term path for
it.

## Backward paths

For the full 14×26 matrix the diagnostic constructs test states in the row
space of the binary32 reference Jacobian. That makes recovery through the
reference pseudoinverse meaningful despite the matrix's 12-dimensional
nullspace.

The minimum-norm solve is implemented as

```text
x = Jᵀ (J Jᵀ)⁻¹ y
```

using binary32 arithmetic after storage decode.

For the 14×6 coefficient block the diagnostic uses ordinary least squares via

```text
x = (Jᵀ J)⁻¹ Jᵀ y
```

again in binary32.

If quantization makes a solve numerically singular, the diagnostic tries a
small sequence of diagonal ridge values and reports the ridge used. This is a
run-to-completion diagnostic, not a claim that the regularized result is the
physical inverse.

## Reported residuals

Residual magnitude is never a pass/fail criterion. The job fails only if the
diagnostic cannot compile, cannot read the real matrix, aborts before producing
a report, or fails to reach `report_complete`.

The report includes:

- matrix-storage residuals;
- count of nonzero entries quantized to zero;
- unsupported E5M3 magnitudes;
- forward residuals with binary32 computation;
- forward residuals when every term is requantized;
- inverse state residuals;
- residual after storing the recovered state again;
- residual after pushing the recovered state back through the reference
  Jacobian;
- self-roundtrip observation residual;
- inverse failures and any ridge required.

This deliberately replaces comparisons dominated by arbitrary large scalar
stress values with residuals from the actual matrix used in the econometric
benchmark.
