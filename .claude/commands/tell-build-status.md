# /tell-build-status — 進行中プロジェクトの状態確認

引数: $ARGUMENTS（省略可。project-nameを指定すればそのプロジェクトのみ表示）

## 動作内容

1. `state/*/pipeline_status.json` を全て読み込む（引数があれば該当プロジェクトのみ）
2. プロジェクトごとに以下を要約して表示する:
   - project名
   - 現在のフェーズ（spec / build / test / gate2 / release / report / improve）
   - test_roundの回数（3を超えていれば要注意として明記）
   - ゲート1・ゲート2の承認状況
   - 直近の成果物ファイルの更新日時
3. フェーズが `test` で `test_round` が3を超えているプロジェクトがあれば、
   improvement-analystの起動を提案する
4. 特に何もアクション不要なら、その旨を一言で伝える（過剰な提案をしない）
