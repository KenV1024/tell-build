# ebay-jp-research（フェーズ1・MVP）

eBayで「日本のセラーから売れた商品（Sold）」のCSVを取り込み、
国内フリマ（メルカリ／ヤフーフリマ／楽天ラクマ）の検索URLと、
想定仕入値からの利益額・利益率を計算して、**利益候補リストのCSV**を作るツールです。

> このフェーズ1は「どの商品を狙うか」の材料づくりに絞っています。
> 実際の購入・出品・出荷や、フリマの自動収集（スクレイピング）は行いません。

---

## 1. 必要なもの

- Windows 11
- Python 3.9 以上（このPCでは `py` コマンドで動きます）
- 追加インストールは不要です（標準ライブラリだけで動きます）

Pythonが入っているか確認する:

```
py --version
```

---

## 2. かんたんな使い方（3ステップ）

このツールは付属のサンプルだけで一通り動作を試せます。
コマンドはこのフォルダ（`README.md`がある場所）で実行してください。

### ステップA: まず動かしてみる（サンプル）

```
py -m ebay_jp_research run --input samples/sold_with_cost_sample.csv --output output.csv
```

- `output.csv` が作られます。Excelで開くと、利益率の高い順に商品が並びます。
- `is_candidate` が `yes` の行が「利益率20%以上の候補」です。

### ステップB: 自分のデータで動かす（2回に分けて使うのがおすすめ）

1. Terapeak等でSoldを絞り込み、CSVで書き出します（列は下の「入力CSV」を参照）。
2. **1回目の実行**（まだ仕入値は分かっていない状態）:

   ```
   py -m ebay_jp_research run --input あなたのSold.csv --output 下調べ.csv
   ```

   `下調べ.csv` には各商品の検索URLが入っています。URLを開いて国内相場を目視で確認します。

3. `下調べ.csv` の `estimated_cost_jpy` 列に、確認した**想定仕入値（円）**を手で入力して保存します。
4. **2回目の実行**（利益計算）:

   ```
   py -m ebay_jp_research run --input 下調べ.csv --output 利益候補.csv
   ```

   `利益候補.csv` に利益額・利益率・候補フラグが入ります。

---

## 3. 入力CSV（eBay Sold）の列

既定では以下の列名を読みます（`config.json` で自由に変えられます）。

| 列名 | 意味 | 必須 |
|---|---|---|
| `Title` | 商品タイトル | 必須 |
| `Sold price` | 売れた価格（`US $85.00` のような形式もOK） | 必須 |
| `Currency` | 通貨（例: `USD`）。空欄なら `USD` とみなします | 任意 |
| `Sold date` | 販売日 | 任意 |
| `Seller location` | セラー所在地（`Japan` を含む行だけ処理します） | 必須 |
| `estimated_cost_jpy` | あなたが入力する想定仕入値（円） | 2回目のみ |

> 列名がTerapeakの書き出しと違う場合は、`config.json` の `column_mapping` を書き換えてください。

---

## 4. 出力CSVの列

`title / seller_location / sold_date / currency / sold_price / sold_price_jpy /
estimated_cost_jpy / keywords / mercari_url / yahoo_flea_url / rakuma_url /
ebay_fee_jpy / payment_fee_jpy / intl_shipping_jpy / profit_jpy / profit_rate / is_candidate`

- **UTF-8 BOM付き**で出力するので、Excelで開いても日本語が文字化けしません。
- **利益率の高い順**に並びます。仕入値が未入力の行は末尾にまとまります。
- `profit_rate` は「利益 ÷ 売上（円）」です（例: `0.2328` = 約23%）。

---

## 5. 設定変更（config.json）

コードを触らずに、`config.json` を書き換えるだけで挙動を変えられます。

| 項目 | 意味 | 既定値 |
|---|---|---|
| `fees.ebay_final_value_fee_rate` | eBay落札手数料率 | 0.13 |
| `fees.payment_processing_fee_rate` | 決済手数料率 | 0.03 |
| `fees.international_shipping_jpy` | 国際送料（円・固定概算） | 2000 |
| `exchange.rates.USD` | 1ドル＝何円か | 155.0 |
| `profit.threshold_rate` | 候補にする利益率のしきい値 | 0.20（=20%） |
| `keyword.stopwords` | 検索キーワードから除く不要語 | Japan, Used ほか |
| `column_mapping` | 入力CSVの列名の対応表 | 上記表のとおり |
| `search_urls` | 各フリマの検索URLの形（`{keyword}` が置換されます） | 3サイト分 |

> 設定ファイルが無かったり、一部の項目が抜けていても、
> ツールは**エラーで止まらず**、警告を出しながら既定値で動きます。

---

## 6. 自動取得（スクレイピング）について

規約リスクがあるフリマの自動収集は**フェーズ1では実装していません**。
`config.json` の `auto_fetch` は骨格だけ用意してあります。

```
py -m ebay_jp_research auto-fetch
```

- `enabled` と `risk_acknowledged` が両方 `false`（既定）→「OFFです」と表示して終了。
- 片方だけ `true` →「両方を true にする必要がある」と表示して終了。
- 両方 `true` →「フェーズ3で提供予定」と表示して**安全に終了**（実際の収集はしません）。

---

## 7. 同梱サンプル

- `samples/sold_sample.csv` … Sold 10件（うち日本セラー6件）。仕入値なし。
- `samples/sold_with_cost_sample.csv` … 上記に想定仕入値を入れたもの。
- `samples/expected_output.csv` … 上記を処理した期待出力の例。

---

## 8. テスト（開発者向け）

```
py -m unittest discover -s tests -v
```
