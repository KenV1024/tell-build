"""eBay Sold CSV の取込・列マッピング・日本セラー絞り込み（F1-1, F1-2）。"""

import csv
import re

_NUM_RE = re.compile(r"-?\d+(?:[.,]\d+)*")


def parse_money(value):
    """'US $34.99' や '1,200' のような文字列から数値を取り出す。取れなければ None。"""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    match = _NUM_RE.search(text.replace(",", ""))
    if not match:
        return None
    try:
        return float(match.group())
    except ValueError:
        return None


def is_japan_seller(location, japan_values):
    """セラー所在地が日本を示すか判定（部分一致・大文字小文字無視）。"""
    if not location:
        return False
    text = str(location).strip().lower()
    return any(str(v).strip().lower() in text for v in japan_values if str(v).strip())


def load_sold_csv(path, config):
    """Sold CSV を読み込み、列マッピングと日本セラー絞り込みを適用して行リストを返す。

    戻り値: (rows, stats)
      rows: 正規化済み dict のリスト（title, sold_price, currency, sold_date,
            seller_location, estimated_cost_jpy を持つ）
      stats: {"total": 全行数, "japan": 日本セラー件数}
    """
    mapping = config["column_mapping"]
    japan_values = config["japan_filter"]["seller_location_values"]

    rows = []
    total = 0
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            total += 1
            location = raw.get(mapping["seller_location"], "")
            if not is_japan_seller(location, japan_values):
                continue

            title = (raw.get(mapping["title"], "") or "").strip()
            sold_price = parse_money(raw.get(mapping["sold_price"]))
            currency = (raw.get(mapping["currency"], "") or "").strip() or "USD"
            estimated_cost = parse_money(raw.get(mapping["estimated_cost_jpy"]))

            rows.append({
                "title": title,
                "sold_price": sold_price,
                "currency": currency,
                "sold_date": (raw.get(mapping["sold_date"], "") or "").strip(),
                "seller_location": str(location).strip(),
                "estimated_cost_jpy": estimated_cost,
            })

    return rows, {"total": total, "japan": len(rows)}
