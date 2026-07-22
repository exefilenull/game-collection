# Implementation Plan

- [ ] 1. 表示: クリア済み列からの置き換え
- [x] 1.1 プレイ状況セルの表示を追加し、旧クリア済みリンクを削除する
  - `<thead>`の「クリア済み」列見出しを「プレイ状況」に変更する
  - `displayTable`内の`clearedCell`生成ロジック(`game_clear/*.html`へのリンク)を削除し、`play_status`の値に応じたラベル(未プレイ/プレイ中/全クリア)を表示するセルに置き換える。値が未設定または既知の3値以外の場合は「未プレイ」として表示する
  - 観測可能な完了条件: `game_clear/*.html`へのリンクがどのゲーム行にも表示されず、`play_status`が未設定のゲームが「未プレイ」と表示される
  - _Requirements: 1.1, 1.3, 4.1, 4.2_

- [x] 1.2 攻略情報リンクセルの表示を追加する
  - `<thead>`に「攻略情報」列見出しを追加する
  - `walkthrough_note_path`が設定されている場合のみ、そのパスへのリンクをセルに表示する。未設定または空文字の場合はセルに何も表示しない
  - 観測可能な完了条件: `walkthrough_note_path`を持つゲームにはリンクが表示され、持たないゲームのセルは空であることを確認できる
  - _Requirements: 3.1, 3.2_

- [ ] 2. Core: プレイ状況の循環編集
- [x] 2.1 プレイ状況セルのクリックで循環編集を実装する
  - プレイ状況セルのクリックで、`currentGames`内の該当エントリの`play_status`を「未プレイ→プレイ中→全クリア→未プレイ」の順で1段階進め、表示を更新する(既存の`.toggle-favorite`等と同じ検索・更新パターンに従う)
  - このクリックハンドラは`walkthrough_note_path`に一切触れない(design.md Key Decisions: プレイ状況の変更で攻略メモへのリンクが消えてはならない)
  - 観測可能な完了条件: プレイ状況セルをクリックするたびに表示ラベルが固定順で1段階ずつ切り替わり、同じ行の攻略情報セルの表示は変化しない
  - _Requirements: 1.2, 3.3_
  - _Boundary: HardwareDetailPage_

- [x] 2.2 変更検知(markChanged)にplay_statusを追加する
  - `originalPlayStatus`スナップショットを追加し、`originalFavorite`と同じタイミング(初回ロード時・保存成功時)で初期化・更新する
  - `markChanged()`が`play_status`の差分も検知し、保存ボタンを活性化するよう拡張する
  - 観測可能な完了条件: プレイ状況を変更すると保存ボタンが有効化され、元の値に戻すと(他に差分が無ければ)無効化される
  - _Requirements: 1.4_
  - _Boundary: HardwareDetailPage_

- [ ] 3. Integration: 保存フローへの統合確認
- [x] 3.1 プレイ状況が既存の保存フローでまとめて保存されることを確認する
  - 保存実行時に`currentGames`全体(`play_status`を含む)が`DataStoreModule.saveToGitHub`経由で対象JSONファイルに送信されることを確認する。design.mdの決定通り、既存の保存経路(`sourceCategoryData`の再構築・送信ロジック)自体には変更を加えない
  - 観測可能な完了条件: 送信されるJSONペイロードに変更後の`play_status`が含まれ、保存成功後に変更検知の状態がリセットされる
  - _Requirements: 2.1_
  - _Boundary: HardwareDetailPage, DataStoreModule_
  - _Depends: 2.2_

- [ ] 4. Integration & Validation
- [ ] 4.1 既存編集・保存機能の非破壊性を回帰確認する
  - 収集状況(新品/中古)・収集不要・お気に入り・ソート・絞り込みの表示・編集・保存が、本機能追加前と同じ挙動であることを確認する
  - 観測可能な完了条件: 回帰確認チェックリストの全項目がPassする
  - _Requirements: 2.2, 4.3_
  - _Depends: 3.1_

- [ ] 4.2 攻略メモリンクの持続性とプレイ状況循環の受け入れシナリオを実行する
  - プレイ状況を複数回クリックして循環させても攻略情報リンクの表示が変化しない(消えない)ことを確認する
  - design.mdのTesting Strategyに列挙された全シナリオを実行する
  - 観測可能な完了条件: 全シナリオがPassし、不具合があれば修正のうえ再確認済みである
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3_
  - _Depends: 4.1_

## Implementation Notes
- 2.1: `getPlayStatusLabel`(新規)とタスク1.1由来の`displayTable`内インラインswitch文が、プレイ状況ラベル変換ロジックをほぼ重複して持っている(レビューでSuggestion指摘、ブロッキングではない)。将来的に触る機会があれば`getPlayStatusLabel`に統一してよい。
