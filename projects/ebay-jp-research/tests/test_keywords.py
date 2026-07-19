import unittest

from ebay_jp_research.config import DEFAULT_CONFIG
from ebay_jp_research.keywords import extract_model_numbers, generate_keywords

STOP = DEFAULT_CONFIG["keyword"]["stopwords"]


class KeywordTest(unittest.TestCase):
    def test_removes_stopwords_ac3(self):
        # AC-3: Japan / Used 等の不要語を除去する
        result = generate_keywords(
            "Nintendo Game Boy Color Console Japan Used", STOP, 6
        )
        self.assertEqual(result, "Nintendo Game Boy Color Console")
        self.assertNotIn("Japan", result)
        self.assertNotIn("Used", result)

    def test_max_keywords(self):
        result = generate_keywords("aa bb cc dd ee ff gg hh", [], 3)
        self.assertEqual(result, "aa bb cc")

    def test_dedup_case_insensitive(self):
        result = generate_keywords("Sony sony SONY Walkman", [], 6)
        self.assertEqual(result, "Sony Walkman")

    def test_empty_title(self):
        self.assertEqual(generate_keywords("", STOP, 6), "")
        self.assertEqual(generate_keywords(None, STOP, 6), "")

    def test_model_number_kept(self):
        result = generate_keywords("Casio G-Shock DW-5600 Watch Japan", STOP, 6)
        self.assertIn("DW-5600", result)

    def test_extract_model_numbers(self):
        models = extract_model_numbers("Casio DW-5600 and WM-EX194 plain word")
        self.assertIn("DW-5600", models)
        self.assertIn("WM-EX194", models)
        self.assertNotIn("plain", models)


if __name__ == "__main__":
    unittest.main()
