# /forge-improve — 公開後フィードバックからの改善サイクル

引数: $ARGUMENTS

## 使い方
```
/forge-improve <project-name> "<フィードバック内容・不具合報告>"
```
project-nameかフィードバック内容が引数になければユーザーに確認する。

## 動作内容

1. `state/<project-name>/pipeline_status.json` を確認する（無ければプロジェクトが存在しない旨を伝えて終了）
2. `improvement-analyst` エージェントを起動し、フィードバック内容・`state/<project-name>/test_report.md`・
   `docs/specs/<project-name>/spec.md` を渡して原因判定させる
3. `state/<project-name>/improvement_plan.md` ができたら、判定結果（バグ or 仕様の問題）と
   差し戻し先をユーザーに提示し、進めてよいか確認する
4. 承認されたら:
   - バグ → `code-builder` を起動（`pipeline_status.json` の `phase` を `build` に、`test_round` を0にリセット）
   - 仕様の問題 → `spec-interviewer` を起動（`phase` を `spec` に戻し、`gate1_approved` を false に。
     ゲート1からやり直しになる旨をユーザーに明確に伝える）
5. 以降は `/forge <project-name>` と同じフローで進行する
