import json
import os
import tempfile
import unittest

from ebay_jp_research.config import load_config


class ConfigTest(unittest.TestCase):
    def test_missing_file_uses_defaults_ac9(self):
        # AC-9: 設定ファイルが無くてもエラーで落ちず既定値＋警告
        config, warnings = load_config("does_not_exist.json")
        self.assertIn("USD", config["exchange"]["rates"])
        self.assertEqual(config["profit"]["threshold_rate"], 0.20)
        self.assertTrue(any("見つかりません" in w for w in warnings))

    def test_partial_config_filled_ac9(self):
        # exchange と fees を省いた設定 → 既定値で補完し警告
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "config.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"profit": {"threshold_rate": 0.30}}, f)
            config, warnings = load_config(path)
        self.assertEqual(config["profit"]["threshold_rate"], 0.30)
        # 欠けた為替・手数料は既定値
        self.assertEqual(config["exchange"]["rates"]["USD"], 155.0)
        self.assertEqual(config["fees"]["international_shipping_jpy"], 2000)
        self.assertTrue(len(warnings) > 0)

    def test_broken_json_uses_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "config.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{ this is not valid json ")
            config, warnings = load_config(path)
        self.assertEqual(config["profit"]["threshold_rate"], 0.20)
        self.assertTrue(any("失敗" in w for w in warnings))

    def test_auto_fetch_defaults_off_ac7(self):
        config, _ = load_config("does_not_exist.json")
        self.assertFalse(config["auto_fetch"]["enabled"])
        self.assertFalse(config["auto_fetch"]["risk_acknowledged"])


if __name__ == "__main__":
    unittest.main()
