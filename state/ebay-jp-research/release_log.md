# ebay-jp-research リリースログ（2026-07-10）

## ステータス: 実行計画（承認待ち・ゲート2）

**この文書はドラフトです。まだ git commit / push などの操作は一切実行していません。**
以下の内容でよいかご確認いただき、承認をいただいてから実行します。

---

## 1. 何を公開するか（対象）

- **プロジェクト**: `ebay-jp-research`（フェーズ1・MVP、qa-tester検証で受け入れ条件AC-1〜AC-10 全10件PASS）
- **中身**: eBayの「日本セラーからのSold（売れた）CSV」を取り込み、メルカリ／ヤフーフリマ／ラクマの検索URLと想定利益を計算する、あなたのPCだけで動くローカルCLIツール（Webサービスではありません。外部への公開・課金は発生しません）

### コミット対象ファイル（git statusで確認済みの未追跡ファイル）

| パス | 内容 |
|---|---|
| `docs/specs/ebay-jp-research/spec.md` | 仕様書（ゲート1で承認済み） |
| `projects/ebay-jp-research/` 一式 | ツール本体（コード・README・サンプルCSV・設定ファイル・テスト） |
| `state/ebay-jp-research/test_report.md` | qa-testerのテスト結果（全PASS） |
| `state/ebay-jp-research/pipeline_status.json` | パイプライン進行状況 |
| `state/ebay-jp-research/release_log.md` | 本ログ（実行後に結果を追記） |

### 除外するもの（コミットに含めない）

- `projects/ebay-jp-research/**/__pycache__/` および `*.pyc`
  → Pythonがテスト実行時に自動生成した中間ファイル（キャッシュ）。ソースコードではないので不要。コミットに混ざらないよう明示的に除外します。
- テスト時に作られた一時出力（`out.csv`等）は、qa-testerが検証後に削除済みで現在は残っていないことを確認済みです。

### 秘密情報チェック

- `config.json`・ソースコード内を検索し、APIキー・パスワード・トークン等の認証情報は含まれていないことを確認済みです（このツールは外部サービスへの自動アクセスを行わない設計のため、そもそも認証情報は不要です）。

---

## 2. どこへ公開するか

- **リポジトリ**: `https://github.com/KenV1024/tell-build`（現在のリモート `origin`）
- **公開範囲**: **パブリック（誰でも閲覧可能）** ← GitHub APIで確認済み（`"private": false`）
- **提案**: ローカルコミット＋リモート（GitHub）へのpushの両方を行う
  - 理由: 現状の`tell-build`運用は他プロジェクトも同様に`origin/master`へpushして記録する方針（既存コミット履歴より）。ローカルのみに留めると、他のPCとの同期や万一のPC故障時にコードが失われるリスクがあります。
- **公開リポジトリであることのリスク確認**:
  - コード・サンプルCSV（ダミーデータ）・設定ファイルが誰でも閲覧可能になります。
  - 認証情報・個人情報は含まれていないため、情報漏えいのリスクは無いと判断します。
  - 課金は発生しません（GitHubの無料パブリックリポジトリ、外部APIコールなし）。
  - 業務・事業上の機密（ASPの成果報酬率や仕入戦略の詳細等）はこのツールのコード・サンプルには含まれていません。念のため、pushする前に一度ご自身でも「見られて困る情報が無いか」だけご確認ください。

---

## 3. 戻し方（ロールバック手順・非エンジニア向け）

### ケースA: コミットしたが、まだpushしていない場合
直前のコミットを取り消したいだけなら:
```
git reset --soft HEAD~1
```
→ ファイルの変更はそのまま残り、「コミットした」という記録だけ取り消されます。

### ケースB: すでにpushしてしまった後に問題が見つかった場合
コミットを打ち消す「取り消しコミット」を新しく作る方法（履歴を書き換えないので安全）:
```
git revert <コミットのハッシュ>
git push
```
→ 「元に戻す」という新しい記録が追加される形になります。過去の記録は消えません。

### ケースC: とにかく今すぐ非公開にしたい場合
GitHubの当該リポジトリの Settings → Danger Zone → Change repository visibility から
一時的に「Private」に切り替えることも可能です（コード自体は消えません）。

※ `git reset --hard`や`force push`のような、変更を完全に消す操作は今回は使いません（安全のため）。

---

## 4. 実行手順（承認後に実行するコマンド）

```bash
# 1. 現状確認
git status

# 2. コミット対象を追加（__pycache__を除外）
git add docs/specs/ebay-jp-research/
git add projects/ebay-jp-research/ -- ':!**/__pycache__' ':!**/*.pyc'
git add state/ebay-jp-research/test_report.md state/ebay-jp-research/pipeline_status.json state/ebay-jp-research/release_log.md

# 3. 追加内容の最終確認（__pycache__/*.pycが含まれていないこと）
git status
git diff --cached --stat

# 4. コミット
git commit -m "$(cat <<'EOF'
feat: ebay-jp-researchツールを追加（フェーズ1・MVP）

eBayの日本セラーSoldCSVから国内フリマ検索URLと想定利益を計算するローカルCLIツール。
qa-tester検証で受け入れ条件AC-1〜AC-10 全10件PASS。

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
EOF
)"

# 5. リモートへpush（公開）
git push origin master

# 6. 結果確認
git log --oneline -3
git status
```

### 参考: __pycache__を今後も自動で除外したい場合
リポジトリ直下の`.gitignore`に以下を追記することを提案します（今回のコミットとは別に、承認いただければ実施します）:
```
__pycache__/
*.pyc
```

---

## 5. ユーザーがツールを使い始めるための最初の一歩

1. READMEの場所: `projects/ebay-jp-research/README.md`
2. 最初に実行するコマンド（このフォルダに移動してから）:
   ```
   py -m ebay_jp_research run --input samples/sold_with_cost_sample.csv --output output.csv
   ```
   → 付属のサンプルCSVで動作し、`output.csv`が作られます。Excelで開くと利益率順に並び、`is_candidate`が`yes`の行が候補です。
3. 自分のeBay Soldデータで使う場合はREADMEの「2. かんたんな使い方 ステップB」を参照してください。

---

## 公開内容（承認後に確定）

- 対象: `ebay-jp-research`（フェーズ1・MVP一式）
- 公開先: `https://github.com/KenV1024/tell-build`（パブリックリポジトリ・`master`ブランチ）

## 実行手順
（上記「4. 実行手順」参照。承認後に実施）

## ロールバック手順
（上記「3. 戻し方」参照）

## 結果
- 公開URL/場所: （実行後に記載）
- 実行日時: （実行後に記載）
