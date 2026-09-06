import unittest

from check_wasserman_bootstrap import check_answers, check_case


class WassermanOracleTests(unittest.TestCase):
    def test_basic_interval_accepts_close_numeric_answer(self):
        case = {
            "id": "basic",
            "expect": {"method": "basic_bootstrap", "interval": [9.7, 10.2]},
            "tolerance": {"interval": 1e-6},
        }
        self.assertEqual(
            check_case(
                case,
                {"method": "basic_bootstrap", "interval": [9.7000004, 10.1999997]},
            ),
            [],
        )

    def test_basic_interval_rejects_endpoint_formula_error(self):
        case = {
            "id": "basic",
            "expect": {"interval": [9.7, 10.2]},
            "tolerance": {"interval": 1e-9},
        }
        errors = check_case(case, {"interval": [9.8, 10.3]})
        self.assertTrue(errors)

    def test_boolean_claim_is_not_treated_as_number(self):
        case = {
            "id": "validity",
            "expect": {"guaranteed_valid_coverage": False},
        }
        self.assertTrue(check_case(case, {"guaranteed_valid_coverage": 0}))

    def test_full_sweep_requires_every_case_once(self):
        cases = [
            {"id": "a", "expect": {"x": 1}},
            {"id": "b", "expect": {"x": 2}},
        ]
        passes, failures = check_answers(
            cases, [{"id": "a", "answer": {"x": 1}}]
        )
        self.assertEqual(passes, ["a"])
        self.assertIn("b: missing submission", failures)


if __name__ == "__main__":
    unittest.main()
