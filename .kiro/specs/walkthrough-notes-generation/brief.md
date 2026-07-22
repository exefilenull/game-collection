# Brief: walkthrough-notes-generation

## Problem
ゲームをプレイ中・クリア済みにした際、そのゲームの攻略メモを毎回手動で書くのは手間がかかる。既存の手書きメモ(`C:\Users\T\Desktop\Game`配下)と同じ構成でAIに調査・下書きさせたいが、ライブサイト上でリアルタイムにAI APIを呼ぶには追加課金(Anthropic API等の従量課金アカウント)が必要であり、現状の契約では賄えない。

## Current State
`C:\Users\T\Desktop\Game`には`【ハード略称】タイトル.md`という命名のMDファイルが多数手動作成されている(構成: タイトル見出し(一部`<span style="color:#XXXXXX">`でカラーコード付き)、目次、`<details open><summary>`による折りたたみ式セクション、箇条書きの攻略メモ・個人の感想)。

2026-07-22、このうち8件を手作業でHTML形式に変換し、`play-status-tracking` specが定義する`game_notes/{category}/{hardware}/{title}.html`のディレクトリ構成に配置し、対応するレコードに`walkthrough_note_path`を設定して紐付け済み(元の`.md`ファイルは`Desktop\Game`にそのまま残置、非破壊)。**この8件のHTML出力が、本specでAIエージェントが生成すべき最終フォーマットの実例そのものである**(`game_notes/`配下を直接参照できる)。GitHub Pagesは`.md`をレンダリングしないため、`.html`形式を採用した(詳細は下記Constraints参照)。

これ以外のレコード(プレイ状況が未プレイ以外だが攻略メモがまだ無いもの)については、生成・配置・紐付けの自動化された仕組みがまだ存在しない。

## Desired Outcome
- プレイ状況が「未プレイ」以外になっていて、対応する攻略メモ(HTML)がまだ存在しないレコードを洗い出せる
- AIエージェント(Claude Codeに限らず、他のAIツールでも使えるプロバイダ非依存の手順)が、ハード名とゲームタイトルを元に調査し、`game_notes/`配下の既存8件と同じ構成(タイトル見出し・目次・`<details><summary>`による折りたたみセクション)のHTMLファイルを生成できる
- 生成する文体は既存メモの文体(個人の感想を含むトーン)をできる範囲で模倣する
- タイトルのカラーコードは、既存メモに色指定が無い場合は既定で黒(`#000000`)にする
- 生成先は`game_notes/{category}/{hardware}/{title}.html`(既存8件と同じ構成)に配置し、各レコードの`walkthrough_note_path`から参照できるようにする
- 対応する攻略メモ(HTML)が既に存在するレコードには生成処理を行わない(冪等性)
- 上記の調査・生成手順をSKILL.md(または同等のドキュメント)として文書化し、他のAIエージェントからも再利用できるようにする

## Approach
生成手順・期待するHTMLファイル構成(見出し規則、目次規則、折りたたみセクション規則、カラーコードのデフォルト、`<head>`のCSS等)を定義したSKILL.mdを作成する。テンプレートの参照元は`game_notes/`配下に既に存在する8件の実例(2026-07-22に手動変換済み)とする。あわせて、「プレイ状況が未プレイ以外かつ攻略メモ未生成」のレコードを列挙する手段(スクリプトまたは手順書内の指示)を用意する。実際の生成はAIエージェント(Claude Codeなど)がこのSKILL.mdに従って手元のセッションでオフライン実行し、生成物をリポジトリにコミットする運用とする。

## Scope
- **In**: HTML生成手順・期待するファイル構成を定義するSKILL.md、対象レコード抽出手段、生成先ディレクトリへの配置ロジック、生成済みHTMLファイルとレコード(`walkthrough_note_path`)との紐付け更新
- **Out**: ライブサイトでのリアルタイムAI呼び出し(コスト都合により対象外)、生成したHTML内容の正確性保証(AIが調査して書く内容は目安であり、事実確認は保証しない)、特定AIプロバイダのAPIに直接依存する実装、`play_status`フィールド自体のUI・保存(→`play-status-tracking`)、Markdownからの変換処理(2026-07-22時点で対象8件は変換済み、以降は最初からHTMLで生成するため変換ロジックは不要)

## Boundary Candidates
- SKILL.md(調査手順・出力HTMLフォーマット・カラーコード既定値などの定義)
- 対象抽出ロジック(未プレイ以外かつ攻略メモ未生成のレコードの特定方法)
- 生成・配置ロジック(ファイルパスの決定規則・書き込み・レコード側`walkthrough_note_path`の更新)

## Out of Boundary
- `play_status`フィールドの追加・UI・保存(→`play-status-tracking` spec、実装済み)
- ライブサイトでのAI API呼び出し・関連するNetlify Function追加

## Upstream / Downstream
- **Upstream**: `play-status-tracking` specで定義される`play_status`フィールドおよび`walkthrough_note_path`参照の仕組み(実装済み)。`game_notes/`配下の既存8件(実例・テンプレート参照元)
- **Downstream**: なし(現時点で本spec完了後に依存する後続作業は未定)

## Existing Spec Touchpoints
- **Extends**: なし(新規spec)
- **Adjacent**: `play-status-tracking`(`walkthrough_note_path`参照の仕組みを共有する隣接spec、実装済み)

## Constraints
- 特定のAIプロバイダ(Claude API等)のAPIに直接依存する実装をしない。オフライン/バッチでAIエージェントが手順書に従って実行する運用とする
- 出力形式は**HTML**とする(`.md`ではない)。理由: サイトはGitHub Pagesで配信されており`.md`ファイルは整形レンダリングされず生テキスト表示になってしまうため、「攻略情報」リンクをクリックした際にブラウザでそのまま意図通り表示されるよう、既存の`game_clear/*.html`と同系統のスタイル・構成を持つ完全なHTML文書として生成する
- 既存の`C:\Users\T\Desktop\Game`のメモ構成(見出し・目次・折りたたみセクション・タイトルのカラーコード)を踏襲する。タイトルのカラーコードは、指定が無い場合は既定で黒(`#000000`)とする
- 本文中の改行は必ずブラウザで可視化されるようにする。`<body>`に`white-space: pre-line;`を含める(2026-07-22、8件の手動変換時に、元メモの「行末2スペース」というMarkdown改行記法をそのままコピーしただけの箇所で本文が1行に結合されてしまう不具合が発生し、このCSSで修正済み。新規生成時も同じ問題が起きないよう、`<br>`変換に頼るだけでなくこのCSSを必ず含めること)
- 対応する攻略メモ(HTML)が既に存在するレコードには生成処理を行わない(冪等性)
