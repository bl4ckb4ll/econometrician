import math
import unittest

from econometrician import InputError, calculate


class ChiSquareTests(unittest.TestCase):
    def test_mendel_regression_case(self):
        answer = calculate({
            "test": "goodness_of_fit",
            "observed": [315, 101, 108, 32],
            "probabilities": [9 / 16, 3 / 16, 3 / 16, 1 / 16],
        })
        self.assertAlmostEqual(answer["statistic"], 0.470023, places=5)
        self.assertAlmostEqual(answer["p_value"], 0.9254259, places=6)
        self.assertEqual(answer["degrees_of_freedom"], 3)
        self.assertEqual(answer["decision"], "do_not_reject")

    def test_independence_known_table(self):
        answer = calculate({
            "test": "independence",
            "observed": [[90, 165], [84, 307]],
        })
        self.assertAlmostEqual(answer["statistic"], 14.95864, places=4)
        self.assertEqual(answer["degrees_of_freedom"], 1)
        self.assertLess(answer["p_value"], 0.01)
        self.assertEqual(answer["decision"], "reject")

    def test_same_proportions_are_independent(self):
        answer = calculate({"test": "independence", "observed": [[10, 20], [20, 40]]})
        self.assertEqual(answer["statistic"], 0)
        self.assertEqual(answer["p_value"], 1)

    def test_warns_on_sparse_expected_counts(self):
        answer = calculate({
            "test": "goodness_of_fit", "observed": [1, 9], "probabilities": [.5, .5]
        })
        self.assertFalse(answer["warnings"])
        answer = calculate({
            "test": "goodness_of_fit", "observed": [1, 7], "probabilities": [.5, .5]
        })
        self.assertTrue(answer["warnings"])

    def test_rejects_bad_probability_vector(self):
        with self.assertRaises(InputError):
            calculate({"test": "goodness_of_fit", "observed": [1, 2],
                       "probabilities": [.2, .2]})

    def test_rejects_empty_margin(self):
        with self.assertRaises(InputError):
            calculate({"test": "independence", "observed": [[0, 0], [2, 3]]})


if __name__ == "__main__":
    unittest.main()
