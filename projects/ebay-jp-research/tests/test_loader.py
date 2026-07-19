import os
import unittest

from ebay_jp_research.config import DEFAULT_CONFIG
from ebay_jp_research.loader import is_japan_seller, load_sold_csv, parse_money

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "samples")


class ParseMoneyTest(unittest.TestCase):
    def test_us_dollar_string(self):
        self.assertEqual(parse_money("US $85.00"), 85.0)

    def test_comma(self):
        self.assertEqual(parse_money("1,200"), 1200.0)

    def test_plain_number(self):
        self.assertEqual(parse_money(70), 70.0)

    def test_empty(self):
        self.assertIsNone(parse_money(""))
        self.assertIsNone(parse_money(None))


class JapanSellerTest(unittest.TestCase):
    values = DEFAULT_CONFIG["japan_filter"]["seller_location_values"]

    def test_japan(self):
        self.assertTrue(is_japan_seller("Japan", self.values))
        self.assertTrue(is_japan_seller("日本", self.values))
        self.assertTrue(is_japan_seller("Tokyo, Japan", self.values))

    def test_not_japan(self):
        self.assertFalse(is_japan_seller("United States", self.values))
        self.assertFalse(is_japan_seller("Germany", self.values))
        self.assertFalse(is_japan_seller("", self.values))


class LoadCsvTest(unittest.TestCase):
    def test_filters_to_japan_only_ac1(self):
        # AC-1: 10件中 日本セラー6件のみが処理対象
        path = os.path.join(SAMPLE_DIR, "sold_sample.csv")
        rows, stats = load_sold_csv(path, DEFAULT_CONFIG)
        self.assertEqual(stats["total"], 10)
        self.assertEqual(stats["japan"], 6)
        self.assertEqual(len(rows), 6)
        for r in rows:
            self.assertIn("japan", r["seller_location"].lower())

    def test_reads_estimated_cost_ac4(self):
        path = os.path.join(SAMPLE_DIR, "sold_with_cost_sample.csv")
        rows, _ = load_sold_csv(path, DEFAULT_CONFIG)
        self.assertTrue(all(r["estimated_cost_jpy"] is not None for r in rows))


if __name__ == "__main__":
    unittest.main()
