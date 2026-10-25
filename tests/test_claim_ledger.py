import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers import load, run  # noqa: E402

cl = load("claim_ledger")

TODAY = date(2026, 10, 16)
FLOOR = date(2026, 9, 24)  # starting point (beta start)


def src(value, publisher, tier, day, url=None):
    return {"value": value, "publisher": publisher, "tier": tier, "date": day,
            "url": url or f"https://example.com/{publisher}/{day}/{value}"}


def claim(*sources, changed=None):
    c = {"topic": "test", "sources": list(sources)}
    if changed:
        c["changed"] = {"date": changed, "url": "https://example.com/patch", "note": "changed"}
    return c


def status(c):
    return cl.judge(c, FLOOR, TODAY)[0]


class ValueMatching(unittest.TestCase):
    def test_same_percent_written_differently(self):
        for v in ("8%", "8 %", "8 percent", "8 per cent", "8.0%", "8.00 pct", "8 Percent"):
            self.assertEqual(cl.norm(v), "8%", v)

    def test_trailing_zeros_only(self):
        self.assertEqual(cl.norm("10.50%"), "10.5%")
        self.assertEqual(cl.norm("1.05%"), "1.05%")
        self.assertEqual(cl.norm("100%"), "100%")

    def test_different_numbers_stay_different(self):
        self.assertNotEqual(cl.norm("8%"), cl.norm("9%"))
        self.assertNotEqual(cl.norm("8%"), cl.norm("80%"))

    def test_priority_order_ignores_spacing_and_case(self):
        self.assertEqual(cl.norm("Hit > Strength"), cl.norm("hit>strength"))
        self.assertNotEqual(cl.norm("Hit > Strength"), cl.norm("Strength > Hit"))

    def test_differently_written_values_verify_together(self):
        c = claim(src("8%", "Method", 2, "2026-10-06"), src("8 percent", "Icy Veins", 2, "2026-10-07"))
        self.assertEqual(status(c), "VERIFIED")


class Verified(unittest.TestCase):
    def test_one_current_blizzard_source(self):
        s, value, _ = cl.judge(claim(src("8%", "Blizzard", 1, "2026-10-01")), FLOOR, TODAY)
        self.assertEqual((s, value), ("VERIFIED", "8%"))

    def test_two_guide_sites_agree_ignoring_spacing_and_case(self):
        c = claim(src("8%", "Method", 2, "2026-10-06"), src("8 %", "Icy Veins", 2, "2026-10-07"))
        self.assertEqual(status(c), "VERIFIED")

    def test_old_blizzard_source_still_counts_if_topic_never_changed(self):
        # Tier 1 is not limited by the starting point.
        self.assertEqual(status(claim(src("8%", "Blizzard", 1, "2026-08-01"))), "VERIFIED")

    def test_blizzard_overrides_guide_site_and_names_dissent(self):
        c = claim(src("8%", "Blizzard", 1, "2026-10-01"), src("9%", "Method", 2, "2026-10-06"))
        s, value, note = cl.judge(c, FLOOR, TODAY)
        self.assertEqual((s, value), ("VERIFIED", "8%"))
        self.assertIn("Method", note)

    def test_undated_blizzard_plus_one_agreeing_site(self):
        c = claim(src("8%", "Blizzard", 1, "undated"), src("8%", "Method", 2, "2026-10-06"))
        self.assertEqual(status(c), "VERIFIED")


class Unconfirmed(unittest.TestCase):
    def test_single_guide_site(self):
        self.assertEqual(status(claim(src("8%", "Method", 2, "2026-10-06"))), "UNCONFIRMED")

    def test_two_pages_from_same_site_count_once(self):
        c = claim(src("8%", "Wowhead", 2, "2026-10-06", url="https://wowhead.com/a"),
                  src("8%", "wowhead", 2, "2026-10-07", url="https://wowhead.com/b"))
        self.assertEqual(status(c), "UNCONFIRMED")

    def test_untrusted_sources_only(self):
        c = claim(src("8%", "Reddit", 3, "2026-10-06"), src("8%", "YouTube", 3, "2026-10-07"))
        self.assertEqual(status(c), "UNCONFIRMED")

    def test_undated_blizzard_alone(self):
        self.assertEqual(status(claim(src("8%", "Blizzard", 1, "undated"))), "UNCONFIRMED")


class Conflict(unittest.TestCase):
    def test_guide_sites_disagree(self):
        c = claim(src("8%", "Method", 2, "2026-10-06"), src("9%", "Icy Veins", 2, "2026-10-07"))
        s, value, note = cl.judge(c, FLOOR, TODAY)
        self.assertEqual(s, "CONFLICT")
        self.assertIsNone(value)
        self.assertIn("8%", note)
        self.assertIn("9%", note)

    def test_blizzard_sources_disagree(self):
        c = claim(src("8%", "Blizzard", 1, "2026-10-01", url="https://blizzard.com/a"),
                  src("9%", "Blizzard", 1, "2026-10-10", url="https://blizzard.com/b"))
        self.assertEqual(status(c), "CONFLICT")


class Stale(unittest.TestCase):
    def test_guide_older_than_starting_point(self):
        c = claim(src("8%", "Method", 2, "2026-09-01"), src("8%", "Icy Veins", 2, "2026-09-02"))
        self.assertEqual(status(c), "STALE")

    def test_guides_older_than_topic_change(self):
        c = claim(src("8%", "Method", 2, "2026-10-01"), src("8%", "Icy Veins", 2, "2026-10-02"),
                  changed="2026-10-15")
        self.assertEqual(status(c), "STALE")

    def test_blizzard_older_than_topic_change(self):
        self.assertEqual(status(claim(src("8%", "Blizzard", 1, "2026-10-01"), changed="2026-10-15")), "STALE")

    def test_sources_on_change_day_are_current(self):
        c = claim(src("8%", "Method", 2, "2026-10-15"), src("8%", "Icy Veins", 2, "2026-10-16"),
                  changed="2026-10-15")
        self.assertEqual(status(c), "VERIFIED")

    def test_change_before_starting_point_does_not_loosen_cutoff(self):
        c = claim(src("8%", "Method", 2, "2026-09-01"), src("8%", "Icy Veins", 2, "2026-09-02"),
                  changed="2026-08-01")
        self.assertEqual(cl.claim_cutoff(c, FLOOR), FLOOR)
        self.assertEqual(status(c), "STALE")


class AfterLaunch(unittest.TestCase):
    """Launch is recorded per topic, not as a reset of the starting point."""
    AFTER_LAUNCH = date(2026, 11, 10)

    def test_beta_guides_still_count_when_launch_did_not_change_topic(self):
        c = claim(src("8%", "Method", 2, "2026-10-06"), src("8%", "Icy Veins", 2, "2026-10-07"))
        self.assertEqual(cl.judge(c, FLOOR, self.AFTER_LAUNCH)[0], "VERIFIED")

    def test_beta_guides_stale_when_launch_changed_topic(self):
        c = claim(src("8%", "Method", 2, "2026-10-06"), src("8%", "Icy Veins", 2, "2026-10-07"),
                  changed="2026-11-04")
        self.assertEqual(cl.judge(c, FLOOR, self.AFTER_LAUNCH)[0], "STALE")


class CommandLine(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.ledger = os.path.join(self.dir, "ledger.json")
        code, out = self.cli("init", "--today", "2026-10-16", "--cutoff", "2026-09-24", "--version", "beta")
        self.assertEqual(code, 0, out)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def cli(self, *args):
        return run("claim_ledger", "--ledger", self.ledger, *args)

    def add(self, url, publisher, tier, day, value="8%"):
        return self.cli("add", "--id", "hit", "--topic", "Hit cap", "--value", value,
                        "--url", url, "--publisher", publisher, "--tier", str(tier), "--date", day)

    def report(self):
        code, out = self.cli("report", "--json")
        self.assertEqual(code, 0, out)
        return {c["id"]: c for c in json.loads(out)["claims"]}

    def test_add_two_sites_then_report_verified(self):
        self.assertEqual(self.add("https://method.gg/a", "Method", 2, "2026-10-06")[0], 0)
        self.assertEqual(self.add("https://icy-veins.com/a", "Icy Veins", 2, "2026-10-07")[0], 0)
        self.assertEqual(self.report()["hit"]["status"], "VERIFIED")

    def test_changed_makes_older_sources_stale(self):
        self.add("https://method.gg/a", "Method", 2, "2026-10-06")
        self.add("https://icy-veins.com/a", "Icy Veins", 2, "2026-10-07")
        code, out = self.cli("changed", "--id", "hit", "--date", "2026-10-15",
                             "--url", "https://blizzard.com/patch", "--note", "hit changed")
        self.assertEqual(code, 0, out)
        row = self.report()["hit"]
        self.assertEqual(row["status"], "STALE")
        self.assertEqual(row["too_old_if_before"], "2026-10-15")

    def test_init_rejects_cutoff_after_today(self):
        code, _ = self.cli("init", "--today", "2026-10-16", "--cutoff", "2026-10-20", "--version", "x")
        self.assertNotEqual(code, 0)

    def test_rejects_future_source(self):
        code, out = self.add("https://method.gg/a", "Method", 2, "2026-11-01")
        self.assertNotEqual(code, 0)
        self.assertIn("after today", out)

    def test_rejects_undated_guide_site(self):
        code, _ = self.add("https://method.gg/a", "Method", 2, "undated")
        self.assertNotEqual(code, 0)

    def test_accepts_undated_blizzard(self):
        code, out = self.add("https://blizzard.com/a", "Blizzard", 1, "undated")
        self.assertEqual(code, 0, out)

    def test_rejects_bad_tier(self):
        code, _ = self.add("https://method.gg/a", "Method", 4, "2026-10-06")
        self.assertNotEqual(code, 0)

    def test_rejects_duplicate_url(self):
        self.add("https://method.gg/a", "Method", 2, "2026-10-06")
        code, out = self.add("https://method.gg/a", "Method", 2, "2026-10-07")
        self.assertNotEqual(code, 0)
        self.assertIn("already recorded", out)

    def test_report_without_init_fails(self):
        os.remove(self.ledger)
        code, out = self.cli("report")
        self.assertNotEqual(code, 0)
        self.assertIn("Run 'init' first", out)


if __name__ == "__main__":
    unittest.main()
