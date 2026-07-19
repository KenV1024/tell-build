# ebay-jp-research テストレポート（2026-07-10・往復1回目）

対象仕様: `docs/specs/ebay-jp-research/spec.md` 9. 受け入れ条件（AC-1〜AC-10）
実行環境: Windows 11 / `py`（Python） / 作業ディレクトリ `projects/ebay-jp-research/`

## 結果サマリ
PASS: 10 / FAIL: 0

セルフテスト（`py -m unittest discover -s tests -v`）: **36 tests, OK**（FAILなし）

## 項目別結果

- [x] AC-1: サンプルのeBay Sold CSV（10件、うち日本セラー6件）を取り込むと、日本セラー6件のみが処理対象になる — **PASS**
  - 実行コマンド: `py -m ebay_jp_research run --input samples/sold_with_cost_sample.csv --output out.csv`
  - 実際の出力: `取込: 全10件 → 日本セラー6件を処理対象にしました。`
  - `samples/sold_sample.csv` でも同様に確認: `取込: 全10件 → 日本セラー6件を処理対象にしました。`（United States/Germany/United Kingdom/Chinaの4件は除外）

- [x] AC-2: 各商品についてメルカリ・ヤフーフリマ・ラクマの検索URLが3本生成され、ブラウザで開くと関連商品の検索結果が表示される — **PASS**
  - 生成されたURL例（Nintendo Game Boy Color Console）:
    - `https://jp.mercari.com/search?keyword=Nintendo%20Game%20Boy%20Color%20Console`
    - `https://paypayfleamarket.yahoo.co.jp/search/Nintendo%20Game%20Boy%20Color%20Console`
    - `https://fril.jp/search/Nintendo%20Game%20Boy%20Color%20Console`
  - 実際に `curl -s -L` で3本すべてにHTTPリクエストを送信し確認:
    - mercari: HTTP 200、実HTMLページ（Next.js製検索結果ページ）を返却
    - yahoo_flea: HTTP 200、`<title>...Nintendo Game Boy Color Consoleの新品・未使用品・中古品｜Yahoo!フリマ（旧PayPayフリマ）</title>` を含む実際の検索結果ページ
    - fril(ラクマ): HTTP 200、`<title>Nintendo Game Boy Color Consoleのフリマアイテム一覧</title>` を含む実際の検索結果ページ
  - ドメイン・パス・キーワードのURLエンコード（`quote(..., safe="")`でスペースは`%20`）いずれも正しい形式であることを確認

- [x] AC-3: 検索キーワード生成が `"Nintendo Game Boy Color Console Japan Used"` から不要語（Japan/Used等）を除いた妥当なキーワードを出力する — **PASS**
  - 実際の出力CSVの`keywords`列: `Nintendo Game Boy Color Console`（Japan/Usedが除去され、型番相当の固有名詞は保持）
  - ユニットテスト `test_removes_stopwords_ac3` もPASS

- [x] AC-4: 各商品に想定仕入値を入力したCSVを再取込すると、利益額・利益率が計算され出力される — **PASS**
  - 仕入値なし（`samples/sold_sample.csv`）で実行 → `利益計算済み0件・候補0件`、`profit_jpy`等が空欄、`ヒント: estimated_cost_jpy 列に想定仕入値を入力して再実行すると利益が計算されます。`を表示
  - 仕入値あり（`samples/sold_with_cost_sample.csv`）で実行 → `利益計算済み6件・候補4件`、`profit_jpy`/`profit_rate`が実数で埋まる（例: Pokemon Charizard Card → profit_jpy=18550.0, profit_rate=0.4787）

- [x] AC-5: 手数料率・国際送料・為替レート・利益率しきい値を設定ファイルで変更すると、再計算結果に反映される — **PASS**
  - `config.json`のコピーを作り `profit.threshold_rate` を0.20→0.40、`exchange.rates.USD` を155.0→100.0に変更した一時設定ファイルで実行
  - 結果: `sold_price_jpy`が為替反映で変化（例: Pokemon Charizard: 38750.0→25000.0）、候補件数が4件→0件に変化（しきい値変更を反映）。実行後、テスト用一時ファイルは削除済み（本番`config.json`は未変更）

- [x] AC-6: 利益率しきい値（20%）以上の商品だけに「候補」フラグが立ち、出力CSVが利益率降順に並ぶ — **PASS**
  - `out.csv`（既定config, `sold_with_cost_sample.csv`）を`samples/expected_output.csv`と`diff`で比較 → **IDENTICAL**（完全一致）
  - 内容: profit_rate降順 0.4787(yes) > 0.3561(yes) > 0.2956(yes) > 0.2328(yes) > 0.1948(no) > 0.0515(no)。しきい値0.20以上のみ`is_candidate=yes`

- [x] AC-7: オプションの自動取得機能は既定でOFFで、ONにするには設定＋リスク同意フラグの両方が必要（片方だけでは動かない） — **PASS**
  - 既定config（両方false）: `py -m ebay_jp_research auto-fetch` → `自動取得は既定でOFFです。規約リスクのある自動収集はフェーズ1では実装していません。`（収集なし、終了コード0）
  - 片方のみtrue（enabled=true, risk_acknowledged=false）: `自動取得を有効にするには...両方をtrueにする必要があります（現在は片方のみ）。`（収集なし）
  - 両方true: `自動取得機能はフェーズ3で提供予定です。現時点では収集を行わず安全に終了します。`（実収集は行われない＝安全側）

- [x] AC-8: 出力CSVをExcel/スプレッドシートで開くと文字化けせず（UTF-8 BOM等）、必須列がすべて揃っている — **PASS**
  - 先頭3バイトを実際にバイナリ確認: `od -An -tx1 -N3 out.csv` → `ef bb bf`（UTF-8 BOM）
  - 列: `title,seller_location,sold_date,currency,sold_price,sold_price_jpy,estimated_cost_jpy,keywords,mercari_url,yahoo_flea_url,rakuma_url,ebay_fee_jpy,payment_fee_jpy,intl_shipping_jpy,profit_jpy,profit_rate,is_candidate`（17列すべて存在、`samples/expected_output.csv`のヘッダーと一致）

- [x] AC-9: 為替・手数料が未設定のまま実行すると、エラーで止まらず警告を出し既定値を使う（またはガイドを表示） — **PASS**
  - 存在しない設定ファイルを指定: `py -m ebay_jp_research run -i samples/sold_with_cost_sample.csv -o out.csv -c none.json`
  - 実際の出力: `[警告] 設定ファイルが見つかりません（none.json）。すべて既定値で実行します。` に続き `column_mapping`/`japan_filter`/`keyword`/`fees`/`exchange`/`profit`/`search_urls`/`auto_fetch` 各項目について既定値使用の警告を表示
  - 終了コード確認: `EXIT CODE: 0`（エラー終了せず、`out_noconfig.csv`が正常に6件生成された）

- [x] AC-10: サンプル一式（入力CSV・設定ファイル・期待出力）が同梱され、READMEの手順どおりで再現できる — **PASS**
  - `samples/sold_sample.csv`（10件・仕入値なし）、`samples/sold_with_cost_sample.csv`（仕入値入り）、`samples/expected_output.csv`（期待出力）すべて実在し内容を確認
  - README「2. かんたんな使い方 ステップA」記載のコマンドをそのまま実行 → `output.csv`相当の`out.csv`が`expected_output.csv`と完全一致（`diff`でIDENTICAL）
  - `py -m unittest discover -s tests -v` も README「8. テスト」の記載どおり実行し36件PASS

## 補足: セルフテスト実行結果（再確認）

```
py -m unittest discover -s tests -v
...
Ran 36 tests in 0.044s

OK
```

## テスト実施時の注意事項

- 検証で使用した一時出力ファイル（`out.csv`, `out_nocost.csv`, `out_noconfig.csv`, テスト用config複製）はすべて検証後に削除済み。プロジェクトディレクトリは検証前の状態に復元されている（`config.json`本体は未変更）
- コードの修正は一切行っていない（バグがあれば発見のみ、修正はcode-builder担当）

## 総合判定

**全10項目 PASS。FAILなし。**
