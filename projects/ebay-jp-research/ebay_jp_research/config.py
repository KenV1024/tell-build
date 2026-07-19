"""設定ファイル(config.json)の読み込みと既定値。

未設定でもエラーで止めず、既定値で補完し警告を返す（AC-9）。
"""

import json
import os

# コードを触らず設定ファイルで変更できる項目の既定値（非機能要件・保守性）
DEFAULT_CONFIG = {
    "column_mapping": {
        "title": "Title",
        "sold_price": "Sold price",
        "currency": "Currency",
        "sold_date": "Sold date",
        "seller_location": "Seller location",
        "estimated_cost_jpy": "estimated_cost_jpy",
    },
    "japan_filter": {
        # セラー所在地がこれらのいずれかに一致（部分一致・大文字小文字無視）したら日本セラー扱い
        "seller_location_values": ["Japan", "日本", "JP"],
    },
    "keyword": {
        # タイトルから取り除く不要語（小文字で比較）
        "stopwords": [
            "japan", "japanese", "used", "new", "for", "the", "with", "and",
            "genuine", "authentic", "oem", "fs", "f/s", "free", "shipping",
            "import", "rare", "vintage", "excellent", "good", "mint",
            "condition", "from", "very", "nice", "boxed", "set", "lot",
        ],
        "max_keywords": 6,
    },
    "fees": {
        "ebay_final_value_fee_rate": 0.13,   # eBay落札手数料率
        "payment_processing_fee_rate": 0.03, # 決済/入金手数料率
        "international_shipping_jpy": 2000,   # 国際送料（円・固定概算）
    },
    "exchange": {
        # 通貨 -> 円 のレート。売価をこのレートで円換算する
        "rates": {"USD": 155.0, "JPY": 1.0},
    },
    "profit": {
        "threshold_rate": 0.20,  # 利益率しきい値（これ以上で候補フラグ）
    },
    "search_urls": {
        # {keyword} をURLエンコード済みキーワードに置換する
        "mercari": "https://jp.mercari.com/search?keyword={keyword}",
        "yahoo_flea": "https://paypayfleamarket.yahoo.co.jp/search/{keyword}",
        "rakuma": "https://fril.jp/search/{keyword}",
    },
    "auto_fetch": {
        # フェーズ3で提供予定の自動取得オプション。フェーズ1では骨格のみ（AC-7）
        "enabled": False,
        "risk_acknowledged": False,
    },
}


def _merge(default, override, warnings, path=""):
    """default をベースに override を上書きした dict を返す。欠けたキーは警告に記録。"""
    result = {}
    for key, default_value in default.items():
        full_key = f"{path}.{key}" if path else key
        if not isinstance(override, dict) or key not in override:
            result[key] = default_value
            warnings.append(f"設定 '{full_key}' が未設定のため既定値 {default_value!r} を使用します。")
            continue
        override_value = override[key]
        if isinstance(default_value, dict) and isinstance(override_value, dict):
            result[key] = _merge(default_value, override_value, warnings, full_key)
        else:
            result[key] = override_value
    return result


def load_config(path):
    """設定ファイルを読み込み、(config, warnings) を返す。

    ファイルが無い/壊れている/キーが欠けていてもエラーで落とさず、
    既定値で補完し warnings に理由を積む（AC-9）。
    """
    warnings = []
    user_config = {}

    if not path or not os.path.exists(path):
        warnings.append(
            f"設定ファイルが見つかりません（{path}）。すべて既定値で実行します。"
        )
        return _merge(DEFAULT_CONFIG, {}, warnings), warnings

    try:
        with open(path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        warnings.append(
            f"設定ファイルの読み込みに失敗しました（{exc}）。すべて既定値で実行します。"
        )
        return _merge(DEFAULT_CONFIG, {}, warnings), warnings

    if not isinstance(user_config, dict):
        warnings.append("設定ファイルの形式が不正です。すべて既定値で実行します。")
        user_config = {}

    return _merge(DEFAULT_CONFIG, user_config, warnings), warnings
