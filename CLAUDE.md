# forge プロジェクト CLAUDE.md

グローバル設定（`~/.claude/CLAUDE.md`）も参照すること。

---

## プロジェクト概要

「作りたいものを伝えるだけで、要件定義→実装→テスト→デビュー（公開）→改善→報告」を
自動でこなすソフトウェアエンジニアリング・パイプライン。

複数の専門サブエージェントが**直列パイプライン**で連携する（対立・議論はさせない）。
各サブエージェントはClaude Codeの仕様上、他のサブエージェントを呼び出せないため、
**メインセッション自身が司令塔**となり、`/forge` コマンドでフェーズを順に進行させる。

```
ユーザー依頼
   ↓
① spec-interviewer（要件ヒアリング・opus）
   ↓ ══ゲート1: ユーザーが仕様書を承認══
② code-builder（実装・opus）
   ↓
③ qa-tester（動作確認・sonnet）
   ↓ ──FAILなら②へ差し戻し（最大3往復）
   ↓ ══ゲート2: ユーザーがデプロイを承認══
④ release-manager（公開・sonnet）
   ↓
⑤ progress-reporter（報告・sonnet）→ ユーザー
   ↓
（公開後フィードバック）→ ⑥ improvement-analyst（opus）
        ├─ バグ → ②へ
        └─ 仕様変更 → ①へ
```

詳細な引き渡しフォーマット・差し戻しルールは `shared/pipeline_rules.md` が正典。

---

## ディレクトリ構成

```
forge/
├── .claude/
│   ├── agents/       # 6体のサブエージェント定義
│   └── commands/     # /forge, /forge-status, /forge-improve
├── docs/specs/<project>/   # 仕様書（ゲート1の承認対象）
├── projects/<project>/     # 生成される各プロダクトの実体
├── state/                  # pipeline_status.json / test_report.md / improvement_plan.md
├── shared/pipeline_rules.md  # 引き渡しフォーマット・差し戻し上限・承認ルールの正典
├── reports/                # ユーザー向け報告
└── tasks/                  # todo.md / lessons.md
```

---

## 重要ルール（必ず遵守）

- **ゲート1（仕様承認）・ゲート2（デプロイ承認）を必ずユーザーに確認する**。
  承認なしに実装やpush/公開を進めない（グローバル規約「プランモード必須」「確認してから動く」の実装）
- 各サブエージェントは自分の役割の成果物だけを作る。越権しない
  （例: qa-testerはバグを直さない、release-managerは仕様変更をしない）
- テスト失敗時の差し戻しは最大3往復。それを超えたらimprovement-analystが原因切り分け
  （バグか仕様の問題かを判定し、code-builderかspec-interviewerのどちらに戻すか決める）
- 全サブエージェントは `effort: high` で運用する
- モデル割り当て: 難しい判断（要件確定・実装・原因切り分け）は `claude-opus-4-8`、
  定型作業（テスト実行・リリース手順・報告文作成）は `claude-sonnet-5`

---

## よく使うコマンド

```bash
# 新規プロジェクトを起動 / 既存プロジェクトを再開
/forge <project-name> "<作りたいものの説明>"

# 進行中の全プロジェクトの状態確認
/forge-status

# 公開後のフィードバックから改善サイクルを起動
/forge-improve <project-name> "<フィードバック内容>"
```

---

## タスク管理ルール

1. **プランモード必須**: ゲート1・ゲート2ではメインセッションが必ず計画・変更内容を提示し、承認を得る
2. **todo.md**: 作業開始時に `tasks/todo.md` を更新、完了したら即マーク
3. **lessons.md**: 修正・指摘を受けたら `tasks/lessons.md` にルールを追記
