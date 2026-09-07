# Econometrician on Oodriç

This branch is a real numerical-program probe for `isomorphisms/Idric` branch `Oodriç`.

It branches from the current Wasserman-style exact-bootstrap work at `c32c594f624ba80e512cb18a42699aa1ef260fc2`, rather than the nearly empty `main` branch, so the Oodriç program has an existing deterministic oracle.

## First program

`oodric/BootstrapMean.idric` computes the ordinary nonparametric bootstrap standard error of the scalar arithmetic mean by enumerating every ordered size-n resample with replacement.

For `[1, 2, 3, 4]` it evaluates all `4^4 = 256` resamples. The existing Python reference gives:

- estimate: `2.5`
- bootstrap standard error: `0.5590169943749475`

The Oodriç source is intentionally explanatory rather than dependency ordered: `main` appears first, then the bootstrap calculation, then its numerical and resampling machinery. This exercises forward references in recursive list-producing numerical code rather than another synthetic compiler test.

## Scope

This first slice is deliberately narrower than the full econometrician bootstrap contract. It establishes exact enumeration and the scalar-mean standard-error oracle. The basic interval, checked refusal boundaries, and other supported statistics remain governed by the existing reference implementation until equivalent Oodriç acceptance exists.

The compiler probe pins `isomorphisms/Idric` at `b7ac1eea7adca7c44a68d465a24a55c8e0830c4c`.
