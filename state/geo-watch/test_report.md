# geo-watch テストレポート（2026-07-18）

検証対象:
- 仕様書: `c:\Users\socra\tell-build\docs\specs\geo-watch\spec.md`（第8章 AC-1〜AC-10）
- 実装物: `c:\Users\socra\tell-build\projects\geo-watch\`
- 実行環境: Windows 11 / Python 3.14.5（`py`ランチャー） / `requests` 2.34.0（インストール済み確認）
- テスト出力先: `c:\Users\socra\tell-build\state\geo-watch\qa_tmp\`（運用ディレクトリ `C:\Users\socra\geo_knowledge\watch\` は非汚染）

## 結果サマリ
PASS: 10 / FAIL: 0

## 項目別結果

- [x] **AC-1**: `python geo_watch.py` が完走し中間MD生成、実在フィード3件以上から新着取得 — PASS
  - 実行: `py geo_watch.py --out-dir qa_tmp\ac1 --days 7`
  - 結果: `watch_raw_20260718.md` 生成。RSS新着30件、新着ありソース7件（Search Engine Land / Kevin Indig 等）、取得失敗0件。3件以上の条件を満たす。

- [x] **AC-2**: 期間フィルタが機能する（`--days`で件数変化） — PASS
  - 実行: `--days 1` → RSS新着10件・新着ありソース3。`--days 30` → RSS新着65件・新着ありソース8。
  - 件数が明確に変化することを確認（ユニットテスト`test_days_30_vs_1_differs`もPASS）。
  - 備考: 差分チェック側（357件）は`--days`の対象外（仕様上RSSのみに適用される期間フィルタのため仕様通り）。

- [x] **AC-3**: フィード1件が404でも全体完走・失敗ソースが理由付きで記録される — PASS
  - 実行: 実在フィード1件＋存在しないURL1件を含むテスト用`feeds_404.json`で実行。
  - 結果: 完走（RSS新着10件取得）。末尾「取得失敗ソース一覧」に
    `**Broken 404 Test** (...) — HTTPError: 404 Client Error: Not Found for url: ...` と理由付きで記録。

- [x] **AC-4**: 差分チェック：初回全件記録→2回目実行で新着0件 — PASS
  - 実行: diffのみのテスト用feeds（Profound blog）で1回目→2回目連続実行。
  - 結果: 1回目 差分新着202件、2回目 差分新着0件。

- [x] **AC-5**: `feeds.json`に1行追記のみでソース追加、`geo_watch.py`コード変更不要 — PASS
  - 実行: RSS 1件のみのfeedsで実行(RSS新着10件・ソース1)→ Ahrefs Blogを1件追記して再実行。
  - 結果: RSS新着13件・新着ありソース2に増加。`git diff --stat -- geo_watch.py` で差分なしを確認（コード無変更）。

- [x] **AC-6**: `geo-watch.md`に(a)4手順(b)インジェクション対策(c)ダイジェスト出力形式(d)追加APIコストゼロ、が記載 — PASS
  - `geo-watch.md`を確認。手順1〜4が存在（収集実行／Gmail検索／セッション内要約／APIコストゼロ確認）。
  - 「重要な前提（厳守）」節にプロンプトインジェクション対策の明記あり。
  - ダイジェスト構成に「今週のトップ3トピック」「我々のGEO戦略への影響（⚠️警告含む）」「ソース別新着一覧」「取得失敗ソース」の4項目すべて記載。
  - 追加APIコストゼロは「重要な前提」および手順4の両方に明記。

- [x] **AC-7**: 出力先ディレクトリが存在しなくても自動作成されエラーにならない — PASS
  - 事前に`qa_tmp\notexist_yet`が存在しないことを確認した上で`--out-dir qa_tmp\notexist_yet\deeper`（2階層とも未存在）を指定して実行。
  - 結果: エラーなく完走（EXIT=0）。`watch_raw_20260718.md`が生成されたことを`Test-Path`で確認（True）。

- [x] **AC-8**: 実装時のフィード検証結果（成否・扱い）が実装メモに記録されている — PASS
  - `IMPLEMENTATION_NOTES.md`「3. フィード検証結果」に候補URL12件すべての実取得結果（ステータス・件数）と最終扱い（RSS採用／差分チェック）が表形式で記録されていることを確認。

- [x] **AC-9**: ユニットテスト同梱・セルフテスト全PASS（期間フィルタ・差分検出を含む） — PASS
  - 実行: `py -m unittest test_geo_watch -v`
  - 結果: `Ran 15 tests in 0.016s / OK`（15/15 PASS）。期間フィルタ4テスト・差分検出3テストを含む。

- [x] **AC-10**: READMEの手順どおりに追加の有料API契約なしで実行が再現できる — PASS
  - `README.md`記載の依存インストール手順`py -m pip install requests`はrequests既存インストール（2.34.0）で確認済み。
  - README記載の各オプション（`--days`／`--out-dir`／`--feeds`／`--seen`）がAC-1〜AC-7の実行で全て文書通りに機能することを確認済み。
  - 備考: 既定の`--out-dir`（運用ディレクトリ`C:\Users\socra\geo_knowledge\watch\`）への実行そのものは、QA方針（運用ディレクトリを汚さない）に従い今回は未実行。コード上のデフォルト値（`DEFAULT_OUT_DIR`）とREADMEの記載一致は確認済み。

## 備考（仕様外・気付き事項。FAIL扱いではない）

- 差分チェックは「同一ドメインの全リンク」を新着対象とするため、初回実行時にナビゲーション等の非記事リンクも大量に新着として出る（Profound blogのみで202件、全体実行では357件）。実装メモにも既知の制約として明記されており、2回目以降はノイズが収まる設計のため仕様範囲内と判断（FAILとしない）。
- `collect_rss`内の`f.get("name", url_or_unknown(f))`は、`name`キーが存在する場合でも`url_or_unknown(f)`を評価してから渡している（Python的にはデフォルト引数として無駄に評価されるだけで副作用はなし。動作への影響なし）。

## 総合判定

AC-1〜AC-10 すべてPASS。FAILなし。
