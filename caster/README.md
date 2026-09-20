# Caster uncertainty receipts

This directory contains independent R, Ithon, Haskell, Agda, and Idriç
implementations of the small caster calculation that exposed the Dakota
failure modes.  The R and Haskell programs consume the common files; the
Ithon, Agda, and Idriç programs are independent typed acceptance kernels for
the same historical inputs and failure guards.  The programs calculate; prose
and chat do not supply numeric results.

The executable contract is intentionally narrow:

1. Read two endpoint observations with immutable provenance.
2. Reject a pair whose generation, adjustment state, side, sweep, approach
   direction, or steering source differs.
3. Calculate

   ```text
   |C| = |(gamma_right - gamma_left)
          / (sin(theta_right) - sin(theta_left))|.
   ```

4. Calculate the analytic Jacobian in the declared order

   ```text
   theta_right_deg, theta_left_deg, gamma_right_deg, gamma_left_deg
   ```

   and check it by centered finite differences.
5. If covariance sources are supplied, validate their labels, symmetry,
   positive-semidefiniteness, source identities, and covered effects before
   calculating `J Sigma J^T`.
6. If bounds are supplied, report both the first-order interval and the exact
   nonlinear box interval.  A bound is not a probability distribution.
7. Audit a proposed resampling plan before any bootstrap.  Designed steering
   positions are not IID draws, and an effect already present in an explicit
   covariance source cannot also enter through resampling.  For symmetric
   steering data the plan must keep each `+delta/-delta` pair inside one
   independent sweep/session unit; the odd and even camber components are both
   retained and must be recomputed after group resampling.
8. Emit a line-oriented receipt that states what was calculated and what was
   not established.

The primary case is [`cases/g2-passenger-half-turn`](cases/g2-passenger-half-turn).
Its road-wheel angles are the nominal values implied by the documented 17.4:1
overall steering ratio.  They are not arbitrary and they are not direct
per-wheel angle measurements.  No numerical angle tolerance is invented.
Consequently the primary receipt contains no statistical error bar.

The case's `bounds.tsv` preserves the historical `+/-5 deg` road-wheel exercise
under the explicit kind `historical_stress_test_not_measurement_uncertainty`.
It exists to catch inadequate first-order propagation, not to describe the
Dakota.

## Input files

`observations.tsv` has one `right` and one `left` row.  Angles and camber are in
degrees.  `theta_source_kind` distinguishes a nominal geometry model from a
direct observation.

Optional covariance inputs use two files:

- `sources.tsv` records a stable source ID, source type, semicolon-separated
  covered effects, provenance, and whether its scale is empirical.
- `covariance.tsv` records matrix cells by source ID and named row/column.

If more than one covariance source is added, `policy.tsv` must contain a
nonempty `independence_assertion`; adding the matrices asserts zero
cross-covariance.  Reusing a covered effect in two sources is rejected.

`bounds.tsv` records one nonnegative radius per named input.  `resampling.tsv`
records the sampling structure, resampling unit, group identity, symmetric
`pair_id`, `pair_role` (`plus` or `minus`), and covered effects.  A valid
odd/even bootstrap plan has at least two genuinely independent sweep/session
groups, gives every group the same pair set, and contains exactly one plus and
one minus member of every pair.  The current surviving single-sweep Dakota
record therefore cannot produce a bootstrap error bar; the programs validate
the future resampling structure but do not manufacture independent groups.
All formats are ordinary tab-separated text, not JSON.

## Run

From the repository root:

```sh
Rscript caster/r/caster_receipt.R caster/cases/g2-passenger-half-turn
ithon caster/ithon/caster_receipt.pi
runghc caster/haskell/CasterReceipt.hs caster/cases/g2-passenger-half-turn
```

The Agda and Idriç programs are typed, independently evaluated kernels for the
same G2 case and the covariance/nonlinearity invariants.  They intentionally do
not duplicate the TSV ingestion boundary.  See their source headers for that
boundary.

Run all available local checks with:

```sh
./caster/run_checks.sh
```

The check script reports a language as `BLOCKED`, never `PASS`, when its real
frontend is unavailable.  CI installs or pins the named frontends.
