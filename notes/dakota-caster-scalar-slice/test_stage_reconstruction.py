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

import stage_reconstruction as r


class StageReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = r.load_evidence()
        cls.result = r.build_result(cls.evidence)

    def test_checked_anchor_is_exactly_reproduced(self):
        self.assertAlmostEqual(
            self.result["anchor"]["reproduced_caster_magnitude_deg"],
            5.568798743106686, places=12)

    def test_G2_passenger_three_symmetric_scales(self):
        pairs = self.result["G2_passenger"]["pair_results"]
        self.assertEqual([p["pair_id"] for p in pairs],
                         ["half_turn", "full_turn", "lock"])
        actual = [p["magnitude_interval_deg"][0] for p in pairs]
        expected = [
            5.568798743106686,
            5.660816193809301,
            5.523601342980962,
        ]
        for a, e in zip(actual, expected):
            self.assertAlmostEqual(a, e, places=12)
        self.assertLess(max(actual) - min(actual), 0.14)

    def test_G2_combined_odd_coefficient_is_near_anchor_not_eight(self):
        interval = self.result["G2_passenger"]["nominal_combined_odd_coefficient_interval_deg"]
        self.assertAlmostEqual(interval[0], -5.564714271422755, places=12)
        self.assertAlmostEqual(interval[1], -5.564714271422755, places=12)
        self.assertLess(abs(interval[0]), 6.0)

    def test_G2_driver_does_not_get_filled_from_old_transcription(self):
        self.assertIsNone(self.result["G2_driver"]["caster_result"])

    def test_G3_spot_measurements_do_not_become_caster(self):
        self.assertIsNone(self.result["G3"]["caster_result"])

    def test_G4_driver_pairwise_nominal_results(self):
        pairs = {p["pair_id"]: p for p in self.result["G4_driver"]["pair_results"]}
        self.assertAlmostEqual(pairs["half_turn"]["magnitude_interval_deg"][0],
                               3.480499214441678, places=12)
        self.assertAlmostEqual(pairs["lock"]["magnitude_interval_deg"][0],
                               2.5316506155329406, places=12)
        lo, hi = pairs["full_turn"]["magnitude_interval_deg"]
        self.assertAlmostEqual(lo, 3.5380101211308133, places=12)
        self.assertAlmostEqual(hi, 3.8918111332438943, places=12)

    def test_G4_combined_interval_is_conditional_and_below_old_eight(self):
        lo, hi = self.result["G4_driver"]["nominal_combined_magnitude_interval_deg"]
        self.assertAlmostEqual(lo, 2.8772184053589744, places=12)
        self.assertAlmostEqual(hi, 2.974912858857083, places=12)
        self.assertLess(hi, 4.0)

    def test_G4_passenger_remains_unclaimed(self):
        self.assertEqual(self.result["G4_passenger"]["status"],
                         "provisional_not_benchmark_truth")
        self.assertIsNone(self.result["G4_passenger"]["caster_result"])

    def test_post_reverse_state_remains_unmeasured(self):
        self.assertEqual(self.result["I2"]["current_post_reverse_caster_status"],
                         "unmeasured in preserved full sweep")

    def test_legacy_eight_degree_result_is_rejected(self):
        boundary = self.result["model_boundary"]
        self.assertIn("rejected", boundary["legacy_8_degree_driver_results"])
        serialized = json.dumps(self.result, sort_keys=True)
        self.assertNotIn('"caster_result": 8', serialized)

    def test_no_independence_or_rss_assumption(self):
        u = self.result["uncertainty"]
        self.assertFalse(u["automatic_independence_assumption"])
        self.assertFalse(u["rss_sigma_collapse"])

    def test_illustrative_sigmas_are_excluded(self):
        x = self.result["uncertainty"]["excluded_illustrative_sigmas"]
        self.assertEqual(x, {"camber_deg": 0.25, "steering_wheel_deg": 15.0})

    def test_symbolic_epsilons_survive(self):
        eps = self.result["uncertainty"]["unresolved_symbolic_epsilons"]
        self.assertEqual(eps, [
            "epsilon_setup_hysteresis",
            "epsilon_gauge_calibration",
            "epsilon_cam_state_model",
        ])
        self.assertIn("epsilon^2 = 0", self.result["uncertainty"]["epsilon_rule"])

    def test_each_pair_exposes_checked_jacobian_rows(self):
        for stage in ("G2_passenger", "G4_driver"):
            for pair in self.result[stage]["pair_results"]:
                for endpoint in pair["endpoint_linearizations"]:
                    self.assertEqual(len(endpoint["jacobian_magnitude"]), 4)
                    self.assertTrue(all(math.isfinite(x)
                                        for x in endpoint["jacobian_magnitude"]))
                    self.assertTrue(endpoint["derivative_check"]["pass"])

    def test_anchor_common_zero_modes_cancel_first_order(self):
        pair = self.result["G2_passenger"]["pair_results"][0]
        j = pair["endpoint_linearizations"][0]["jacobian_magnitude"]
        self.assertAlmostEqual(j[0] + j[1], 0.0, places=12)
        self.assertAlmostEqual(j[2] + j[3], 0.0, places=12)
        self.assertNotAlmostEqual(j[0] - j[1], 0.0, places=8)

    def test_generations_are_not_grand_averaged(self):
        self.assertTrue(self.result["model_boundary"]["no_grand_average_across_generations"])
        self.assertNotIn("overall_caster", self.result)

    def test_full_preserved_rows_are_carried_without_promotion(self):
        b = self.result["preserved_evidence_boundary"]
        self.assertEqual(b["G0_measurements_retained"], 6)
        self.assertEqual(b["G1_driver_rows_retained_but_rejected"], 7)
        self.assertEqual(b["G1_passenger_rows_retained_but_rejected"], 7)
        self.assertEqual(b["G4_passenger_rows_retained_but_provisional"], 7)
        self.assertIn("not_used", b["secondary_reconstruction_records_status"])
        self.assertIn("not silently substituted", b["unmapped_4_75_correction_status"])

    def test_cli_output_is_byte_deterministic(self):
        cmd = [sys.executable, str(HERE / "stage_reconstruction.py")]
        self.assertEqual(subprocess.check_output(cmd, cwd=HERE),
                         subprocess.check_output(cmd, cwd=HERE))


if __name__ == "__main__":
    unittest.main(verbosity=2)
