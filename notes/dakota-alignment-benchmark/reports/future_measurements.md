# Required future measurements

These are questions computation cannot resolve from the present record.

1. **Rebuild one canonical seven-position command/camber sweep; direct yaw is optional.** For every endpoint record steering-wheel command, side, camber, time/order, and whether the suspension was rolled/jounced/steered immediately before the read. Repeat the half/full/lock pairs so the odd-signal scale ratios and the two sides can test the declared 17.4:1 steering-map family. If a one-time external yaw calibration ever becomes practical, attach it as an additional constraint; do not block the procedure on it.
2. **Repeat each camber read without changing steering/state** enough times to estimate read scatter separately from setup/systematic error.
3. **Calibrate level/gauge zero** before and after a sweep so drift can be distinguished from common-mode offset.
4. **Use controlled level ground or measured ground plane** for ride height and repeat the spindle/front-pivot/rear-pivot measurements on both sides.
5. **Photograph each eccentric orthogonally before and after a move** with a fixed reference and record physical pivot displacement as well as bolt rotation. Keep the benchmark CW/CCW viewpoint: rear looking forward.
6. **Make isolated interventions**: one cam at a time, small known moves, with controlled settling and a complete before/after sweep. This is the minimum evidence needed to calibrate the cam-response Jacobian.
7. **Measure hysteresis/path effects** by approaching the same steering position from both directions after standardized rolling/jouncing.
8. **Recover the seven steering-angle estimates already mentioned in the work**, if they exist in a missing note/file, rather than reconstructing them from memory.
9. **Recover or restate the original curvature-Jacobian definition** before implementing it.
10. **For second-order identification**, repeat at several controlled intervention magnitudes around the same baseline. A Hessian/curvature term cannot be separated from state drift using one before/after move.

A good next experiment is not “more readings” in the abstract; it is a design
that separates the confounders the user can actually control: canonical command
records, calibrated common-mode offsets, controlled settling, repeated
half/full/lock pairs, and isolated cam inputs. Direct road-wheel angle would be
useful supplementary calibration, not a mandatory demand.
