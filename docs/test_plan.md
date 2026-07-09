# E2Eテスト計画書

**目的**: TellBuildパイプラインが設計どおりに完走すること・ゲートと差し戻しが機能することを、
実際のプロジェクトで検証する（`quality_checklist.md` C群に対応）。

**実施方法**: `tell-build` ディレクトリでClaude Codeを起動し（サブエージェントはtell-build配下でのみ有効）、
以下のシナリオを順に実行する。結果は本ファイル末尾の記録表に記入する。

---

## テスト用プロジェクト（推奨）

小さく・外部依存なく・成果が目で見えるものにする。推奨:

**`kw-counter`** — Google広告の文字数カウンター（CLI）
「テキストを渡すと全角2B/半角1B換算でバイト数を数え、ヘッドライン30B/説明文90Bの超過判定をする」
※実業務（ppc_affiliate）でそのまま使える上に、受け入れ条件が明確でテストしやすい。

---

## シナリオ1: ハッピーパス完走（C-1）

1. `/tell-build kw-counter "広告文の全角半角バイト数カウンター"` を実行
2. spec-interviewerの質問に答え、spec.mdが生成されることを確認
3. ゲート1で承認 → code-builderが `projects/kw-counter/` に実装することを確認
4. qa-testerが受け入れ条件を**実際に実行して**判定することを確認（コードレビューだけならNG）
5. 全PASS後、ゲート2で承認（公開先は「ローカルのみ」でOK。push不要）
6. progress-reporterの報告が専門用語なしで出ることを確認

**合格基準**: spec→build→test→gate2→release→report が手動介入なし（ゲート承認以外）で進む。

## シナリオ2: ゲート1差し戻し（C-2）

1. ゲート1で承認せず「受け入れ条件に○○を追加して」と修正依頼を出す
2. spec-interviewerが再ヒアリングし、spec.mdが更新されることを確認
3. 再提示→承認で先に進むことを確認

**合格基準**: 修正依頼でcode-builderに進まず、spec.md更新→再承認の流れになる。

## シナリオ3: テストFAIL差し戻し（C-3）

1. 意図的にFAILさせる（例: spec.mdに「存在しない機能」の受け入れ条件を1つ混ぜてからビルドさせる、
   または生成コードの1箇所を手で壊してからqa-testerを走らせる）
2. qa-testerがFAILと再現手順をtest_report.mdに書くことを確認
3. code-builderがFAIL項目**のみ**修正することを確認（無関係な箇所を触ったらNG）
4. `pipeline_status.json` の `test_round` が+1されていることを確認

**合格基準**: FAIL→差し戻し→修正→再テスト→PASSのループが1周する。

## シナリオ4: 中断・再開（C-4）

1. シナリオ1の途中（buildフェーズ完了時点など）でセッションを終了する
2. 新しいセッションで `/tell-build kw-counter` を実行
3. `pipeline_status.json` の `phase` から正しく再開されることを確認（最初からやり直しになったらNG）

**合格基準**: 記録済みフェーズの続きから再開する。

## シナリオ5: /tell-build-improve 振り分け（C-5・推奨）

1. 完走後に `/tell-build-improve kw-counter "半角カナが1Bで数えられるか不安"` を実行
2. improvement-analystが「バグ or 仕様の問題」を根拠つきで判定することを確認
3. 承認後、正しい差し戻し先（code-builder / spec-interviewer）に進むことを確認

## シナリオ6: /tell-build-status 表示（C-6・推奨）

1. `/tell-build-status` を実行し、kw-counterのフェーズ・test_round・ゲート状況が正しく表示されることを確認

---

## 観察ポイント（全シナリオ共通）

- [ ] エージェントが越権していないか（qa-testerが直す・code-builderが仕様外を作る等）
- [ ] `pipeline_status.json` が各フェーズ遷移で更新されているか
- [ ] 成果物ファイルのパス・形式が `shared/pipeline_rules.md` と一致しているか
- [ ] ゲートでAskUserQuestion等による**明示的な**承認が求められるか（「進めますね」はNG）

---

## 実施記録

| 日付 | シナリオ | 結果 | 発見した問題（tasks/todo.mdにも転記） |
|---|---|---|---|
| 2026-07-07 | 1（kw-counter） | ✅ 合格。spec→build→test→gate2→release→report が手動介入（ゲート承認）以外なしで完走。qa-testerはコードレビューではなく実機Chromiumで10項目を実行検証、10/10 PASS・差し戻し0回 | なし |
| 2026-07-07 | 2（kw-counter2） | ✅ 合格。ゲート1で修正依頼を出したところ承認せずspec-interviewerに戻り再ヒアリング→spec.md更新→再提示→承認、の流れを確認 | なし |
| 2026-07-08 | 3（calc-test3） | ✅ 合格。自然発生では3回ともFAILせず（code-builderが小数丸め処理等を自発的に実装したため）、test_plan.mdの代替手段「生成コードを手で壊す」に切替。index.htmlの`parseInput()`空文字判定を`0`→`null`に手動で改変し、qa-testerがFAILと再現手順（実機Playwright検証）をtest_report.mdに正確に記録することを確認。code-builderへ差し戻したところ、FAIL箇所の1行のみを修正し他のPASS項目・ファイルには一切触れず（越権なし）。test_roundは1→2に更新。再テストで7項目全PASS（退行なし）を確認 | なし |
| 2026-07-08 | 4（resume-test1） | ✅ 合格。spec承認・build完了後、phaseを`test`にした時点で意図的に中断（qa-tester未実行）。この会話の経緯を一切持たない新規Agentに「`/forge resume-test1`」を実行させたところ、`pipeline_status.json`のphaseのみを根拠にspec/buildをやり直さずtestフェーズから再開し、qa-testerとして受け入れ条件11項目を実機検証・全PASS→phaseを`gate2`に更新することを確認 | なし |
| 2026-07-07 | 5（kw-counter、絵文字警告フィードバック） | ✅ 合格。improvement-analystが「仕様の問題」と根拠つきで判定→spec-interviewerへ差し戻し（phase=spec, gate1_approved=false）→再ヒアリング→ゲート1再承認→code-builder実装→qa-testerが既存10＋新規6=16項目全PASS→ゲート2再承認→報告書更新 | なし |
| 2026-07-08 | 6（/forge-status） | ✅ 合格。記憶を持たない新規Agentにforge-status.mdの手順のみを渡して実行させたところ、state配下の全5プロジェクト（kw-counter/kw-counter2/calc-test3/calc-test4/resume-test1、うちcalc-test4はtodo.md未記載の過去テスト残骸）を正しく列挙・要約。test_round>3の判定も正しく「該当なし」。想定外データ（kw-counterのphase値が正典スキーマ外の"done"）にも、ファイルを書き換えず注記のみで対応する適切な挙動を確認 | forge.mdの手順5・6（ゲート2承認後〜report完了後）に`phase`更新の明記がなく、正典スキーマ（release/report）にない"done"という値が過去に書き込まれていた。forge.mdの手順4までは「phaseを◯◯に更新する」と明記があるのに手順5・6にはない、という記述の抜け漏れが原因 |
