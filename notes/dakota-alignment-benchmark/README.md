# Dodge Dakota alignment audit and mathematical benchmark

**Audit version:** 2026-09-12-audit-1  
**Current acceptance:** **PARTIAL / NOT YET ACCEPTED FOR REUSABLE PHYSICAL THEORY**

This package reconstructs the recoverable 2005 Dodge Dakota alignment record and separates five evidence levels throughout:

1. observation;
2. convention;
3. derived result;
4. uncertainty statement;
5. interpretation/model.

A previous assistant answer, generated PDF, passing test, or reproducible fit is never promoted to observation merely because it is neat or repeatable. The machine-readable ledger uses only the five categories `observation`, `convention`, `derived_result`, `uncertainty_statement`, and `interpretation_model`; transcription/reconstruction quality lives in provenance fields rather than becoming a sixth evidence class.

## Main conclusions

### 1. The old caster fit is not a settled truck measurement

The recovered timestamped Sep10 passenger sequence runs from maximum right `0°` to maximum left `+6°`, while the saved script uses the same ascending values in a row vector labeled from left/negative to right/positive. A later passenger correction involving `4.75°` is also not mapped to a unique row/generation. The old robust-fit coefficients therefore remain **legacy model outputs**, not verified physical caster.

### 2. Steering-angle uncertainty can dominate the early caster calculation

For the symmetric model `C = Delta_gamma/(2 sin theta)`, the nominal half-turn angle is only `10.3448°`. If actual road-wheel angle is uncertain by `±5°`, the multiplier changes by about `−32%` to `+93%`. This is before adding camber-read error, settling, calibration, or model error. Early measurements with poorly known road-wheel angle need broad bounds/feasible sets or symbolic epsilon, not a narrow manufactured sigma.

### 3. Measurement generations must remain separate

Sep7/Sep10/Sep11/Sep12 observations were not all made with the same state or measurement quality. Later work contains explicit evidence of a passenger-front settling change after a cam move / steering path. The benchmark therefore stores generation and intervention state rather than taking a grand average.

### 4. The large recoverable Jacobian is intentionally non-identifying

The candidate observation model uses 14 camber observations and 26 state/nuisance coordinates. At the diagnostic reference it has rank 14 and nullity 12. The smaller coefficient/geometry/calibration block is rank-deficient and severely ill-conditioned. A pseudoinverse is a minimum-norm convention, not an identified suspension state.

### 5. Epsilon mixed products are unresolved

The design record distinguishes nilpotent `epsilon^2=0` from ordered nonstandard infinitesimals but does not settle whether distinct `epsilon_i epsilon_j` terms vanish. The implementation has no default: it supports both an individual-square-zero algebra and the stronger first-order square-zero-ideal algebra only when selected explicitly.

### 6. The project-specific “curvature Jacobian” was not recovered

The record contains ordinary Jacobian ideas, a sweep second derivative, and the valid general nearest-curve relation `E''=1-r kappa`, but no recovered definition of the named project object. The implementation refuses to invent one.

## Deliverables

1. **Evidence ledger** — 87 normalized rows with source/provenance/state fields, partitioned for review as `data/evidence_ledger_001-030.csv`, `data/evidence_ledger_031-060.csv`, and `data/evidence_ledger_061-087.csv`.
2. **Convention specification** — `reports/conventions.md` and `data/conventions.json`.
3. **Discrepancy ledger** — `data/discrepancy_ledger.csv` and `data/contradictions.jsonl`.
4. **Measurement-generation report** — `reports/measurement_generations.md`.
5. **Uncertainty taxonomy/representation** — `reports/uncertainty_spec.md` plus `src/dakota_benchmark/uncertainty.py`.
6. **Edriç epsilon specification** — `reports/epsilon_spec.md` plus `src/dakota_benchmark/epsilon.py`.
7. **Reproducible calculation suite** — `src/dakota_benchmark/geometry.py`, tests, and `reports/calculations.md`.
8. **Large Jacobian implementation** — `src/dakota_benchmark/measurement_model.py`, `data/candidate_large_jacobian.csv`, and `data/jacobian_spec.json`.
9. **Curvature Jacobian specification/implementation status** — `reports/curvature_jacobian.md` and the explicit refusal boundary in `curvature.py`.
10. **Inverse uncertainty implementation** — `src/dakota_benchmark/inverse.py` and `reports/inverse_uncertainty.md`.
11. **Combined-error implementation** — `src/dakota_benchmark/uncertainty.py` and `reports/combined_error.md`.
12. **Curvature / second-order report** — `reports/curvature_second_order.md`.
13. **Algebraic-geometry report** — `reports/algebraic_geometry.md`.
14. **Dakota benchmark dataset** — `data/benchmark.json` plus the ledgers, matrices, source manifest and contradictions.
15. **Regression and invariant tests** — `tests/`, `run_checks.sh`, `test_receipt_public.txt`, and `reports/regression_tests.md`.
16. **Downstream map** — `reports/downstream_map.md`.
17. **Required future measurements** — `reports/future_measurements.md`.

Additional requested phases are covered by `reports/sequential_inference_and_system_identification.md` and `reports/evidence_findings.md`.

## Source/provenance structure

This public repository copy intentionally does **not** duplicate the recovered personal photographs, screenshots, or other raw binary evidence. `data/source_manifest.csv` inventories 40 recovered/derived source artifacts and records their SHA-256 hashes, sizes, Library identifiers where available, and evidentiary roles. `data/evidence_ledger_001-030.csv`, `data/evidence_ledger_031-060.csv`, and `data/evidence_ledger_061-087.csv` preserve the normalized provenance links. The private audit package also retains `data/raw_evidence.jsonl`; that derivative reconstruction is intentionally not duplicated into this public repository copy. The already-public legacy caster-recheck script and output remain in the sibling repository directory `notes/dakota-caster-recheck/`; this benchmark does not duplicate them. `run_checks.sh` uses that archive when run from the repository. See `SOURCES_NOT_INCLUDED.md`.

The prior conversation audit states that it could not recover complete original mechanical transcripts. A focused recovery for the later “seven steering-angle estimates” likewise found no exact numeric table or method record, so that benchmark slot remains explicitly missing. This package therefore does **not** claim that every historical utterance has been restored. Missing primary conversation evidence is represented as a source limitation, not filled from model output. Any visual reinspection must return to the original private source artifact rather than treating this public derivative package as a replacement.

## Running the checks

```sh
./run_checks.sh
```

Current receipt:

- 22 new benchmark tests pass;
- the recovered legacy caster script regenerates its saved JSON byte-for-byte.

The second result demonstrates old-code reproducibility only. It does not resolve the passenger row-direction/value conflicts.

## Safe use boundary

The package is suitable now for:

- source/provenance auditing;
- uncertainty-representation experiments;
- rank/conditioning/nullspace examples;
- checked Jacobian software infrastructure;
- symbolic epsilon design experiments with explicit algebra choice;
- sequential-identification design.

It is **not** suitable yet for:

- using the old fit as the truck's caster;
- prescribing a new cam rotation from the paper coefficients;
- claiming a recovered full suspension Jacobian;
- claiming a truck-specific curvature Jacobian;
- assigning one Gaussian covariance to the entire experiment;
- treating a pseudoinverse as a uniquely inferred alignment state.
