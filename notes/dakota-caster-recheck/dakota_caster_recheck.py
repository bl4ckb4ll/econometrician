#!/usr/bin/env python3
"""Reproducible Dakota caster-sweep sensitivity comparison.

Requires Python 3, numpy, scipy. Run:
    python3 dakota_caster_recheck.py > dakota_caster_recheck_results.json

This is a model comparison, NOT a calibrated alignment or cam-adjustment rule.
No observations are silently deleted. Ambiguous transcriptions are separate scenarios;
range midpoints are explicit summaries, not additional independent samples.
The driver's -5 degree full-right value remains photo-derived and unconfirmed.

Angles:
  alpha = steering-wheel rotation, radians, positive right.
  theta = individual road-wheel yaw, radians, positive right.
  gamma = measured camber, degrees.
  gamma = gamma0 + B*sin(theta) + K*(1-cos(theta)).
  Reported caster-related magnitude is -B for driver, +B for passenger.
  Equating those coefficients with physical caster is an approximation.

Working geometry assumptions:
  wheelbase 131.3 in, front track 62.8 in;
  constant ratio 17.4:1 interpreted as equivalent center-wheel angle;
  stops symmetric at +/- 1.59 steering-wheel turns.
  'ackermann' means ideal Ackermann, NOT measured Dakota rack kinematics.

Uncertainty assumptions for the main comparison:
  sigma_gamma = 0.25 degree, sigma_alpha = 15 degrees.
  These are illustrative one-standard-deviation scales, NOT measured tolerances.
  Independent errors, no systematic angle/level/camber zero covariance.
  First-order propagation includes the full alpha -> theta -> gamma chain.
  Huber transition is 1.345 standardized residuals; effective variances
  are frozen in each convex inner fit and recomputed between fits.
  This iterated effective-variance method is NOT a full errors-in-variables
  maximum-likelihood fit and does not generate confidence intervals.

Method references:
  https://www.mathworks.com/help/vdynblks/ref/kinematicsteering.html
  https://www.itl.nist.gov/div898/handbook/mpc/section5/mpc55.htm
  https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html
"""
from __future__ import annotations
import json
import sys
import numpy as np
from scipy.optimize import least_squares

WHEELBASE = 131.3
FRONT_TRACK = 62.8
RATIO = 17.4
TURNS = np.array([-1.59, -1., -0.5, 0., 0.5, 1., 1.59])
ALPHA = TURNS * 2 * np.pi

def steering_map(alpha: np.ndarray, side: str,
                 ackermann: bool) -> tuple[np.ndarray, np.ndarray]:
    if side not in ("driver", "passenger"):
        raise ValueError("side must be driver or passenger")
    alpha = np.asarray(alpha, dtype=float)
    delta = alpha / RATIO
    if not ackermann:
        return delta, np.full(delta.shape, 1.0 / RATIO)
    k = FRONT_TRACK / (2 * WHEELBASE)
    if side == "passenger":
        k = -k
    t = np.tan(delta)
    theta = np.arctan2(t, 1 + k * t)
    dtheta_dalpha = (1 + t*t) / ((1 + k*t)**2 + t*t) / RATIO
    return theta, dtheta_dalpha

def readings(side: str, driver_half_left: float = 0.25,
             passenger_full_left: float = 0.25) -> np.ndarray:
    if side == "driver":
        return np.array([3.75, 2.25, driver_half_left, -2.375,
                         -3.5, -4.5, -5.0])
    if side == "passenger":
        return np.array([0., passenger_full_left, 0.5, 1.125,
                         2.5, 4.25, 6.])
    raise ValueError("unknown side")

def fit(side: str, gamma: np.ndarray, ackermann: bool = True,
        sigma_alpha_deg: float = 15., sigma_gamma_deg: float = 0.25,
        huber_transition: float = 1.345,
        mask: np.ndarray | None = None) -> dict:
    gamma = np.asarray(gamma, dtype=float)
    if gamma.shape != TURNS.shape or not np.all(np.isfinite(gamma)):
        raise ValueError("exactly seven finite camber values are required")
    if sigma_alpha_deg < 0 or sigma_gamma_deg <= 0 or huber_transition <= 0:
        raise ValueError("invalid uncertainty scale or Huber transition")
    if mask is None:
        mask = np.ones(len(TURNS), dtype=bool)
    mask = np.asarray(mask, dtype=bool)
    theta, angle_derivative = steering_map(ALPHA, side, ackermann)
    design = np.column_stack((np.ones(len(theta)),
                              np.sin(theta), 1-np.cos(theta)))
    if np.linalg.matrix_rank(design[mask]) < 3:
        raise ValueError("included positions do not identify three coefficients")
    beta = np.linalg.lstsq(design[mask], gamma[mask], rcond=None)[0]
    converged = False
    for iteration in range(300):
        curve_derivative = beta[1]*np.cos(theta) + beta[2]*np.sin(theta)
        sigma = np.sqrt(sigma_gamma_deg**2 +
                        (curve_derivative * angle_derivative *
                         np.radians(sigma_alpha_deg))**2)
        xw = design[mask] / sigma[mask, None]
        yw = gamma[mask] / sigma[mask]
        result = least_squares(
            lambda b: xw @ b - yw, beta,
            # SciPy may transform the Jacobian for robust loss: return a copy.
            jac=lambda b: xw.copy(), loss="huber", f_scale=huber_transition,
            ftol=1e-12, xtol=1e-12, gtol=1e-12, max_nfev=1000)
        if not result.success:
            raise RuntimeError("inner fit failed: " + result.message)
        new_beta = result.x
        converged = np.max(np.abs(new_beta-beta)) < 1e-8
        beta = new_beta
        if converged:
            break
    if not converged:
        raise RuntimeError("effective-variance iteration did not converge")
    curve_derivative = beta[1]*np.cos(theta) + beta[2]*np.sin(theta)
    sigma = np.sqrt(sigma_gamma_deg**2 +
                    (curve_derivative * angle_derivative *
                     np.radians(sigma_alpha_deg))**2)
    residual = gamma - design @ beta
    huber_factor = np.minimum(
        1., huber_transition / np.maximum(np.abs(residual/sigma), 1e-100))
    factor_sign = -1 if side == "driver" else 1
    return dict(
        side=side,
        geometry="ideal_ackermann" if ackermann else "equal_angles",
        caster_related_coefficient_deg=float(factor_sign * beta[1]),
        coefficients_gamma0_B_K=beta.tolist(),
        steering_wheel_turns=TURNS.tolist(),
        road_wheel_angles_deg=np.degrees(theta).tolist(),
        observed_camber_deg=gamma.tolist(),
        predicted_camber_deg=(design@beta).tolist(),
        residual_camber_deg=residual.tolist(),
        effective_sigma_deg=sigma.tolist(),
        huber_factors=huber_factor.tolist(),
        total_weights=(huber_factor/sigma**2).tolist(),
        included_rows=mask.tolist(),
        sigma_alpha_deg=sigma_alpha_deg,
        sigma_gamma_deg=sigma_gamma_deg,
        huber_transition=huber_transition,
        outer_iterations=iteration+1, converged=True)

def checks() -> dict:
    errors = {}
    for side in ("driver", "passenger"):
        theta, derivative = steering_map(ALPHA, side, True)
        h = 1e-5
        numerical = (steering_map(ALPHA+h, side, True)[0] -
                     steering_map(ALPHA-h, side, True)[0]) / (2*h)
        error = float(np.max(np.abs(numerical-derivative)))
        if error > 1e-8:
            raise RuntimeError("steering-map derivative check failed")
        beta = np.array([0.3, -7. if side == "driver" else 7., 10.])
        design = np.column_stack((np.ones(len(theta)), np.sin(theta),
                                  1-np.cos(theta)))
        recovered = fit(side, design@beta)
        recovery_error = float(np.max(np.abs(
            np.array(recovered["coefficients_gamma0_B_K"])-beta)))
        if recovery_error > 1e-7:
            raise RuntimeError("noise-free synthetic recovery failed")
        errors[side] = dict(
            derivative_max_absolute_error=error,
            synthetic_recovery_max_absolute_error=recovery_error)
    return errors

def main() -> None:
    output = {
        "status": "illustrative sensitivity comparison; no confidence interval",
        "assumed_geometry": dict(wheelbase_in=WHEELBASE, front_track_in=FRONT_TRACK,
                                 ratio=RATIO, lock_to_lock_turns=3.18),
        "checks": checks(), "comparison": [], "scale_sensitivity": [],
        "additional_driver_sensitivity": []}
    scenarios = [
        ("earlier_large_transcriptions", 1.25, 4.0),
        ("quarter_degree_transcription_scenario", 0.25, 0.25)]
    for scenario, d, p in scenarios:
        for ack in (False, True):
            for side in ("driver", "passenger"):
                record = fit(side, readings(side, d, p), ackermann=ack)
                record["scenario"] = scenario
                output["comparison"].append(record)
    for sa in (5., 15., 30., 45.):
        for side in ("driver", "passenger"):
            record = fit(side, readings(side), sigma_alpha_deg=sa)
            output["scale_sensitivity"].append(record)
    for d in (0.25, 1.25, -1.0):
        for omit in (False, True):
            mask = np.ones(7, dtype=bool)
            mask[-1] = not omit
            record = fit("driver", readings("driver", d), mask=mask)
            record["driver_half_left"] = d
            record["omit_photo_only_full_right"] = omit
            output["additional_driver_sensitivity"].append(record)
    json.dump(output, sys.stdout, indent=2, allow_nan=False)
    print()

if __name__ == "__main__":
    main()
