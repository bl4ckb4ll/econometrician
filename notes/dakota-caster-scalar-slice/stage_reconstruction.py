#!/usr/bin/env python3
"""Evidence-led Dakota caster reconstruction anchored to the checked PR #5 slice."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from scalar_slice import (analytic_jacobian_magnitude, derivative_check,
                          signed_caster_coefficient)

HERE = Path(__file__).resolve().parent


def load_evidence(path: Path = HERE / "reconstruction_evidence.json") -> dict:
    return json.loads(path.read_text())


def load_g5_reset_sweep(path: Path = HERE / "g5_reset_sweep.csv") -> dict:
    rows = list(csv.DictReader(path.read_text().splitlines()))
    if len(rows) != 14:
        raise ValueError("G5 reset sweep must contain seven rows per side")
    stage = {
        "id": "G5",
        "date": "2026-09-16",
        "kind": "reset_state_sweep",
        "status": "same-session raw sweep; nominal angles only",
    }
    for side in ("driver", "passenger"):
        observations = []
        for row in rows:
            if row["side"] != side:
                continue
            low = float(row["camber_min_deg"])
            high = float(row["camber_max_deg"])
            observations.append({
                "evidence_id": row["evidence_id"],
                "steering": row["steering_position"],
                "turns": float(row["turns"]),
                "direction": row["direction"],
                "camber_deg": low if low == high else [low, high],
                "generation": row["generation"],
                "adjustment_state": row["adjustment_state"],
                "sweep_id": row["sweep_id"],
                "approach_direction": row["approach_direction"],
                "provenance": row["provenance"],
                "uncertainty": row["uncertainty"],
            })
        by_position = {row["steering"]: row for row in observations}
        stage[side] = {
            "observations": observations,
            "accepted_symmetric_pairs": [
                {"id": "half_turn",
                 "right": by_position["0.5 turn right"]["evidence_id"],
                 "left": by_position["0.5 turn left"]["evidence_id"]},
                {"id": "full_turn",
                 "right": by_position["1 turn right"]["evidence_id"],
                 "left": by_position["1 turn left"]["evidence_id"]},
                {"id": "lock",
                 "right": by_position["maximum right"]["evidence_id"],
                 "left": by_position["maximum left"]["evidence_id"]},
            ],
        }
    return stage


def nominal_angle_deg(turns: float, ratio: float) -> float:
    return 360.0 * turns / ratio


def observation_map(stage: dict, side: str) -> dict:
    return {row["evidence_id"]: row for row in stage[side]["observations"]}


def _value_endpoints(value):
    if isinstance(value, list):
        return [float(min(value)), float(max(value))]
    return [float(value)]


def pair_results(stage: dict, side: str, steering_model: dict) -> list[dict]:
    rows = observation_map(stage, side)
    ratio = float(steering_model["overall_ratio"])
    output = []
    for pair in stage[side]["accepted_symmetric_pairs"]:
        rr = rows[pair["right"]]
        ll = rows[pair["left"]]
        tr = nominal_angle_deg(float(rr["turns"]), ratio)
        tl = -nominal_angle_deg(float(ll["turns"]), ratio)
        values = []
        for gr in _value_endpoints(rr["camber_deg"]):
            for gl in _value_endpoints(ll["camber_deg"]):
                signed = signed_caster_coefficient(tr, tl, gr, gl)
                x = [tr, tl, gr, gl]
                jacobian = analytic_jacobian_magnitude(*x)
                values.append({
                    "gamma_right_deg": gr,
                    "gamma_left_deg": gl,
                    "signed_odd_coefficient_deg": signed,
                    "magnitude_deg": abs(signed),
                    "jacobian_magnitude": jacobian,
                    "derivative_check": derivative_check(x, jacobian),
                })
        mags = sorted(v["magnitude_deg"] for v in values)
        signed_values = sorted(v["signed_odd_coefficient_deg"] for v in values)
        output.append({
            "pair_id": pair["id"],
            "right_evidence_id": rr["evidence_id"],
            "left_evidence_id": ll["evidence_id"],
            "theta_right_nominal_deg": tr,
            "theta_left_nominal_deg": tl,
            "actual_road_wheel_angles_status": steering_model["actual_road_wheel_angles_status"],
            "signed_odd_coefficient_interval_deg": [signed_values[0], signed_values[-1]],
            "magnitude_interval_deg": [mags[0], mags[-1]],
            "endpoint_linearizations": values,
        })
    return output


def combined_symmetric_odd_interval(pair_rows: list[dict]) -> list[float]:
    """Least-squares odd coefficient from raw pair differences.

    This is only a deterministic diagnostic under the nominal-angle sine model.
    Ranged camber inputs are propagated by enumerating their endpoints.
    """
    choices = [[]]
    for p in pair_rows:
        variants = p["endpoint_linearizations"]
        choices = [prefix + [v] for prefix in choices for v in variants]

    estimates = []
    for choice in choices:
        numerator = 0.0
        denominator = 0.0
        for p, v in zip(pair_rows, choice):
            tr = math.radians(p["theta_right_nominal_deg"])
            tl = math.radians(p["theta_left_nominal_deg"])
            x = math.sin(tr) - math.sin(tl)
            dgamma = v["gamma_right_deg"] - v["gamma_left_deg"]
            numerator += x * dgamma
            denominator += x * x
        estimates.append(numerator / denominator)
    return [min(estimates), max(estimates)]


def build_result(evidence: dict, g5_stage: dict | None = None) -> dict:
    stages = {s["id"]: s for s in evidence["stages"]}
    steering = evidence["steering_model"]
    g5_stage = load_g5_reset_sweep() if g5_stage is None else g5_stage

    g2_pairs = pair_results(stages["G2"], "passenger", steering)
    anchor_value = g2_pairs[0]["magnitude_interval_deg"][0]
    expected_anchor = float(evidence["anchor"]["caster_magnitude_deg"])
    if not math.isclose(anchor_value, expected_anchor, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("full reconstruction does not reproduce checked PR #5 anchor")

    g2_combined = combined_symmetric_odd_interval(g2_pairs)
    g2_pair_mags = [p["magnitude_interval_deg"][0] for p in g2_pairs]

    g4_pairs = pair_results(stages["G4"], "driver", steering)
    g4_combined = combined_symmetric_odd_interval(g4_pairs)

    g5_driver_pairs = pair_results(g5_stage, "driver", steering)
    g5_passenger_pairs = pair_results(g5_stage, "passenger", steering)
    g5_driver_combined = combined_symmetric_odd_interval(g5_driver_pairs)
    g5_passenger_combined = combined_symmetric_odd_interval(g5_passenger_pairs)

    uncertainty = evidence["uncertainty_policy"]
    return {
        "reconstruction_id": evidence["reconstruction_id"],
        "status": "stagewise_reconstruction_checked_from_verified_anchor",
        "anchor": {
            **evidence["anchor"],
            "reproduced_caster_magnitude_deg": anchor_value,
            "exact_agreement": True,
        },
        "preserved_evidence_boundary": {
            "G0_measurements_retained": len(stages["G0"].get("measurements", [])),
            "G1_driver_rows_retained_but_rejected": len(stages["G1"].get("driver_transcription", [])),
            "G1_passenger_rows_retained_but_rejected": len(stages["G1"].get("passenger_transcription", [])),
            "secondary_reconstruction_records_status": evidence["secondary_reconstruction_records"]["status"],
            "G4_passenger_rows_retained_but_provisional": len(stages["G4"]["passenger"].get("observations", [])),
            "G5_reset_rows_retained": (
                len(g5_stage["driver"]["observations"])
                + len(g5_stage["passenger"]["observations"])
            ),
            "unmapped_4_75_correction_status": stages["G2"]["passenger"]["unmapped_correction"]["status"],
            "discrepancy_rules": evidence["discrepancy_rules"],
        },
        "model_boundary": {
            "pair_formula": "B = (gamma_R - gamma_L) / (sin(theta_R) - sin(theta_L))",
            "reported_pair_quantity": "|B|, the caster-magnitude proxy used by the checked scalar slice",
            "physical_caster_status": "conditional; actual road-wheel angles and nuisance state are unresolved",
            "steering_model": steering,
            "no_grand_average_across_generations": True,
            "legacy_8_degree_driver_results": "rejected as physical evidence and excluded from every estimate",
            "sep17_weighted_result_status": "rejected: 2:1 weighting and practical error bars were not derived from a covariance model",
        },
        "G2_passenger": {
            "status": "strongest preserved internally cross-checked generation",
            "pair_results": g2_pairs,
            "nominal_pair_magnitude_range_deg": [min(g2_pair_mags), max(g2_pair_mags)],
            "nominal_pair_magnitude_spread_deg": max(g2_pair_mags) - min(g2_pair_mags),
            "nominal_combined_odd_coefficient_interval_deg": g2_combined,
            "nominal_combined_magnitude_interval_deg": sorted(abs(v) for v in g2_combined),
            "signed_physical_caster_status": stages["G2"]["passenger"]["signed_physical_caster_status"],
        },
        "G2_driver": {
            "status": stages["G2"]["driver"]["status"],
            "caster_result": None,
        },
        "G3": {
            "status": stages["G3"]["status"],
            "caster_result": None,
        },
        "I1": {
            "status": stages["I1"]["status"],
            "observations": stages["I1"]["observations"],
            "uncertainty_effect": "setup/path/hysteresis state cannot be treated as independent point noise",
        },
        "G4_driver": {
            "status": "conditional nominal-angle reconstruction from corrected same-session table",
            "pair_results": g4_pairs,
            "nominal_combined_odd_coefficient_interval_deg": g4_combined,
            "nominal_combined_magnitude_interval_deg": sorted(abs(v) for v in g4_combined),
            "interpretation": "different physical/measurement generation; do not compare to G2 as though only caster changed",
        },
        "G4_passenger": {
            "status": stages["G4"]["passenger"]["status"],
            "caster_result": None,
        },
        "I2": {
            "status": stages["I2"]["status"],
            "description": stages["I2"]["description"],
            "immediate_post_reverse_caster_status": "no full sweep recovered immediately after I2",
            "later_measurement_status": "superseded by separate G5 reset-state sweep on Sep16",
        },
        "G5_reset_sweep": {
            "status": g5_stage["status"],
            "date": g5_stage["date"],
            "adjustment_state": "passenger front returned; only rear driver remained displaced",
            "reference_state": {
                "restored_hood_endpoint_heights_in": [47.5, 47.5],
                "deliberate_reference_test_endpoint_heights_in": [46.0, 49.0],
                "rule": "body/reference state is not a constant correction carried across steering positions",
            },
            "driver": {
                "pair_results": g5_driver_pairs,
                "nominal_combined_odd_coefficient_interval_deg": g5_driver_combined,
                "nominal_combined_magnitude_interval_deg": sorted(abs(v) for v in g5_driver_combined),
            },
            "passenger": {
                "pair_results": g5_passenger_pairs,
                "nominal_combined_odd_coefficient_interval_deg": g5_passenger_combined,
                "nominal_combined_magnitude_interval_deg": sorted(abs(v) for v in g5_passenger_combined),
            },
            "interpretation": "pair disagreement is evidence against collapsing the sweep to one nominal-angle caster/error bar; actual road-wheel angles remain unmeasured",
        },
        "uncertainty": {
            **uncertainty,
            "pair_jacobian_columns": [
                "theta_right_deg", "theta_left_deg",
                "gamma_right_deg", "gamma_left_deg"
            ],
            "steering_zero_note": "for a nominal equal/opposite pair, common additive steering-zero error cancels to first order; equal/opposite magnitude error does not",
            "gauge_zero_note": "common additive camber zero cancels in pair differences; calibration/placement and path effects do not thereby disappear",
            "stage_note": "setup and hysteresis are shared/stateful nuisance terms, not automatically independent reading errors",
        },
        "intervention_boundary": {
            "sequence_preserved": ["I0", "G2", "G3", "I1", "G4", "I2", "G5"],
            "current_CW_CCW_viewpoint": "rear looking forward",
            "retroactive_conversion_of_historical_rotation_labels": False,
            "paper_cam_effect_coefficients_used_for_adjustment_inference": False,
        },
        "finish_condition": {
            "checked_anchor_reproduced": True,
            "three_G2_passenger_pair_rows_checked": True,
            "G4_driver_rows_kept_in_own_generation": True,
            "G4_passenger_provisional_not_promoted": True,
            "legacy_8_degree_driver_result_rejected": True,
            "actual_road_wheel_angles_not_invented": True,
            "single_covariance_not_invented": True,
            "unresolved_epsilons_retained": True,
            "immediate_post_I2_full_sweep_not_claimed": True,
            "later_G5_reset_sweep_preserved": True,
        },
    }


def main() -> None:
    result = build_result(load_evidence())
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
