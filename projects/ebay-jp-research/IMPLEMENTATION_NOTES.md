# 実装メモ: ebay-jp-research フェーズ1（MVP）

対象仕様: `docs/specs/ebay-jp-research/spec.md` の「10. 実装計画」フェーズ1。
実装範囲は AC-1〜AC-10（AC-7は骨格）。

---

## 1. 何を実装したか（受け入れ条件との対応）

| AC | 実装箇所 | 内容 |
|---|---|---|
| AC-1 | `loader.py` | Sold CSV取込＋セラー所在地=日本の絞り込み。10件中6件が対象になる |
| AC-2 | `urls.py` | メルカリ／ヤフーフリマ／ラクマの検索URLを3本生成（`config.search_urls`で変更可） |
| AC-3 | `keywords.py` | 不要語(Japan/Used等)除去・型番保持のキーワード生成 |
| AC-4 | `profit.py` + `cli.py` | `estimated_cost_jpy`入りCSVを再取込すると利益額・利益率を計算 |
| AC-5 | `config.py` | 手数料率・国際送料・為替・しきい値を`config.json`で変更→再計算に反映 |
| AC-6 | `profit.py` + `output.py` | しきい値以上に`is_candidate`、出力は利益率降順 |
| AC-7 | `cli.py`(auto-fetch) | 既定OFF。片方/両方trueでも収集せず「フェーズ3で提供予定」で安全終了（骨格） |
| AC-8 | `output.py` | `utf-8-sig`(BOM付き)で出力、必須列17列すべて揃える |
| AC-9 | `config.py` | 設定欠落/ファイル無/壊れたJSONでも落ちず、警告＋既定値で継続 |
| AC-10 | `samples/`, `README.md` | サンプル入力・設定・期待出力・非エンジニア向け手順を同梱 |

---

## 2. 設計判断・前提

- **依存ゼロ**: Python標準ライブラリのみ（csv, json, argparse, urllib, re, unittest）。
  `requirements.txt`は追加インストール不要である旨のみ。設定は`config.json`（JSONはstdlibで確実に読める）。
- **利益率の定義**: `profit_rate = 利益 ÷ 売上(円)`。仕様の計算式
  「eBay売価 − eBay手数料 − 決済手数料 − 国際送料 − 仕入値」をそのまま実装し、売上比の率にした。
- **通貨換算**: `exchange.rates`（通貨→円）で換算。売価文字列は`US $85.00`等からも数値を抽出。
- **日本セラー判定**: `seller_location`に`Japan`/`日本`/`JP`のいずれかを含めば対象（部分一致・大小無視）。
- **1コマンドで両パスを兼ねる**: `run`は仕入値が無い行はURL付きの「下調べ表」として出力し、
  仕入値がある行は利益計算する。同じ出力CSVを埋めて再取込するとラウンドトリップできる。

---

## 3. 既知の制約・意図的に省いたこと（スコープ外）

- フリマの自動価格取得（スクレイピング）は未実装（仕様どおり。AC-7は骨格のみ）。
- 為替の自動取得・スプレッドシート出力・GitHub Actions定期実行はフェーズ2/3のため未実装。
- eBay手数料はカテゴリ別ではなく一律率（`config`で1つの率）。カテゴリ別化はフェーズ2以降。
- 買い手負担の送料はeBay売価(revenue)に含めていない（仕様の計算式に合わせた簡略化）。
- タイトルのキーワード生成は不要語除去＋型番保持の範囲。高度な形態素解析はしない。

---

## 4. qa-tester向け: 検証手順のヒント

作業ディレクトリはすべて `projects/ebay-jp-research/`。Pythonは `py` で起動。

- **セルフテスト全実行**:
  `py -m unittest discover -s tests -v` → 36 tests OK を確認。
- **AC-1/AC-2/AC-6/AC-8（一括）**:
  `py -m ebay_jp_research run --input samples/sold_with_cost_sample.csv --output out.csv`
  → 標準出力に「日本セラー6件」、`out.csv`が6行・URL3本・利益率降順・`is_candidate`にyes/no混在・
  先頭バイトがBOM(EF BB BF)。`samples/expected_output.csv`と一致するはず。
- **AC-3**: `sold_with_cost_sample.csv`のGame Boy行の`keywords`が
  `Nintendo Game Boy Color Console`（Japan/Usedが消えている）。
- **AC-4**: 仕入値なし`samples/sold_sample.csv`で実行→`profit_*`が空欄・URLは出る。
  出力の`estimated_cost_jpy`に値を入れて再実行→利益が埋まる。
- **AC-5**: `config.json`の`profit.threshold_rate`や`exchange.rates.USD`を変えて再実行→
  候補件数や`sold_price_jpy`が変わる。
- **AC-7**: `config.json`の`auto_fetch`を書き換え、`py -m ebay_jp_research auto-fetch`。
  両false=「既定でOFF」、片方true=「両方必要」、両true=「フェーズ3で提供予定」。いずれも収集しない。
- **AC-9**: 存在しない設定パスを渡す
  `py -m ebay_jp_research run -i samples/sold_with_cost_sample.csv -o out.csv -c none.json`
  → 警告が出るがエラー終了せず`out.csv`が生成される（終了コード0）。
- **AC-10**: 本READMEの手順どおりで再現できること。

---

## 5. セルフテスト実行結果

```
py -m unittest discover -s tests -v
...
Ran 36 tests in 0.047s
OK
```

全36件PASS（FAILなし）。
