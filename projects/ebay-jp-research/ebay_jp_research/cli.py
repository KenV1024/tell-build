"""コマンドライン入口。

使い方:
  python -m ebay_jp_research run --input samples/sold_sample.csv --output out.csv
  python -m ebay_jp_research auto-fetch
"""

import argparse
import os
import sys

from ebay_jp_research.config import load_config
from ebay_jp_research.keywords import generate_keywords
from ebay_jp_research.loader import load_sold_csv
from ebay_jp_research.output import write_output_csv
from ebay_jp_research.profit import compute_profit
from ebay_jp_research.urls import build_search_urls

DEFAULT_CONFIG_PATH = "config.json"
DEFAULT_OUTPUT_PATH = "output.csv"


def _print_warnings(warnings):
    for w in warnings:
        print(f"[警告] {w}", file=sys.stderr)


def cmd_run(args):
    config, warnings = load_config(args.config)
    _print_warnings(warnings)

    if not os.path.exists(args.input):
        print(f"[エラー] 入力CSVが見つかりません: {args.input}", file=sys.stderr)
        return 2

    rows, stats = load_sold_csv(args.input, config)
    print(f"取込: 全{stats['total']}件 → 日本セラー{stats['japan']}件を処理対象にしました。")

    kw_conf = config["keyword"]
    templates = config["search_urls"]

    results = []
    priced = 0
    candidates = 0
    for row in rows:
        keywords = generate_keywords(
            row["title"], kw_conf["stopwords"], kw_conf["max_keywords"]
        )
        search_urls = build_search_urls(keywords, templates)
        profit = compute_profit(row, config)
        if profit.get("warning"):
            print(f"[警告] {row['title']}: {profit['warning']}", file=sys.stderr)
        if profit["profit_jpy"] is not None:
            priced += 1
        if profit["is_candidate"]:
            candidates += 1

        results.append({
            "title": row["title"],
            "seller_location": row["seller_location"],
            "sold_date": row["sold_date"],
            "currency": row["currency"],
            "sold_price": row["sold_price"],
            "estimated_cost_jpy": row["estimated_cost_jpy"],
            "keywords": keywords,
            "mercari_url": search_urls.get("mercari", ""),
            "yahoo_flea_url": search_urls.get("yahoo_flea", ""),
            "rakuma_url": search_urls.get("rakuma", ""),
            **{k: profit[k] for k in (
                "sold_price_jpy", "ebay_fee_jpy", "payment_fee_jpy",
                "intl_shipping_jpy", "profit_jpy", "profit_rate", "is_candidate",
            )},
        })

    written = write_output_csv(args.output, results)
    print(f"出力: {args.output} に {written}件（利益計算済み{priced}件・候補{candidates}件）を書き出しました。")
    if priced == 0:
        print("ヒント: estimated_cost_jpy 列に想定仕入値を入力して再実行すると利益が計算されます。")
    return 0


def cmd_auto_fetch(args):
    """フェーズ3で提供予定の自動取得オプション（骨格・AC-7）。"""
    config, warnings = load_config(args.config)
    _print_warnings(warnings)

    af = config["auto_fetch"]
    enabled = bool(af.get("enabled"))
    ack = bool(af.get("risk_acknowledged"))

    if not enabled and not ack:
        print("自動取得は既定でOFFです。規約リスクのある自動収集はフェーズ1では実装していません。")
        return 0

    if enabled != ack:
        print(
            "自動取得を有効にするには auto_fetch.enabled と auto_fetch.risk_acknowledged の"
            "両方を true にする必要があります（現在は片方のみ）。"
        )
        return 0

    # 両方 true でも実際の取得は行わず、安全に終了する（フェーズ3で提供予定）
    print("自動取得機能はフェーズ3で提供予定です。現時点では収集を行わず安全に終了します。")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="ebay_jp_research",
        description="eBay Sold CSV から国内フリマ仕入れの利益候補を作るリサーチ支援ツール（フェーズ1）。",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Sold CSV を取り込み、利益候補CSVを出力する")
    p_run.add_argument("--input", "-i", required=True, help="eBay Sold CSV のパス")
    p_run.add_argument("--output", "-o", default=DEFAULT_OUTPUT_PATH, help="出力CSVのパス")
    p_run.add_argument("--config", "-c", default=DEFAULT_CONFIG_PATH, help="設定ファイル(config.json)のパス")
    p_run.set_defaults(func=cmd_run)

    p_af = sub.add_parser("auto-fetch", help="（フェーズ3予定）自動取得オプションの状態確認")
    p_af.add_argument("--config", "-c", default=DEFAULT_CONFIG_PATH, help="設定ファイル(config.json)のパス")
    p_af.set_defaults(func=cmd_auto_fetch)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
