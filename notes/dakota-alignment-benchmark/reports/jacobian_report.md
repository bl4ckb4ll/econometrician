# Large Jacobian report

## Implemented object

`src/dakota_benchmark/measurement_model.py` implements the 14×26 Jacobian of the recovered candidate sweep observation map. Row/column names and units are in `data/jacobian_spec.json`; the numeric diagnostic matrix is in `data/candidate_large_jacobian.csv`.

The numerical reference point uses coefficients from the old quarter-degree / ideal-Ackermann scenario solely so derivatives can be exercised against a nontrivial state. Those coefficients are disputed model outputs and are **not** accepted Dakota alignment values.

## Derivative provenance

Analytic columns:

- `gamma0`, `B`, `K` for each side;
- common level bias;
- side gauge biases.

Centered finite-difference columns:

- nominal steering ratio;
- wheelbase;
- front track;
- each of 14 per-reading steering-angle offsets.

The regression suite compares the hybrid Jacobian with an all-centered-finite-difference Jacobian and requires maximum disagreement below `2e-6` at the diagnostic reference.

## Rank and conditioning

At that reference:

- full candidate Jacobian: shape 14×26, rank 14, nullity 12;
- first 12 columns (coefficients + nominal geometry + calibration biases): rank 9, nullity 3;
- first 9 columns (coefficients + geometry): rank 9, with a condition number of roughly `4.1e11` over its numerically nonzero singular values;
- first 6 coefficient columns are full column rank and moderately conditioned, **conditional on treating steering geometry and calibration as known**.

The full matrix's finite nonzero condition number does not rescue identifiability. It is underdetermined by dimension: there are 26 state/nuisance coordinates and 14 observations. A pseudoinverse therefore picks one minimum-norm point among a family; it does not identify the truck state.

There are also exact calibration dependencies: driver `gamma0` and driver gauge bias have the same observation direction; passenger `gamma0` and passenger gauge bias likewise, while common level bias couples both sides.

## Sparsity and units

Rows are camber degrees. Most columns affect only one side; common geometry/calibration columns couple sides. Per-reading steering offsets are row-local. Units are explicit in the JSON spec, so derivative values are interpreted as output degrees per named state unit rather than as dimensionless entries.

## What is not implemented as fact

No verified full physical suspension Jacobian was recovered. In particular, the uncalibrated 2×2-per-side eccentric paper model is kept separately in `cam_effect_model.py` / `data/paper_cam_effect_jacobian.csv` instead of being fused into the sweep Jacobian as though calibrated.
