# Required future measurements

These are questions computation cannot resolve from the present record.

1. **Rebuild one canonical seven-position sweep with measured road-wheel yaw.** For every endpoint record steering-wheel command, direct driver/passenger road-wheel angles, camber, time/order, and whether the suspension was rolled/jounced/steered immediately before the read.
2. **Repeat each camber read without changing steering/state** enough times to estimate read scatter separately from setup/systematic error.
3. **Calibrate level/gauge zero** before and after a sweep so drift can be distinguished from common-mode offset.
4. **Use controlled level ground or measured ground plane** for ride height and repeat the spindle/front-pivot/rear-pivot measurements on both sides.
5. **Photograph each eccentric orthogonally before and after a move** with a fixed reference and record physical pivot displacement as well as bolt rotation. Keep the benchmark CW/CCW viewpoint: rear looking forward.
6. **Make isolated interventions**: one cam at a time, small known moves, with controlled settling and a complete before/after sweep. This is the minimum evidence needed to calibrate the cam-response Jacobian.
7. **Measure hysteresis/path effects** by approaching the same steering position from both directions after standardized rolling/jouncing.
8. **Recover the seven steering-angle estimates already mentioned in the work**, if they exist in a missing note/file, rather than reconstructing them from memory.
9. **Recover or restate the original curvature-Jacobian definition** before implementing it.
10. **For second-order identification**, repeat at several controlled intervention magnitudes around the same baseline. A Hessian/curvature term cannot be separated from state drift using one before/after move.

A good next experiment is not “more readings” in the abstract; it is a design that breaks the current confounders: direct angle measurement, calibrated common-mode offsets, controlled settling, and isolated cam inputs.
