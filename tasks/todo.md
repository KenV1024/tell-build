# 進行中タスク

## 2026-07-07: プロジェクト初期構築
- [x] forgeディレクトリ・gitリポジトリ作成
- [x] CLAUDE.md 作成
- [x] shared/pipeline_rules.md 作成
- [x] 6体のサブエージェント定義（.claude/agents/）作成
- [x] スラッシュコマンド（/forge, /forge-status, /forge-improve）作成

## 2026-07-07: 内部アルファ（M1）— パブリックベータに向けて
- [x] 設計計画書（docs/design_plan.md）作成
- [x] 品質管理チェックリスト（docs/quality_checklist.md）作成
- [x] ベータ公開準備チェックリスト（docs/beta_readiness_checklist.md）作成
- [x] E2Eテスト計画書（docs/test_plan.md）作成
- [x] ベータユーザー向けREADME.md作成
- [x] 監査指摘の修正（最小権限tools・status.json初期化のlast_updated・図の番号・インジェクション注意書き）

## 2026-07-07: E2Eテスト シナリオ1（ハッピーパス）実施 → 合格
- [x] kw-counterプロジェクトで /forge を実行し、spec→build→test→gate2→release→reportを完走
- [x] qa-testerが実機Chromiumで10項目検証、10/10 PASS・差し戻し0回
- [x] quality_checklist.md C-1 / test_plan.md シナリオ1 / beta_readiness_checklist.md を更新

## 2026-07-07: E2Eテスト シナリオ2（ゲート1差し戻し）実施 → 合格
- [x] kw-counter2でゲート1にて修正依頼→spec-interviewer再ヒアリング→spec.md更新→再提示→承認、の流れを確認
- [x] quality_checklist.md C-2 / test_plan.md シナリオ2 を更新

## 2026-07-07: E2Eテスト シナリオ5（/forge-improve振り分け）実施 → 合格
- [x] kw-counterへ絵文字関連のフィードバックを投入、improvement-analystが「仕様の問題」と判定→spec再ヒアリング→ゲート1再承認
- [x] code-builderが警告表示を実装、qa-testerが既存10＋新規6=16項目全PASS→ゲート2再承認
- [x] quality_checklist.md C-5 / test_plan.md シナリオ5 を更新（シナリオ3は今回もFAILが発生せず未検証のまま）

## 2026-07-08: E2Eテスト シナリオ3（テストFAIL差し戻し）実施 → 合格
- [x] calc-test3で自然発生を3回試すも全てPASS（code-builderが丸め処理等を自発実装）したため手動でコードを破壊する方式に切替
- [x] index.htmlの空欄=0処理を意図的に破壊→qa-testerがFAILと再現手順を正確に記録することを確認
- [x] code-builderがFAIL箇所1行のみ修正（無関係箇所への越権なし）、test_roundが1→2に更新されることを確認
- [x] 再テストで7項目全PASS（退行なし）を確認
- [x] quality_checklist.md C-3 / test_plan.md シナリオ3 を更新
- [x] calc-test3はゲート2を承認せず終了（テスト用途のため公開不要。`gate2_approved: false`のまま凍結、以後このプロジェクトは扱わない）

## 2026-07-08: E2Eテスト シナリオ4（中断・再開）実施 → 合格
- [x] resume-test1でspec承認・build完了後、phaseをtestにした時点で意図的に中断（qa-tester未実行）
- [x] 会話の経緯を持たない新規Agentに「/forge resume-test1」を実行させ、pipeline_status.jsonのphaseのみを根拠にspec/buildをやり直さずtestフェーズから再開することを確認
- [x] qa-testerとして受け入れ条件11項目を実機検証・全PASS→phaseがgate2に更新されることを確認
- [x] quality_checklist.md C-4 / test_plan.md シナリオ4 を更新
- [x] resume-test1もゲート2は承認せずクローズ（テスト用途のため公開不要）

## 2026-07-08: E2Eテスト シナリオ6（/forge-status表示）実施 → 合格
- [x] 記憶を持たない新規Agentにforge-status.mdの手順のみで実行させ、state配下5プロジェクト全件（kw-counter/kw-counter2/calc-test3/calc-test4/resume-test1）を正しく列挙・要約することを確認
- [x] test_round>3の警告判定が正しく機能する（該当プロジェクトなしと正しく判定）ことを確認
- [x] quality_checklist.md C-6 / test_plan.md シナリオ6 を更新
- [x] 副産物として発見: kw-counterのphaseが正典スキーマにない"done"という値になっていた → 下記ブロッカーに追加

## 2026-07-08: READMEの新規ユーザー視点監査 → 公開前クリーンアップ実施
- [x] 記憶を持たない新規Agentに「今クローンしたばかりのユーザー」としてREADME.mdの内容（前提条件・コマンド一覧・仕組み図・FAQ・LICENSE）を実態と突き合わせ検証 → 記述内容に矛盾なし
- [x] 発見: リポジトリにコミットが1件もなく、`state/`/`projects/`/`docs/specs/`/`reports/`にE2Eテスト残骸5件（calc-test3, calc-test4, kw-counter, kw-counter2, resume-test1）が未整理のまま残存していた
- [x] テスト残骸5件を削除し、各ディレクトリを`.gitkeep`のみのクリーンな状態に復元（テスト実施記録自体はtest_plan.md/quality_checklist.md/todo.mdに残っているため証跡は失われない）
- [ ] （任意・小）`docs/design_plan.md`等の開発者向け内部ドキュメントが一般ユーザーから見て文脈不明という指摘あり。`docs/internal/`への隔離 or README側に「開発者向け」の注記を検討

## ベータ公開ブロッカー（No-Go要因）
- [x] **E2Eテスト残りシナリオ**: シナリオ1〜6すべて合格（必須C-1〜C-4・推奨C-5〜C-6）
- [x] **forge.mdのphase更新漏れ修正**: 手順5に`phase`→`release`、手順6に`phase`→`report`（完走の最終状態）に更新する記述を追加。kw-counterの`pipeline_status.json`の`phase`も`"done"`→`"report"`に修正済み
- [x] **READMEの手順を新規クローン環境で再現確認**: 記述と実態の矛盾なし。テスト残骸の削除により公開用にクリーンな状態にした
- [ ] 初回コミット＆GitHub公開（ユーザー承認必須）
- [ ] フィードバック窓口（GitHub Issues）整備
