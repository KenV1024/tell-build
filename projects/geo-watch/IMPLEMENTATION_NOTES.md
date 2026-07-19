# geo-watch 実装メモ

対象仕様: `docs/specs/geo-watch/spec.md`（ゲート1承認済み）
実装日: 2026-07-18 / 環境: Windows 11, Python 3.14.5（`py` ランチャー）

---

## 1. 何を実装したか（受け入れ条件との対応）

| AC | 内容 | 対応 |
|---|---|---|
| AC-1 | `geo_watch.py` が完走し中間MDを生成、実在フィード3件以上から新着取得 | ○ セルフテストで**新着ありソース7件**を確認 |
| AC-2 | 期間フィルタ（`--days`で件数変化 or ユニットテスト） | ○ `filter_by_days` のユニットテスト＋`--days 1/7/30/365`で件数変化を検証 |
| AC-3 | フィード404でも全体完走・失敗ソースを理由付きで記録 | ○ `collect_rss` が例外を握って `failures` に集約、末尾「取得失敗ソース一覧」に出力。404テスト実施 |
| AC-4 | 差分チェック：初回全件記録→2回目新着0 | ○ 2回目実行で差分新着0件を確認。`compute_new` のユニットテスト |
| AC-5 | `feeds.json` 1行追加でソース追加・コード変更不要 | ○ `rss`/`diff` 配列に追記するだけ。コードは配列を走査 |
| AC-6 | `geo-watch.md` に4手順/インジェクション対策/出力形式/APIコストゼロ明記 | ○ すべて記載 |
| AC-7 | 出力先が無くても自動作成しエラーにならない | ○ `out_dir.mkdir(parents=True, exist_ok=True)`。存在しない `watch404` 先で検証 |
| AC-8 | フィード検証結果を実装メモに記録 | ○ 本メモ「3. フィード検証結果」 |
| AC-9 | ユニットテスト同梱・全PASS | ○ 15テスト全PASS |
| AC-10 | READMEどおり有料API契約なしで再現可能 | ○ 依存は `requests` のみ。手順をREADMEに明記 |

機能要件 F1〜F5 も上表・下記の通り実装済み（F4は `geo-watch.md` に記載、要約はスクリプトでは行わない）。

---

## 2. 実装時判断（仕様第10章の委譲事項の結論）

1. **依存の入れ方**: 追加依存は `requests` のみ（環境に既存）。フィード解析は `feedparser` を使わず
   標準ライブラリ `xml.etree.ElementTree` で実装（依存最小化）。venvは不要。
2. **差分チェックのリンク抽出**: BeautifulSoup等は使わず `requests` ＋正規表現（`href="..."`）で抽出。
   同一ドメインの絶対URLのみ・フラグメント除去・重複除去。
3. **各候補フィードの最終的な扱い**: 「3. フィード検証結果」の通り。
4. **Peec AI / Scrunch AI**: RSSなし（HTML）→ 差分チェックへ回した。
5. **日付フォーマット**: `YYYYMMDD`（実行日基準）で統一。
6. **アクセスマナー**: User-Agent = `geo-watch/1.0 (+personal weekly research tool; contact: owner)`、
   タイムアウト既定20秒、リトライなし（週1回・低頻度のため）。

### 出力先の上書き（仕様範囲内の実装判断）
テストで運用ディレクトリを汚さないよう `--out-dir` / `--feeds` / `--seen` で出力先・入力先を
上書き可能にした。既定は仕様どおり `C:\Users\socra\geo_knowledge\watch`。

### セキュリティ（インジェクション/XML）
- 取得コンテンツはデータ扱い。`eval` 等の動的実行は一切しない。
- XXE / billion-laughs 緩和として、`defusedxml` が環境に無いため標準ライブラリ利用時に
  **DOCTYPE/ENTITY を含むXMLを解析前に拒否**するガード（`_safe_xml_root`）を実装。
  CPythonの `xml.etree` は外部エンティティを取得しないため、内部エンティティ拒否で主要リスクを緩和。
  （より厳格にするなら将来 `defusedxml` 導入を検討。現状は依存最小方針を優先。）

---

## 3. フィード検証結果（AC-8・各候補URLを2026-07-18に実取得検証）

| ソース | URL | 結果 | 最終扱い |
|---|---|---|---|
| Search Engine Land | `https://searchengineland.com/feed` | 200 / RSS 10件 | **RSS採用** |
| Kevin Indig / Growth Memo | `https://www.growth-memo.com/feed` | 200 / RSS 20件 | **RSS採用** |
| iPullRank | `https://ipullrank.com/feed` | 200だが先頭に空行→素の解析失敗。先頭空白/BOM除去で RSS 5件取得可 | **RSS採用**（スクリプトで先頭空白除去済み） |
| SparkToro | `https://sparktoro.com/blog/feed/` | 200 / RSS 10件 | **RSS採用** |
| Ahrefs Blog | `https://ahrefs.com/blog/feed/` | 200 / RSS 10件 | **RSS採用** |
| Semrush Blog | `https://www.semrush.com/blog/feed/` | 200 / RSS 20件 | **RSS採用** |
| 海外SEO情報ブログ（鈴木謙一） | `https://www.suzukikenichi.com/blog/feed/` | 200 / RSS 6件 | **RSS採用** |
| arXiv（GEO論文） | `http://export.arxiv.org/api/query?...generative+engine+optimization...` | 200 / Atom 10件 | **RSS(Atom)採用** |
| Seer Interactive | `https://www.seerinteractive.com/insights` | 200だがHTML（RSSではない） | **差分チェックへ** |
| Profound blog | `https://www.tryprofound.com/blog` | 200 / HTML（RSSなし） | **差分チェックへ** |
| Peec AI blog | `https://www.peec.ai/blog` | 200 / HTML（RSSなし） | **差分チェックへ** |
| Scrunch AI blog | `https://www.scrunchai.com/blog` | 200 / HTML（RSSなし） | **差分チェックへ** |

- 見送りにした候補はなし（HTMLのものはすべて差分チェックへ回した）。
- 差分チェック対象はページ内の同一ドメイン絶対リンクを新着判定に使う（記事本文は取得しない）。

---

## 4. 既知の制約・意図的に省いたこと

- 記事本文の全文取得・保存はしない（RSSのdescription抜粋＝最大280字まで）。仕様スコープ通り。
- 要約・ダイジェスト生成は `geo_watch.py` では行わない（`/geo-watch` セッション側の責務）。
- 定期実行の仕組み（GitHub Actions/cron/タスクスケジューラ）は作らない。手動実行のみ。
- 差分チェックの新着判定は「同一ドメインの全リンク」ベースのため、ナビゲーション等の
  非記事リンクも初回は新着として拾う場合がある（2回目以降は差分のみ＝ノイズは初回限り）。
- 公開日が取得できない記事は期間フィルタで落とさず常に含める（稀なケースの取りこぼし防止）。

---

## 5. セルフテスト結果（全PASS）

### ユニットテスト
```
py -m unittest test_geo_watch -v
→ Ran 15 tests ... OK （15/15 PASS）
```
検証内容: 期間フィルタ(days 1/7/30/365)、差分検出(初回全件/2回目0/増分)、
日付解析(RFC822/ISO8601/不正)、RSS・Atom解析、先頭空白フィード、DOCTYPE拒否、リンク抽出。

### 実行テスト（中間ファイル生成）
- 通常実行: `py geo_watch.py --out-dir <temp> --days 7`
  → `watch_raw_20260717.md` と `seen_urls.json` 生成。RSS新着30件 / 差分新着357件 /
    新着ありソース7 / 取得失敗0（**AC-1: 3件以上を満たす**）。
- 2回目実行: 差分新着**0件**（**AC-4を満たす**）。
- 404テスト: 壊れURLを含む `feeds.json` で実行 → 全体完走、末尾「取得失敗ソース一覧」に
  `HTTPError: 404 ...` を理由付きで記録（**AC-3を満たす**）。
- 自動ディレクトリ作成: 存在しない `watch404` を `--out-dir` に指定 → エラーなく生成
  （**AC-7を満たす**）。

---

## 6. qa-tester向け 動作確認手順

```
# 1. 依存確認（無ければインストール。requestsのみ）
py -m pip install requests

# 2. ユニットテスト
cd projects/geo-watch
py -m unittest test_geo_watch -v        # 15 tests OK を確認

# 3. 収集スクリプト実行（運用先を汚さないよう出力先を一時ディレクトリに）
py geo_watch.py --out-dir "%TEMP%\geo_watch_test" --days 7
#   → watch_raw_YYYYMMDD.md / seen_urls.json が生成、標準出力に件数サマリ

# 4. AC-2（期間で件数変化）
py geo_watch.py --out-dir "%TEMP%\geo_watch_d1" --days 1
py geo_watch.py --out-dir "%TEMP%\geo_watch_d30" --days 30
#   → 30日の方が新着件数が多いことを確認

# 5. AC-4（差分2回目0）: 手順3のコマンドをもう一度実行 → 差分新着0件

# 6. AC-3（404耐性）: feeds.jsonの diff を空にし rss に存在しないURLを1件足して実行
#   → 完走し「取得失敗ソース一覧」に記録される
```

※ `python` エイリアスはMicrosoft Store版スタブに向くことがあるため、本環境では `py` を推奨。
