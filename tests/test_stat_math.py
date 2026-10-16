import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers import load, run  # noqa: E402

sm = load("stat_math")


class RatingMath(unittest.TestCase):
    def test_rating_to_percent(self):
        self.assertAlmostEqual(sm.rating_to_percent(70, 10), 7.0)

    def test_rating_to_percent_rejects_zero_divisor(self):
        with self.assertRaises(SystemExit):
            sm.rating_to_percent(70, 0)

    def test_rating_needed_when_short(self):
        missing, rating = sm.rating_needed(8, 3, 10)
        self.assertAlmostEqual(missing, 5.0)
        self.assertAlmostEqual(rating, 50.0)

    def test_rating_needed_when_already_capped(self):
        self.assertEqual(sm.rating_needed(8, 9, 10), (0.0, 0.0))

    def test_negative_input_rejected(self):
        with self.assertRaises(SystemExit):
            sm.positive(-1, "rating")


class CritCap(unittest.TestCase):
    def test_crit_cap_subtracts_other_results(self):
        cap, used = sm.crit_cap(0, 6.5, 0, 0, 24, 0)
        self.assertAlmostEqual(used, 30.5)
        self.assertAlmostEqual(cap, 69.5)

    def test_crit_cap_never_negative(self):
        cap, _ = sm.crit_cap(50, 30, 30, 0, 0, 0)
        self.assertEqual(cap, 0.0)


class ItemCompare(unittest.TestCase):
    def test_parse_pairs_normalizes_names(self):
        self.assertEqual(sm.parse_pairs(" Strength = 2.5,crit_rating=1", "w"),
                         {"strength": 2.5, "crit_rating": 1.0})

    def test_parse_pairs_rejects_bad_format(self):
        with self.assertRaises(SystemExit):
            sm.parse_pairs("strength:2", "w")
        with self.assertRaises(SystemExit):
            sm.parse_pairs("strength=lots", "w")

    def test_score(self):
        weights = {"strength": 2.2, "crit_rating": 1.1}
        self.assertAlmostEqual(sm.score({"strength": 20, "crit_rating": 14}, weights), 59.4)

    def test_score_refuses_unweighted_stat(self):
        with self.assertRaises(SystemExit):
            sm.score({"stamina": 10}, {"strength": 2.2})


class Formatting(unittest.TestCase):
    def test_fmt_trims_zeros(self):
        self.assertEqual(sm.fmt(7.0), "7")
        self.assertEqual(sm.fmt(69.5), "69.5")
        self.assertEqual(sm.fmt(18.518518), "18.52")


class CommandLine(unittest.TestCase):
    def test_rating_to_percent_cli(self):
        code, out = run("stat_math", "rating-to-percent", "--rating", "70", "--per-percent", "10")
        self.assertEqual(code, 0)
        self.assertIn("70 rating = 7%", out)

    def test_rating_needed_cli_capped(self):
        code, out = run("stat_math", "rating-needed", "--target", "8", "--have", "9", "--per-percent", "10")
        self.assertEqual(code, 0)
        self.assertIn("No more needed", out)

    def test_crit_cap_cli_reports_waste(self):
        code, out = run("stat_math", "crit-cap", "--dodge", "6.5", "--glancing", "24", "--crit", "75")
        self.assertEqual(code, 0)
        self.assertIn("Crit cap on auto attacks: 69.5%", out)
        self.assertIn("5.5% is wasted", out)

    def test_compare_items_cli(self):
        code, out = run("stat_math", "compare-items",
                        "--weights", "strength=2.2,crit_rating=1.1",
                        "--a", "strength=20,crit_rating=14",
                        "--b", "strength=32")
        self.assertEqual(code, 0)
        self.assertIn("Item B is ahead by 11 points", out)

    def test_compare_items_cli_unknown_stat_fails(self):
        code, out = run("stat_math", "compare-items",
                        "--weights", "strength=2.2", "--a", "agility=10", "--b", "strength=5")
        self.assertNotEqual(code, 0)
        self.assertIn("no verified weight for: agility", out)


if __name__ == "__main__":
    unittest.main()
