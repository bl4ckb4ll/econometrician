#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import scalar_slice as s


class ScalarSliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = s.load_evidence(HERE / "evidence.json")
        nominal = cls.evidence["steering_angle_input"]
        cls.x = [nominal["right_nominal_deg"], nominal["left_nominal_deg"], 0.5, 2.5]
        cls.result = s.build_result(cls.evidence, cls.x[0], cls.x[1])

    def test_raw_observation_identity_and_order(self) -> None:
        rows = self.evidence["raw_observations"]
        self.assertEqual(
            [(r["evidence_id"], r["steering_position"], r["raw_value_deg"]) for r in rows],
            [("E-026", "0.5 turn right", 0.5), ("E-028", "0.5 turn left", 2.5)],
        )

    def test_side_generation_and_sign_metadata(self) -> None:
        self.assertEqual(self.evidence["side"], "passenger")
        self.assertEqual(self.evidence["generation"], "G2")
        self.assertIn("right positive", self.evidence["metadata"]["steering_sign"])
        self.assertIn("top of tire outward", self.evidence["metadata"]["camber_sign"])
        self.assertFalse(self.evidence["metadata"]["current_viewpoint_is_retroactive_historical_claim"])

    def test_cam_state_gap_is_preserved_not_invented(self) -> None:
        self.assertIn("not recovered", self.evidence["metadata"]["eccentric_cam_position_for_selected_pair"])

    def test_nominal_angle_conversion(self) -> None:
        expected = 180.0 / 17.4
        self.assertAlmostEqual(self.x[0], expected, places=12)
        self.assertAlmostEqual(self.x[1], -expected, places=12)

    def test_symmetric_multiplier(self) -> None:
        multiplier = 1.0 / (2.0 * math.sin(math.radians(self.x[0])))
        self.assertAlmostEqual(multiplier, 2.784399371553343, places=12)

    def test_signed_and_magnitude_arithmetic(self) -> None:
        self.assertAlmostEqual(s.signed_caster_coefficient(*self.x), -5.568798743106686, places=12)
        self.assertAlmostEqual(s.caster_magnitude(*self.x), 5.568798743106686, places=12)

    def test_sign_reversal_if_camber_endpoints_swapped(self) -> None:
        swapped = [self.x[0], self.x[1], self.x[3], self.x[2]]
        self.assertAlmostEqual(s.signed_caster_coefficient(*swapped), -s.signed_caster_coefficient(*self.x), places=12)
        self.assertAlmostEqual(s.caster_magnitude(*swapped), s.caster_magnitude(*self.x), places=12)

    def test_analytic_derivatives_match_centered_finite_difference(self) -> None:
        analytic = s.analytic_jacobian_magnitude(*self.x)
        check = s.derivative_check(self.x, analytic)
        self.assertTrue(check["pass"], check)
        self.assertLessEqual(max(check["absolute_error"]), check["tolerance"])

    def test_expected_jacobian(self) -> None:
        expected = [-0.2662274831764701, +0.2662274831764701,
                    -2.784399371553343, +2.784399371553343]
        for actual, target in zip(s.analytic_jacobian_magnitude(*self.x), expected):
            self.assertAlmostEqual(actual, target, places=11)

    def test_common_steering_zero_shift_cancels_first_order(self) -> None:
        j = s.analytic_jacobian_magnitude(*self.x)
        self.assertAlmostEqual(j[0] + j[1], 0.0, places=12)

    def test_equal_opposite_steering_magnitude_error_does_not_cancel(self) -> None:
        j = s.analytic_jacobian_magnitude(*self.x)
        self.assertAlmostEqual(j[0] - j[1], -0.5324549663529402, places=11)

    def test_common_camber_zero_shift_cancels_first_order(self) -> None:
        j = s.analytic_jacobian_magnitude(*self.x)
        self.assertAlmostEqual(j[2] + j[3], 0.0, places=12)

    def test_historical_magnitude_agreement_and_direction_discrepancy(self) -> None:
        comparison = self.result["historical_comparison"]
        self.assertTrue(comparison["recomputed_inside_reported_range"])
        self.assertEqual(comparison["magnitude_result"], "agreement")
        self.assertEqual(comparison["direction_label_result"], "discrepancy")
        self.assertIn("not accepted", comparison["signed_historical_comparison_status"])

    def test_printed_multiplier_rounding_discrepancy_is_small_and_explicit(self) -> None:
        comparison = self.result["historical_comparison"]
        self.assertAlmostEqual(comparison["result_using_printed_multiplier_deg"], 5.568, places=12)
        self.assertAlmostEqual(comparison["exact_minus_printed_multiplier_result_deg"],
                               0.0007987431066858186, places=12)

    def test_legacy_illustrative_sigmas_are_not_used_as_inputs(self) -> None:
        excluded = self.result["uncertainty_boundary"]["legacy_illustrative_sigmas_excluded"]
        self.assertEqual(excluded["legacy_sigma_gamma_deg"], 0.25)
        self.assertEqual(excluded["legacy_sigma_steering_wheel_deg"], 15.0)
        self.assertNotIn("sigma", json.dumps(self.result["calculation"], sort_keys=True))

    def test_symbolic_epsilons_survive_output(self) -> None:
        eps = self.result["linearization"]["unresolved_symbolic_epsilons"]
        self.assertIn("epsilon_setup_hysteresis", eps)
        self.assertIn("epsilon_gauge_calibration", eps)
        self.assertIn("epsilon_cam_state_model", eps)
        self.assertIn("epsilon^2 = 0", self.result["linearization"]["epsilon_rule"])

    def test_cli_output_is_byte_deterministic(self) -> None:
        cmd = [sys.executable, str(HERE / "scalar_slice.py")]
        self.assertEqual(subprocess.check_output(cmd, cwd=HERE),
                         subprocess.check_output(cmd, cwd=HERE))


if __name__ == "__main__":
    unittest.main(verbosity=2)
