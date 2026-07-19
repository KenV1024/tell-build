#!/usr/bin/env python3
"""geo_watch のユニットテスト（ネットワーク非依存）。

最低限、期間フィルタ(F1-2/AC-2)と差分検出(F2/AC-4)のロジックを検証する。
実行: py -m unittest test_geo_watch  （または py test_geo_watch.py）
"""
import unittest
from datetime import datetime, timezone

import geo_watch as gw


def dt(y, m, d):
    return datetime(y, m, d, tzinfo=timezone.utc)


class TestFilterByDays(unittest.TestCase):
    def setUp(self):
        self.now = dt(2026, 7, 18)
        self.entries = [
            {"title": "today", "published": dt(2026, 7, 18)},
            {"title": "3days", "published": dt(2026, 7, 15)},
            {"title": "10days", "published": dt(2026, 7, 8)},
            {"title": "40days", "published": dt(2026, 6, 8)},
            {"title": "nodate", "published": None},
        ]

    def test_days_1(self):
        kept = gw.filter_by_days(self.entries, 1, now=self.now)
        titles = {e["title"] for e in kept}
        # 1日以内は today のみ。日付不明は常に残す。
        self.assertEqual(titles, {"today", "nodate"})

    def test_days_7(self):
        kept = gw.filter_by_days(self.entries, 7, now=self.now)
        titles = {e["title"] for e in kept}
        self.assertEqual(titles, {"today", "3days", "nodate"})

    def test_days_30_vs_1_differs(self):
        few = gw.filter_by_days(self.entries, 1, now=self.now)
        many = gw.filter_by_days(self.entries, 30, now=self.now)
        # AC-2: 期間で件数が変わる
        self.assertGreater(len(many), len(few))

    def test_days_365_includes_all(self):
        kept = gw.filter_by_days(self.entries, 365, now=self.now)
        self.assertEqual(len(kept), 5)


class TestComputeNew(unittest.TestCase):
    def test_first_run_all_new(self):
        current = ["https://x.com/a", "https://x.com/b"]
        new, updated = gw.compute_new(current, [])
        self.assertEqual(new, current)
        self.assertEqual(set(updated), set(current))

    def test_second_run_no_new(self):
        current = ["https://x.com/a", "https://x.com/b"]
        _, seen = gw.compute_new(current, [])
        new2, _ = gw.compute_new(current, seen)
        self.assertEqual(new2, [])  # AC-4

    def test_incremental_new(self):
        seen = ["https://x.com/a"]
        current = ["https://x.com/a", "https://x.com/b"]
        new, updated = gw.compute_new(current, seen)
        self.assertEqual(new, ["https://x.com/b"])
        self.assertEqual(set(updated), {"https://x.com/a", "https://x.com/b"})


class TestParseDate(unittest.TestCase):
    def test_rfc822(self):
        d = gw.parse_date("Mon, 14 Jul 2026 10:00:00 +0000")
        self.assertEqual((d.year, d.month, d.day), (2026, 7, 14))

    def test_iso8601_z(self):
        d = gw.parse_date("2026-07-14T10:00:00Z")
        self.assertEqual((d.year, d.month, d.day), (2026, 7, 14))

    def test_invalid(self):
        self.assertIsNone(gw.parse_date("not a date"))
        self.assertIsNone(gw.parse_date(None))


class TestParseFeed(unittest.TestCase):
    RSS = """<?xml version="1.0"?>
    <rss version="2.0"><channel>
      <item><title>Hello</title><link>https://ex.com/1</link>
        <pubDate>Mon, 14 Jul 2026 10:00:00 +0000</pubDate>
        <description>&lt;p&gt;body text&lt;/p&gt;</description></item>
    </channel></rss>"""

    ATOM = """<?xml version="1.0"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry><title>Atom Post</title>
        <link rel="alternate" href="https://ex.com/atom1"/>
        <published>2026-07-14T10:00:00Z</published>
        <summary>atom summary</summary></entry>
    </feed>"""

    def test_rss(self):
        entries = gw.parse_feed(self.RSS)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["title"], "Hello")
        self.assertEqual(entries[0]["link"], "https://ex.com/1")
        self.assertIn("body text", entries[0]["summary"])

    def test_atom(self):
        entries = gw.parse_feed(self.ATOM)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["title"], "Atom Post")
        self.assertEqual(entries[0]["link"], "https://ex.com/atom1")

    def test_leading_whitespace(self):
        entries = gw.parse_feed("\r\n" + self.RSS)  # iPullRank型（先頭空白）
        self.assertEqual(len(entries), 1)

    def test_doctype_rejected(self):
        evil = '<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "b">]><rss><channel></channel></rss>'
        with self.assertRaises(ValueError):
            gw.parse_feed(evil)


class TestExtractLinks(unittest.TestCase):
    HTML = '''<html><body>
      <a href="/blog/post-1">p1</a>
      <a href="https://site.com/blog/post-2">p2</a>
      <a href="https://other.com/x">external</a>
      <a href="#top">anchor</a>
      <a href="mailto:a@b.com">mail</a>
      <a href="/blog/post-1#frag">dup</a>
    </body></html>'''

    def test_same_domain_absolute_dedup(self):
        links = gw.extract_links(self.HTML, "https://site.com/blog")
        self.assertIn("https://site.com/blog/post-1", links)
        self.assertIn("https://site.com/blog/post-2", links)
        self.assertNotIn("https://other.com/x", links)
        # アンカー・mailto除外、フラグメント正規化で重複しない
        self.assertEqual(links.count("https://site.com/blog/post-1"), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
