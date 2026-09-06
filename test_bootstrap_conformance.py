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
        with self.assertRaisesRegex(BootstrapInputError, "explicitly 'iid'"):
            bootstrap_mean(record)

    def test_refuses_dependent_sampling(self):
        record = self.base_record()
        record["sampling"] = "time_series"
        with self.assertRaisesRegex(BootstrapInputError, "outside this conformance slice"):
            bootstrap_mean(record)

    def test_refuses_non_observation_resampling_unit(self):
        record = self.base_record()
        record["resampling_unit"] = "cluster"
        with self.assertRaisesRegex(BootstrapInputError, "resampling_unit"):
            bootstrap_mean(record)

    def test_refuses_unimplemented_interval(self):
        record = self.base_record()
        record["interval"] = "percentile"
        with self.assertRaisesRegex(BootstrapInputError, "basic_bootstrap"):
            bootstrap_mean(record)

    def test_refuses_large_exact_state_space(self):
        record = self.base_record()
        record["observed"] = list(range(7))
        with self.assertRaisesRegex(BootstrapInputError, "823543 resamples"):
            bootstrap_mean(record)


if __name__ == "__main__":
    unittest.main()
