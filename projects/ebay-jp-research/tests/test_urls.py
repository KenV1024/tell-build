import unittest

from ebay_jp_research.config import DEFAULT_CONFIG
from ebay_jp_research.urls import build_search_urls

TEMPLATES = DEFAULT_CONFIG["search_urls"]


class UrlTest(unittest.TestCase):
    def test_three_urls_generated_ac2(self):
        urls = build_search_urls("Nintendo Game Boy", TEMPLATES)
        self.assertEqual(set(urls.keys()), {"mercari", "yahoo_flea", "rakuma"})
        for u in urls.values():
            self.assertTrue(u.startswith("https://"))

    def test_keyword_is_url_encoded(self):
        urls = build_search_urls("Game Boy", TEMPLATES)
        # 空白は %20 にエンコードされ、生の空白が残らない
        for u in urls.values():
            self.assertNotIn(" ", u)
            self.assertIn("Game%20Boy", u)

    def test_domains(self):
        urls = build_search_urls("test", TEMPLATES)
        self.assertIn("jp.mercari.com", urls["mercari"])
        self.assertIn("paypayfleamarket.yahoo.co.jp", urls["yahoo_flea"])
        self.assertIn("fril.jp", urls["rakuma"])


if __name__ == "__main__":
    unittest.main()
