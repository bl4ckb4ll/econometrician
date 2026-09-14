#!/usr/bin/env python3
"""Checked scalar Dakota caster slice. No large-Jacobian work belongs here."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

RAD_PER_DEG = math.pi / 180.0


def load_evidence(path: Path) -> dict:
    return json.loads(path.read_text())


def signed_caster_coefficient(theta_right_deg, theta_left_deg,
                              gamma_right_deg, gamma_left_deg):
    """Odd sine coefficient; steering signs are inputs, not hidden constants."""
    tr = math.radians(theta_right_deg)
    tl = math.radians(theta_left_deg)
    denominator = math.sin(tr) - math.sin(tl)
    if abs(denominator) < 1e-15:
        raise ValueError("steering-angle denominator is zero")
    return (gamma_right_deg - gamma_left_deg) / denominator


def caster_magnitude(*x):
    return abs(signed_caster_coefficient(*x))


def analytic_jacobian_magnitude(theta_right_deg, theta_left_deg,
                                gamma_right_deg, gamma_left_deg):
    """d|C|/d(theta_R, theta_L, gamma_R, gamma_L), all inputs in degrees."""
    tr = math.radians(theta_right_deg)
    tl = math.radians(theta_left_deg)
    n = gamma_right_deg - gamma_left_deg
    d = math.sin(tr) - math.sin(tl)
    c = n / d
    if c == 0.0:
        raise ValueError("|C| is not differentiable at C = 0")
    s = 1.0 if c > 0.0 else -1.0
    return [
        s * (-n * math.cos(tr) / d**2) * RAD_PER_DEG,
        s * (+n * math.cos(tl) / d**2) * RAD_PER_DEG,
        s * (1.0 / d),
        s * (-1.0 / d),
    ]


def centered_difference(x, index, step):
    plus, minus = x.copy(), x.copy()
    plus[index] += step
    minus[index] -= step
    return (caster_magnitude(*plus) - caster_magnitude(*minus)) / (2 * step)


def derivative_check(x, analytic):
    steps = [1e-5, 1e-5, 1e-6, 1e-6]
    numerical = [centered_difference(x, i, h) for i, h in enumerate(steps)]
    errors = [abs(a - n) for a, n in zip(analytic, numerical)]
    tolerance = 1e-8
    return {
        "analytic": analytic,
        "finite_difference": numerical,
        "absolute_error": errors,
        "tolerance": tolerance,
        "pass": max(errors) <= tolerance,
    }


def build_result(evidence, theta_right_deg, theta_left_deg):
    rows = {r["steering_position"]: r for r in evidence["raw_observations"]}
    gamma_right = float(rows["0.5 turn right"]["raw_value_deg"])
    gamma_left = float(rows["0.5 turn left"]["raw_value_deg"])
    x = [theta_right_deg, theta_left_deg, gamma_right, gamma_left]

    signed = signed_caster_coefficient(*x)
    magnitude = abs(signed)
    jacobian = analytic_jacobian_magnitude(*x)
    check = derivative_check(x, jacobian)
    labels = ["theta_right_deg", "theta_left_deg",
              "gamma_right_deg", "gamma_left_deg"]
    terms = [
        {"source": "delta_theta_right_deg", "coefficient": jacobian[0],
         "unit": "deg caster per deg road-wheel angle"},
        {"source": "delta_theta_left_deg", "coefficient": jacobian[1],
         "unit": "deg caster per deg road-wheel angle"},
        {"source": "delta_gamma_right_deg", "coefficient": jacobian[2],
         "unit": "deg caster per deg camber"},
        {"source": "delta_gamma_left_deg", "coefficient": jacobian[3],
         "unit": "deg caster per deg camber"},
    ]

    symmetric = math.isclose(theta_right_deg, -theta_left_deg, abs_tol=1e-12)
    multiplier = (
        1.0 / (2 * math.sin(math.radians(abs(theta_right_deg))))
        if symmetric else None
    )
    printed_result = abs(gamma_right - gamma_left) * 2.784
    hist = evidence["historical_comparison"]
    magnitude_agrees = 5.0 <= magnitude <= 6.0

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
            "formula_signed":
                "C = (gamma_R - gamma_L) / (sin(theta_R) - sin(theta_L))",
            "formula_reported": "|C|",
            "signed_odd_coefficient_deg": signed,
            "caster_magnitude_deg": magnitude,
            "exact_symmetric_multiplier_if_applicable": multiplier,
            "input_vector": dict(zip(labels, x)),
        },
        "linearization": {
            "base_caster_magnitude_deg": magnitude,
            "terms": terms,
            "unresolved_symbolic_epsilons":
                evidence["uncertainty_policy"]["unresolved_symbolic_epsilons"],
            "epsilon_rule": evidence["uncertainty_policy"]["epsilon_rule"],
            "automatic_independence_assumption": False,
            "note": "No RSS/sigma collapse; correlated perturbations remain separate.",
        },
        "jacobian_row": {
            "quantity": "caster_magnitude_deg",
            "columns": labels,
            "values": jacobian,
            "theta_derivative_unit": "deg caster per deg road-wheel angle",
            "gamma_derivative_unit": "deg caster per deg camber",
        },
        "derivative_check": check,
        "historical_comparison": {
            "reported_symmetric_pair_range_deg": [5.0, 6.0],
            "recomputed_inside_reported_range": magnitude_agrees,
            "magnitude_result": "agreement" if magnitude_agrees else "discrepancy",
            "direction_label_result": "discrepancy",
            "direction_label_discrepancy": hist["direction_label_discrepancy"],
            "direction_discrepancy_effect": hist["direction_discrepancy_effect"],
            "signed_historical_comparison_status":
                "not accepted: historical left/right labels conflict with timestamped evidence",
            "historical_all_data_robust_fit_deg":
                hist["reported_all_data_robust_fit_deg"],
            "all_data_fit_is_not_same_calculation": True,
            "printed_reference_multiplier": 2.784,
            "result_using_printed_multiplier_deg": printed_result,
            "exact_minus_printed_multiplier_result_deg": magnitude - printed_result,
        },
        "uncertainty_boundary": {
            "numerically_propagated_first_order_sources": terms,
            "legacy_illustrative_sigmas_excluded":
                evidence["uncertainty_policy"]["do_not_import_as_evidence"],
            "unresolved":
                evidence["uncertainty_policy"]["unresolved_symbolic_epsilons"],
        },
        "finish_condition": {
            "raw_inputs_deterministic": True,
            "documented_caster_result": True,
            "named_first_order_uncertainty_contributions": True,
            "symbolic_epsilon_retained": True,
            "checked_jacobian_row": check["pass"],
            "finite_difference_agreement": check["pass"],
            "historical_discrepancy_report": True,
            "large_jacobian_not_constructed": True,
            "physical_accuracy_claimed": False,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path,
                        default=Path(__file__).with_name("evidence.json"))
    parser.add_argument("--theta-right-deg", type=float)
    parser.add_argument("--theta-left-deg", type=float)
    args = parser.parse_args()

    evidence = load_evidence(args.evidence)
    nominal = evidence["steering_angle_input"]
    tr = nominal["right_nominal_deg"] if args.theta_right_deg is None else args.theta_right_deg
    tl = nominal["left_nominal_deg"] if args.theta_left_deg is None else args.theta_left_deg
    result = build_result(evidence, tr, tl)
    if not result["derivative_check"]["pass"]:
        raise SystemExit("finite-difference derivative check failed")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
