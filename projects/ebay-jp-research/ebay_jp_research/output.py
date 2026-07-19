"""結果CSVの出力（F4）。UTF-8 BOM でExcel文字化けを防ぐ（AC-8）。"""

import csv

# 出力列（必須列がすべて揃うこと・AC-8）
FIELDNAMES = [
    "title",
    "seller_location",
    "sold_date",
    "currency",
    "sold_price",
    "sold_price_jpy",
    "estimated_cost_jpy",
    "keywords",
    "mercari_url",
    "yahoo_flea_url",
    "rakuma_url",
    "ebay_fee_jpy",
    "payment_fee_jpy",
    "intl_shipping_jpy",
    "profit_jpy",
    "profit_rate",
    "is_candidate",
]


def sort_rows(rows):
    """利益率降順に並べる。利益率が未計算(None)の行は末尾（AC-6, F4-2）。"""
    return sorted(
        rows,
        key=lambda r: (r.get("profit_rate") is not None, r.get("profit_rate") or 0.0),
        reverse=True,
    )


def _fmt(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    return value


def write_output_csv(path, rows):
    """行リストを CSV に書き出す。utf-8-sig で BOM 付き。"""
    ordered = sort_rows(rows)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for row in ordered:
            writer.writerow({k: _fmt(row.get(k)) for k in FIELDNAMES})
    return len(ordered)
