#!/usr/bin/env python3
"""Trustworthy first scalar slice for the Dakota caster record.

The executable calculation is deliberately small. It loads two timestamped
raw camber observations, takes road-wheel steering angles as explicit inputs,
computes the signed odd sweep coefficient and its magnitude, emits the local
Jacobian, and checks analytic derivatives against centered finite differences.

It does not infer the eccentric-cam state, does not turn old illustrative
sigmas into evidence, and does not build the larger Jacobian.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Callable

RAD_PER_DEG = math.pi / 180.0


def load_evidence(path: Path) -> dict:
    return json.loads(path.read_text())


def signed_caster_coefficient(
    theta_right_deg: float,
    theta_left_deg: float,
    gamma_right_deg: float,
    gamma_left_deg: float,
) -> float:
    """Odd sine coefficient in degrees.

    C = (gamma_R - gamma_L) / (sin(theta_R) - sin(theta_L)).
    Steering angle signs are inputs; no symmetry is silently imposed.
    """
    tr = math.radians(theta_right_deg)
    tl = math.radians(theta_left_deg)
    denominator = math.sin(tr) - math.sin(tl)
    if abs(denominator) < 1e-15:
        raise ValueError("steering-angle denominator is zero")
    return (gamma_right_deg - gamma_left_deg) / denominator


def caster_magnitude(*args: float) -> float:
    return abs(signed_caster_coefficient(*args))


def analytic_jacobian_magnitude(
    theta_right_deg: float,
    theta_left_deg: float,
    gamma_right_deg: float,
    gamma_left_deg: float,
) -> list[float]:
    """d|C|/d(theta_R, theta_L, gamma_R, gamma_L).

    Theta derivatives are returned per degree of road-wheel steering input.
    Gamma derivatives are degrees caster per degree camber.
    """
    tr = math.radians(theta_right_deg)
    tl = math.radians(theta_left_deg)
    numerator = gamma_right_deg - gamma_left_deg
    denominator = math.sin(tr) - math.sin(tl)
    c = numerator / denominator
    if c == 0.0:
        raise ValueError("|C| is not differentiable at C = 0")
    sign_c = 1.0 if c > 0.0 else -1.0

    d_c_d_tr_rad = -numerator * math.cos(tr) / (denominator * denominator)
    d_c_d_tl_rad = +numerator * math.cos(tl) / (denominator * denominator)
    d_c_d_gr = 1.0 / denominator
    d_c_d_gl = -1.0 / denominator

    return [
        sign_c * d_c_d_tr_rad * RAD_PER_DEG,
        sign_c * d_c_d_tl_rad * RAD_PER_DEG,
        sign_c * d_c_d_gr,
        sign_c * d_c_d_gl,
    ]


def centered_difference(
    f: Callable[[float, float, float, float], float],
    x: list[float],
    index: int,
    step: float,
) -> float:
    plus = x.copy()
    minus = x.copy()
    plus[index] += step
    minus[index] -= step
    return (f(*plus) - f(*minus)) / (2.0 * step)


def derivative_check(x: list[float], analytic: list[float]) -> dict:
    steps = [1e-5, 1e-5, 1e-6, 1e-6]
    numerical = [
        centered_difference(caster_magnitude, x, i, steps[i])
        for i in range(4)
    ]
    absolute_errors = [abs(a - n) for a, n in zip(analytic, numerical)]
    tolerance = 1e-8
    return {
        "analytic": analytic,
        "finite_difference": numerical,
        "absolute_error": absolute_errors,
        "tolerance": tolerance,
        "pass": max(absolute_errors) <= tolerance,
    }


def build_result(
    evidence: dict,
    theta_right_deg: float,
    theta_left_deg: float,
) -> dict:
    observations = {
        row["steering_position"]: row for row in evidence["raw_observations"]
    }
    right = observations["0.5 turn right"]
    left = observations["0.5 turn left"]
    gamma_right = float(right["raw_value_deg"])
    gamma_left = float(left["raw_value_deg"])

    x = [theta_right_deg, theta_left_deg, gamma_right, gamma_left]
    signed = signed_caster_coefficient(*x)
    magnitude = abs(signed)
    jacobian = analytic_jacobian_magnitude(*x)
    derivative = derivative_check(x, jacobian)

    hist = evidence["historical_comparison"]
    range_low, range_high = 5.0, 6.0
    agreement = range_low <= magnitude <= range_high

    printed_multiplier = 2.784
    exact_symmetric_multiplier = None
    if math.isclose(theta_right_deg, -theta_left_deg, abs_tol=1e-12):
        exact_symmetric_multiplier = 1.0 / (
            2.0 * math.sin(math.radians(abs(theta_right_deg)))
        )
    historical_table_reproduction = (
        abs(gamma_right - gamma_left) * printed_multiplier
    )

    labels = [
        "theta_right_deg",
        "theta_left_deg",
        "gamma_right_deg",
        "gamma_left_deg",
    ]
    expression_terms = [
        {
            "source": "delta_theta_right_deg",
            "coefficient": jacobian[0],
            "unit": "deg caster per deg road-wheel angle",
        },
        {
            "source": "delta_theta_left_deg",
            "coefficient": jacobian[1],
            "unit": "deg caster per deg road-wheel angle",
        },
        {
            "source": "delta_gamma_right_deg",
            "coefficient": jacobian[2],
            "unit": "deg caster per deg camber",
        },
        {
            "source": "delta_gamma_left_deg",
            "coefficient": jacobian[3],
            "unit": "deg caster per deg camber",
        },
    ]

    return {
        "slice_id": evidence["slice_id"],
        "status": "checked_scalar_slice",
        "provenance": {
            "generation": evidence["generation"],
            "side": evidence["side"],
            "raw_observations": evidence["raw_observations"],
            "metadata": evidence["metadata"],
            "steering_angle_input": {
                **evidence["steering_angle_input"],
                "right_used_deg": theta_right_deg,
                "left_used_deg": theta_left_deg,
            },
        },
        "calculation": {
            "formula_signed": (
                "C = (gamma_R - gamma_L) / "
                "(sin(theta_R) - sin(theta_L))"
            ),
            "formula_reported": "|C|",
            "signed_odd_coefficient_deg": signed,
            "caster_magnitude_deg": magnitude,
            "exact_symmetric_multiplier_if_applicable": exact_symmetric_multiplier,
            "input_vector": dict(zip(labels, x)),
        },
        "linearization": {
            "base_caster_magnitude_deg": magnitude,
            "terms": expression_terms,
            "unresolved_symbolic_epsilons": evidence["uncertainty_policy"][
                "unresolved_symbolic_epsilons"
            ],
            "epsilon_rule": evidence["uncertainty_policy"]["epsilon_rule"],
            "automatic_independence_assumption": False,
            "note": (
                "No RSS/sigma collapse is performed. Correlated perturbations remain "
                "separate; a covariance matrix may be applied later only if supported."
            ),
        },
        "jacobian_row": {
            "quantity": "caster_magnitude_deg",
            "columns": labels,
            "values": jacobian,
            "theta_derivative_unit": "deg caster per deg road-wheel angle",
            "gamma_derivative_unit": "deg caster per deg camber",
        },
        "derivative_check": derivative,
        "historical_comparison": {
            "reported_symmetric_pair_range_deg": [range_low, range_high],
            "recomputed_inside_reported_range": agreement,
            "result": "agreement" if agreement else "discrepancy",
            "historical_all_data_robust_fit_deg": hist[
                "reported_all_data_robust_fit_deg"
            ],
            "all_data_fit_is_not_same_calculation": True,
            "printed_reference_multiplier": printed_multiplier,
            "result_using_printed_multiplier_deg": historical_table_reproduction,
            "exact_minus_printed_multiplier_result_deg": (
                magnitude - historical_table_reproduction
            ),
        },
        "uncertainty_boundary": {
            "numerically_propagated_first_order_sources": expression_terms,
            "legacy_illustrative_sigmas_excluded": evidence["uncertainty_policy"][
                "do_not_import_as_evidence"
            ],
            "unresolved": evidence["uncertainty_policy"][
                "unresolved_symbolic_epsilons"
            ],
        },
        "finish_condition": {
            "raw_inputs_deterministic": True,
            "documented_caster_result": True,
            "named_first_order_uncertainty_contributions": True,
            "symbolic_epsilon_retained": True,
            "checked_jacobian_row": derivative["pass"],
            "finite_difference_agreement": derivative["pass"],
            "historical_discrepancy_report": True,
            "large_jacobian_not_constructed": True,
            "physical_accuracy_claimed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path(__file__).with_name("evidence.json"),
    )
    parser.add_argument("--theta-right-deg", type=float)
    parser.add_argument("--theta-left-deg", type=float)
    args = parser.parse_args()

    evidence = load_evidence(args.evidence)
    nominal = evidence["steering_angle_input"]
    theta_right = (
        nominal["right_nominal_deg"]
        if args.theta_right_deg is None
        else args.theta_right_deg
    )
    theta_left = (
        nominal["left_nominal_deg"]
        if args.theta_left_deg is None
        else args.theta_left_deg
    )

    result = build_result(evidence, theta_right, theta_left)
    if not result["derivative_check"]["pass"]:
        raise SystemExit("finite-difference derivative check failed")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
