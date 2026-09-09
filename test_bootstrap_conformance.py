import math
import unittest

from bootstrap_conformance import BootstrapInputError, bootstrap_mean


class BootstrapConformanceTests(unittest.TestCase):
    def base_record(self):
        return {
            "observed": [1, 2, 3, 4],
            "sampling": "iid",
            "resampling_unit": "observation",
            "estimator": "mean",
            "interval": "basic_bootstrap",
            "mode": "exact",
            "alpha": 0.05,
        }

    def assert_refusal(self, record, code, text):
        with self.assertRaisesRegex(BootstrapInputError, text) as caught:
            bootstrap_mean(record)
        self.assertEqual(caught.exception.code, code)

    def test_exact_small_sample_numeric_oracle(self):
        answer = bootstrap_mean(self.base_record())
        self.assertEqual(answer["estimate"], 2.5)
        self.assertAlmostEqual(answer["standard_error"], math.sqrt(5) / 4, places=14)
        self.assertEqual(answer["bootstrap_quantiles"], [1.5, 3.5])
        self.assertEqual(answer["interval"], [1.5, 3.5])
        self.assertEqual(answer["resampling"]["resamples"], 256)
        self.assertIs(answer["resampling"]["replacement"], True)
        self.assertIs(answer["monte_carlo_error"], False)
        self.assertIs(answer["guaranteed_valid_coverage"], False)

    def test_negative_observations_are_valid_for_a_mean(self):
        record = self.base_record()
        record["observed"] = [-1, 1]
        answer = bootstrap_mean(record)
        self.assertEqual(answer["estimate"], 0)
        self.assertAlmostEqual(answer["standard_error"], math.sqrt(0.5), places=14)

    def test_refuses_unstated_iid_assumption(self):
        record = self.base_record()
        del record["sampling"]
        self.assert_refusal(record, "iid_not_established", "explicitly 'iid'")

    def test_refuses_dependent_sampling(self):
        record = self.base_record()
        record["sampling"] = "time_series"
        self.assert_refusal(record, "unsupported_dependence", "outside this conformance slice")

    def test_refuses_non_observation_resampling_unit(self):
        record = self.base_record()
        record["resampling_unit"] = "cluster"
        self.assert_refusal(record, "unsupported_resampling_unit", "observation-level")

    def test_refuses_unimplemented_interval(self):
        record = self.base_record()
        record["interval"] = "percentile"
        self.assert_refusal(record, "unsupported_interval", "basic_bootstrap")

    def test_refuses_large_exact_state_space(self):
        record = self.base_record()
        record["observed"] = list(range(7))
        self.assert_refusal(record, "exact_state_space_limit", "823543 resamples")


if __name__ == "__main__":
    unittest.main()
