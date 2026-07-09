# /tell-build — 新規プロジェクトの起動・再開

引数: $ARGUMENTS

## 使い方
```
/tell-build <project-name> "<作りたいものの説明>"
```
project-nameが引数になければユーザーに確認する。

## 動作内容

メインセッション自身が司令塔となり、`shared/pipeline_rules.md` に従って
以下のフェーズを順に進行させる。各フェーズは対応するサブエージェント
（Agentツールで `subagent_type` 指定、foreground実行）に担当させ、
成果物を検収してから次フェーズへ渡す。

### 手順

1. `state/<project-name>/pipeline_status.json` の有無を確認する
   - 無ければ新規プロジェクト。`state/<project-name>/` を作成し、
     `{"project": "<project-name>", "phase": "spec", "test_round": 0, "gate1_approved": false, "gate2_approved": false, "last_updated": "<今日の日付 YYYY-MM-DD>"}` を書き込む
   - あれば既存プロジェクト。記録されている `phase` から再開する

2. **フェーズ: spec** — `spec-interviewer` エージェントを起動し、ユーザーの依頼内容を渡す。
   `docs/specs/<project-name>/spec.md` ができたら、内容をユーザーに提示し、
   **ゲート1として明示的に承認を求める**（AskUserQuestion等で）。
   承認されるまで次に進まない。修正依頼があればspec-interviewerに戻す。

3. **フェーズ: build** — 承認済み仕様書を渡して `code-builder` エージェントを起動する。
   完了したら `pipeline_status.json` の `phase` を `test` に更新する。

4. **フェーズ: test** — `qa-tester` エージェントを起動する。
   - 全PASS → `phase` を `gate2` に更新し、手順5へ
   - FAILあり → `test_round` を+1し、`code-builder` へ差し戻す（手順3へ）
   - `test_round` が3を超えたら `improvement-analyst` を起動し、
     バグなら code-builder へ、仕様の問題なら spec-interviewer へ（ゲート1からやり直し）差し戻す

5. **ゲート2（デプロイ承認）** — `release-manager` エージェントに実行計画（何を・どこへ・戻し方）を
   作らせ、内容をユーザーに提示して明示的に承認を求める。
   承認なしに公開・push・課金操作を実行してはならない。承認後、release-managerに実行させ、
   完了したら `pipeline_status.json` の `phase` を `release` に更新し、手順6へ進む。

6. **フェーズ: report** — `progress-reporter` エージェントを起動し、`reports/<project-name>_<日付>.md` を
   作らせ、その内容をチャットにも提示する。完了したら `pipeline_status.json` の `phase` を `report` に更新する
   （これが完走の最終状態。`shared/pipeline_rules.md` のスキーマ外の値を書き込んではならない）。

### 注意
- 各エージェントの入出力ファイル形式は `shared/pipeline_rules.md` を正典とする
- ゲート1・ゲート2をスキップして先のフェーズに進んではならない
- 途中で中断された場合は `/tell-build <project-name>` を再実行すれば `pipeline_status.json` から再開できる
