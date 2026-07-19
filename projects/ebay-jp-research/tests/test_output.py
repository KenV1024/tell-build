import csv
import os
import tempfile
import unittest

from ebay_jp_research.output import FIELDNAMES, sort_rows, write_output_csv


class SortTest(unittest.TestCase):
    def test_sorted_by_profit_rate_desc_ac6(self):
        rows = [
            {"title": "a", "profit_rate": 0.10},
            {"title": "b", "profit_rate": 0.48},
            {"title": "c", "profit_rate": None},
            {"title": "d", "profit_rate": 0.30},
        ]
        ordered = sort_rows(rows)
        self.assertEqual([r["title"] for r in ordered], ["b", "d", "a", "c"])


class WriteCsvTest(unittest.TestCase):
    def test_bom_and_columns_ac8(self):
        rows = [{
            "title": "テスト商品", "seller_location": "Japan", "sold_date": "2026-06-30",
            "currency": "USD", "sold_price": 85.0, "sold_price_jpy": 13175.0,
            "estimated_cost_jpy": 6000, "keywords": "Nintendo Game Boy",
            "mercari_url": "https://jp.mercari.com/search?keyword=x",
            "yahoo_flea_url": "https://paypayfleamarket.yahoo.co.jp/search/x",
            "rakuma_url": "https://fril.jp/search/x",
            "ebay_fee_jpy": 1712.75, "payment_fee_jpy": 395.25,
            "intl_shipping_jpy": 2000, "profit_jpy": 3067.0,
            "profit_rate": 0.2328, "is_candidate": True,
        }]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "out.csv")
            write_output_csv(path, rows)
            # 先頭に UTF-8 BOM があること（Excel文字化け防止）
            with open(path, "rb") as f:
                head = f.read(3)
            self.assertEqual(head, b"\xef\xbb\xbf")
            # 必須列がすべて揃うこと
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                self.assertEqual(reader.fieldnames, FIELDNAMES)
                out_rows = list(reader)
            self.assertEqual(out_rows[0]["title"], "テスト商品")
            self.assertEqual(out_rows[0]["is_candidate"], "yes")


if __name__ == "__main__":
    unittest.main()
