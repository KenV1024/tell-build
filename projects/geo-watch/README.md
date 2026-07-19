# geo-watch

GEO業界トップランナーの発信（ブログ・論文・ニュースレター）を週1回まとめて収集し、
Claude Codeセッション内で要約して週次ダイジェストを作るための情報キャッチアップ支援ツール。

- 収集は無料のRSS/Atom取得＋差分チェックのみ。**有料API・LLM APIは使わない。**
- 定期実行はしない。**週1回手動で `/geo-watch` を実行**する運用。
- 要約は `geo_watch.py` ではなく `/geo-watch` コマンド（セッション内のClaude）が行う。

## 構成

| ファイル | 役割 |
|---|---|
| `geo_watch.py` | RSS/Atom収集＋期間フィルタ＋差分チェック＋中間ファイル出力 |
| `feeds.json` | 収集ソース定義（`rss` と `diff` の2区分） |
| `geo-watch.md` | `/geo-watch` スラッシュコマンド定義（`~/.claude/commands/` へ配置） |
| `test_geo_watch.py` | ユニットテスト（ネットワーク非依存） |

## 依存とインストール

- Windows 11 / Python 3（`py` ランチャーを想定。3.11以上推奨）
- 追加ライブラリは **`requests` のみ**。フィード解析は標準ライブラリ（`xml.etree`）を使用。

```
py -m pip install requests
```

> `requests` が既に入っていれば追加インストール不要。venvは必須ではない。

## 実行方法

```
py geo_watch.py
```

主なオプション:

| オプション | 既定 | 説明 |
|---|---|---|
| `--days N` | 7 | 直近N日の新着だけ抽出 |
| `--out-dir PATH` | `C:\Users\socra\geo_knowledge\watch` | 中間ファイル・seen_urls.jsonの出力先 |
| `--feeds PATH` | スクリプト同階層の `feeds.json` | ソース定義ファイル |
| `--seen PATH` | out-dir内の `seen_urls.json` | 差分チェックの記録ファイル |
| `--timeout SEC` | 20 | HTTPタイムアウト |

実行すると出力先に以下が生成される:

- `watch_raw_YYYYMMDD.md` … 収集結果（ソース別新着＋差分新着＋取得失敗一覧）
- `seen_urls.json` … 差分チェック用の既読URL記録（次回実行時に差分判定へ使う）

## ソースの追加・削除

`feeds.json` を編集するだけ。**`geo_watch.py` のコード変更は不要。**

- RSS/Atomがあるサイト → `rss` 配列に `{ "name": "...", "url": "..." }` を追記
- RSSがないサイト → `diff` 配列に `{ "name": "...", "url": "..." }` を追記（ページ内リンクの差分で新着検出）

## テスト

```
py -m unittest test_geo_watch
```

## 週次ダイジェストの生成（要約）

収集後の要約は Claude Code の `/geo-watch` コマンドで行う。詳細は `geo-watch.md` を参照。
`geo_watch.py` 単体では要約せず、収集だけを行う。
