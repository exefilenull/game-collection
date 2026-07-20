# Implementation Plan

- [ ] 1. Foundation: 共有データアクセスモジュールの抽出と統合
- [x] 1.1 データ取得・GitHub保存・エスケープ処理を共有モジュールに抽出する
  - hardware_detail.htmlのインライン実装(jsonFiles配列、saveToGitHub関数、escapeHtml関数)をscripts/data-store.jsに移動する
  - fetchAllCategoryData、saveToGitHub、escapeHtmlとして呼び出せる形にする
  - 観測可能な完了条件: scripts/data-store.jsを`<script>`で読み込み、ブラウザのdevtoolsから`DataStoreModule.escapeHtml()`を呼び出すと、移行前のインライン実装と同一のエスケープ結果が返る
  - _Requirements: 4.1_

- [x] 1.2 hardware_detail.htmlを共有モジュール経由に切り替える(既存動作を変更しない)
  - `<script src="scripts/data-store.js">`を追加し、既存のjsonFiles/saveToGitHub/escapeHtmlの呼び出しをDataStoreModule経由に置き換える
  - 重複していたインライン定義を削除する
  - 観測可能な完了条件: 既存のハードウェアページを開いた際に、テーブル・グラフ表示、収集済み/収集不要のクリック編集、保存ボタンによるGitHub保存が置き換え前と同じ挙動で動作する
  - _Requirements: 4.1_
  - _Boundary: HardwareDetailPage, DataStoreModule_

- [ ] 2. Core: お気に入り機能
- [ ] 2.1 お気に入りの表示と既定値処理を追加する
  - 各ゲーム行にお気に入り状態を示すセルを追加する
  - favoriteフィールドが存在しないゲームは非お気に入りとして表示する
  - 観測可能な完了条件: favoriteフィールドを持たない既存データのゲームが「お気に入りではない」表示になる
  - _Requirements: 1.1, 1.5_
  - _Boundary: HardwareDetailPage_

- [ ] 2.2 お気に入りのクリック切替と変更検知を追加する
  - お気に入りセルのクリックでcurrentGames内の該当エントリのfavorite値を反転し、表示を更新する
  - 既存のmarkChangedのロジックをfavoriteの変更も検知するよう拡張し、保存ボタンを活性化する
  - 観測可能な完了条件: お気に入りセルをクリックすると即座に表示が切り替わり、保存ボタンが有効になる
  - _Requirements: 1.2, 1.3_
  - _Boundary: HardwareDetailPage_

- [ ] 2.3 お気に入りが既存の保存フローで永続化されることを確認する
  - 保存実行時にcurrentGames全体(favoriteを含む)がDataStoreModule.saveToGitHub経由で対象JSONファイルに送信されることを確認する
  - 観測可能な完了条件: 保存成功後、変更検知の状態が他フィールドと同様にリセットされ、送信されたJSONにfavoriteが含まれる
  - _Requirements: 1.4, 4.3_
  - _Boundary: HardwareDetailPage, DataStoreModule_
  - _Depends: 1.2_

- [ ] 3. Core: ソート機能
- [ ] 3.1 ソートキー・順序の選択UIを追加する
  - タイトル/発売日/ジャンル/収集状況/お気に入りを選択できるコントロールと、昇順/降順を切り替えるコントロールを追加する
  - 観測可能な完了条件: 初期表示でソートUIが表示され、既定値(発売日昇順)が選択された状態になる
  - _Requirements: 2.1, 2.2_
  - _Boundary: HardwareDetailPage_

- [ ] 3.2 ソート適用と再描画を実装する
  - 各ソートキーの並び替えロジック(収集状況は複合スコアで判定)を実装し、選択変更時にビューを再構築してイベントを再バインドする
  - 観測可能な完了条件: ソートキーまたは順序を変更すると表示行が並び替えられ、並び替え後の行でもクリック編集が機能する
  - _Requirements: 2.3_
  - _Boundary: HardwareDetailPage_
  - _Depends: 3.1_

- [ ] 4. Core: 絞り込み機能
- [ ] 4.1 絞り込み条件の選択UIを追加する
  - 収集状況(すべて/収集済み/未収集)、クリア状況(すべて/クリア済み/未クリア)のセレクトと、収集不要のみ・お気に入りのみのチェックボックスを追加する
  - 観測可能な完了条件: 初期表示で絞り込みUIが表示され、既定で「絞り込み無し」が選択されている
  - _Requirements: 3.1_
  - _Boundary: HardwareDetailPage_

- [ ] 4.2 複合絞り込みの適用と空状態表示を実装する
  - 選択された条件をAND結合してcurrentGamesから表示用ビューを生成する(currentGames自体は変更しない)
  - 一致件数が0件の場合に空状態メッセージを表示する
  - 観測可能な完了条件: 複数条件を選択すると全条件を満たす行のみが表示され、条件を全解除すると全件表示に戻り、一致0件の組み合わせでは空状態メッセージが表示される
  - _Requirements: 3.2, 3.3, 3.4_
  - _Boundary: HardwareDetailPage_
  - _Depends: 4.1_

- [ ] 4.3 絞り込み中の編集継続とグラフ集計範囲を保証する
  - 絞り込み後のビューでもお気に入り/収集状況/収集不要のクリック編集が機能することを確認する
  - 収集率グラフが絞り込みに関わらずハードウェア全体を集計対象とすることを確認する
  - 観測可能な完了条件: 絞り込み適用中に行を編集してもcurrentGamesが正しく更新され、グラフの数値は絞り込み前後で変化しない
  - _Requirements: 3.7, 3.8_
  - _Boundary: HardwareDetailPage_
  - _Depends: 4.2_

- [ ] 5. Core: ブラウザ内設定の永続化
- [ ] 5.1 設定の読み書きヘルパーとフォールバックを実装する
  - ソートキー・順序・絞り込み条件を単一のブラウザローカルキーに保存/読み込みするヘルパーを実装し、ストレージ利用不可・不正値の場合は既定値にフォールバックする
  - 観測可能な完了条件: 保存キーに不正な値を書き込んだ状態でページを再読み込みしても既定のソート・絞り込み状態になる(エラーにならない)
  - _Requirements: 2.4, 2.5, 3.5, 3.6_
  - _Boundary: PreferenceStore_
  - _Depends: 3.1, 4.1_

- [ ] 5.2 ソート・絞り込みUIへの設定永続化を組み込む
  - ソート・絞り込みコントロール変更時に保存ヘルパーを呼び、ページ読み込み時に最初の描画前に復元ヘルパーを呼ぶ
  - 観測可能な完了条件: ソート・絞り込みを変更してページを再読み込みすると、直前の選択状態が復元される
  - _Requirements: 2.4, 2.5, 3.5, 3.6_
  - _Boundary: HardwareDetailPage, PreferenceStore_
  - _Depends: 5.1_

- [ ] 6. Integration & Validation
- [ ] 6.1 既存編集・保存機能の非破壊性を回帰確認する
  - 収集済み(新品/中古)・収集不要・クリア済みの表示・編集・保存が変更前と同じ挙動であることを確認する
  - お気に入りと既存フィールドの変更を1回の保存操作でまとめて保存できることを確認する
  - 観測可能な完了条件: 回帰確認チェックリストの全項目がPassし、複合変更の単一保存が成功する
  - _Requirements: 4.1, 4.2, 4.3_
  - _Depends: 2.3, 4.3, 5.2_

- [ ] 6.2 お気に入り・ソート・絞り込みの受け入れシナリオを実行する
  - design.mdのTesting Strategyに列挙された全シナリオ(お気に入り、各ソートキー・順序、各絞り込み条件・組み合わせ、空状態、設定復元)を実行する
  - 観測可能な完了条件: 全シナリオがPassし、不具合があれば修正のうえ再確認済みである
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_
  - _Depends: 6.1_

## Implementation Notes
- 1.2: `fetchAllCategoryData()`の返り値だけでは保存先ファイルパス(`sourceJsonFile`)を特定できないため、`DataStoreModule.CATEGORY_JSON_FILES`(パス一覧の定数配列)をdata-store.jsに追加公開した。design.mdのService Interfaceを更新済み。後続タスクでDataStoreModuleの返り値形状を前提にする場合はこの制約を踏まえること。
- リポジトリに`package.json`・テストランナーが存在しないため、各タスクの検証は`node --check`によるJS構文確認と、コードの手動トレースで行っている(design.mdのTesting Strategy参照)。
