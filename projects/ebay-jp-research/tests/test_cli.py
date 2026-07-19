import copy
import csv
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from ebay_jp_research.cli import main
from ebay_jp_research.config import DEFAULT_CONFIG

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "samples")
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")


def _write_config(dirpath, overrides=None):
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    if overrides:
        for section, values in overrides.items():
            cfg[section].update(values)
    path = os.path.join(dirpath, "config.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f)
    return path


class CliRunTest(unittest.TestCase):
    def test_run_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "out.csv")
            rc = main([
                "run",
                "-i", os.path.join(SAMPLE_DIR, "sold_with_cost_sample.csv"),
                "-o", out,
                "-c", CONFIG_PATH,
            ])
            self.assertEqual(rc, 0)
            with open(out, "r", encoding="utf-8-sig", newline="") as f:
                rows = list(csv.DictReader(f))
            # 日本セラー6件のみ（AC-1）
            self.assertEqual(len(rows), 6)
            # 3本のURLが揃う（AC-2）
            for r in rows:
                self.assertTrue(r["mercari_url"].startswith("https://"))
                self.assertTrue(r["yahoo_flea_url"].startswith("https://"))
                self.assertTrue(r["rakuma_url"].startswith("https://"))
            # 利益率降順（AC-6）
            rates = [float(r["profit_rate"]) for r in rows if r["profit_rate"] != ""]
            self.assertEqual(rates, sorted(rates, reverse=True))
            # 候補が少なくとも1件（AC-6）
            self.assertTrue(any(r["is_candidate"] == "yes" for r in rows))

    def test_run_missing_input(self):
        with tempfile.TemporaryDirectory() as d:
            rc = main(["run", "-i", os.path.join(d, "nope.csv"),
                       "-o", os.path.join(d, "o.csv"), "-c", CONFIG_PATH])
            self.assertEqual(rc, 2)

    def test_run_without_config_uses_defaults_ac9(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "out.csv")
            rc = main([
                "run",
                "-i", os.path.join(SAMPLE_DIR, "sold_with_cost_sample.csv"),
                "-o", out,
                "-c", os.path.join(d, "no_config.json"),
            ])
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.exists(out))


class CliAutoFetchTest(unittest.TestCase):
    def _run_auto_fetch(self, overrides):
        with tempfile.TemporaryDirectory() as d:
            cfg = _write_config(d, {"auto_fetch": overrides})
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["auto-fetch", "-c", cfg])
            return rc, buf.getvalue()

    def test_both_false_disabled_ac7(self):
        rc, out = self._run_auto_fetch({"enabled": False, "risk_acknowledged": False})
        self.assertEqual(rc, 0)
        self.assertIn("既定でOFF", out)

    def test_one_flag_only_does_not_run_ac7(self):
        rc, out = self._run_auto_fetch({"enabled": True, "risk_acknowledged": False})
        self.assertEqual(rc, 0)
        self.assertIn("両方", out)

        rc2, out2 = self._run_auto_fetch({"enabled": False, "risk_acknowledged": True})
        self.assertEqual(rc2, 0)
        self.assertIn("両方", out2)

    def test_both_true_phase3_safe_exit_ac7(self):
        rc, out = self._run_auto_fetch({"enabled": True, "risk_acknowledged": True})
        self.assertEqual(rc, 0)
        self.assertIn("フェーズ3", out)


if __name__ == "__main__":
    unittest.main()
