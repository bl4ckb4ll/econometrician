# Dyadic numeric representation for statistical work

This note extends issues #61 and #62 with concrete external implementations.

The point is not that every statistical quantity is exactly dyadic. The point is that **decimal notation should not define the statistical object or its uncertainty**.

## Preserve exact structure where it exists

Examples that should not be rounded to decimal merely for convenience:

- counts: integers;
- exact design ratios and sample fractions: rationals;
- powers-of-two resolutions: dyadics;
- small structural factors such as 1/3 or 2/3: rationals/triadics until an approximation boundary;
- measurement increments such as halves, quarters, eighths, or sevenths when those are how the instrument/procedure is actually resolved.

A printed value such as `0.125` is presentation for the exact dyadic `1/8`; the decimal string is not the mathematical definition.

## Approximate quantities still need an explicit error object

A p-value, transcendental function, fitted parameter, or numerical integral generally cannot be kept as an exact dyadic rational. That does not make a long decimal the right semantic carrier.

Prefer the conceptual form

```
approximation + declared numerical error/bound
```

and choose the arithmetic width so that numerical error is negligible relative to the model/data/measurement error budget.

This is the same distinction already required by #61:

```
model/data uncertainty != arithmetic rounding != display formatting
```

## External precedent

### HoTT Book

`HoTT/book@578b85cc8d586b1677ec4335148adeb443057d24` identifies dyadic rationals `n / 2^k` as an approximate field suitable for constructive computer implementation.

### Lean 4

`leanprover/lean4@2c2bdd9630a7a6c51d7620d5efefcdba104f38f3` implements canonical dyadics as zero or odd numerator times a power of two. Exact addition/multiplication stay exact; inverse/division become explicit precision-bounded operations (`invAtPrec`, `divAtPrec`) when the exact rational result is not dyadic.

That is a useful statistical pattern: make the approximation request explicit at the operation where exactness is lost.

### ConwayHs

`ming-t18/ConwayHs@d80a4ced80527c28306c781b60ae560975ab394a` independently implements arbitrary-precision `n / 2^p` dyadics and normalizes away factors of two. No repository license is declared at that revision, so this is reference evidence only.

## Dakota / Jacobian consequence

For the Dakota work, do not manufacture decimal sigmas or decimal perturbations merely because software wants a float.

Keep separately:

1. the observed measurement/readout granularity;
2. the exact intervention unit where known (turn, half-turn, flat, fraction of a span, etc.);
3. empirical/model uncertainty;
4. the Jacobian or nonlinear response map;
5. numerical approximation error.

Derivative-weighted measurement error belongs to the physical/statistical error propagation. Floating-point roundoff is a different term and should normally be much smaller.

## Implementation direction

A future econometrician numeric layer can accept exact integers/rationals/dyadics at the boundary, evaluate with the coarsest justified representation, and retain a finer oracle only to certify that arithmetic error is below the declared inferential error budget.

Detailed compiler-oriented source notes and permitted upstream mirrors live in `isomorphisms/idric-arm-thumb: _/dyadic-rationals/`.
