import copy
import unittest

from ebay_jp_research.config import DEFAULT_CONFIG
from ebay_jp_research.profit import compute_profit, to_jpy


class ToJpyTest(unittest.TestCase):
    rates = DEFAULT_CONFIG["exchange"]["rates"]

    def test_usd(self):
        value, warn = to_jpy(10, "USD", self.rates)
        self.assertEqual(value, 1550.0)
        self.assertIsNone(warn)

    def test_unknown_currency_warns(self):
        value, warn = to_jpy(10, "EUR", self.rates)
        self.assertIsNone(value)
        self.assertIsNotNone(warn)


class ComputeProfitTest(unittest.TestCase):
    def _row(self, price, cost, currency="USD"):
        return {"sold_price": price, "estimated_cost_jpy": cost, "currency": currency}

    def test_candidate_above_threshold_ac6(self):
        # 85USD*155=13175, 手数料13%+3%+送料2000, 仕入6000 → 利益率>=20%
        result = compute_profit(self._row(85.0, 6000), DEFAULT_CONFIG)
        self.assertAlmostEqual(result["sold_price_jpy"], 13175.0)
        self.assertTrue(result["is_candidate"])
        self.assertGreaterEqual(result["profit_rate"], 0.20)

    def test_below_threshold_not_candidate(self):
        # 70USD*155=10850, 仕入5000 → 利益率<20%
        result = compute_profit(self._row(70.0, 5000), DEFAULT_CONFIG)
        self.assertFalse(result["is_candidate"])
        self.assertLess(result["profit_rate"], 0.20)

    def test_no_cost_returns_none(self):
        result = compute_profit(self._row(85.0, None), DEFAULT_CONFIG)
        self.assertIsNone(result["profit_jpy"])
        self.assertFalse(result["is_candidate"])

    def test_config_change_reflected_ac5(self):
        # AC-5: しきい値・為替を設定で変えると結果に反映
        base = compute_profit(self._row(70.0, 5000), DEFAULT_CONFIG)
        self.assertFalse(base["is_candidate"])

        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg["profit"]["threshold_rate"] = 0.10  # しきい値を下げる
        changed = compute_profit(self._row(70.0, 5000), cfg)
        self.assertTrue(changed["is_candidate"])

        cfg2 = copy.deepcopy(DEFAULT_CONFIG)
        cfg2["exchange"]["rates"]["USD"] = 200.0  # 為替を変える
        changed2 = compute_profit(self._row(85.0, 6000), cfg2)
        self.assertAlmostEqual(changed2["sold_price_jpy"], 17000.0)

    def test_fee_change_reflected_ac5(self):
        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg["fees"]["international_shipping_jpy"] = 9000
        result = compute_profit(self._row(85.0, 6000), cfg)
        self.assertEqual(result["intl_shipping_jpy"], 9000)


if __name__ == "__main__":
    unittest.main()
