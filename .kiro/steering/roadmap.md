# Roadmap

## Overview
プレイ済み・お気に入り・ソート・絞り込み機能を静的サイト(hardware_detail.html)に追加し、あわせて全ハードウェアを横断したゲームデータの重複検出・削除ツールを追加する。既存のGitHub Pages(実体はNetlifyホスティング)+ Netlify Function経由でGitHub Contents APIにコミットする保存パターンを継続する。

## Approach Decision
- **Chosen**: Approach B — 既存のvanilla JS構成を維持しつつ、データ読み込み・GitHub保存・エスケープ処理などの共通ロジックを`scripts/`以下の共通モジュールに切り出し、`hardware_detail.html`と新規`duplicates.html`から共有する。
- **Why**: 重複削除specは複数JSONファイルを横断して読み込み・保存する必要があり、共通化しておくことで実装・保守コストを下げられる。ビルドステップ不要で既存のGitHub Pages+Netlify Functions構成にそのまま乗せられる。
- **Rejected alternatives**:
  - A(各ファイルに個別実装): 重複コードが増え続け保守性が低下するため却下。
  - C(フレームワーク/ビルドツール導入): 既存のシンプルな静的構成に対して過剰であり、GitHub Pages配信のシンプルさを損なうため却下。

## Scope
- **In**: `hardware_detail.html`へのお気に入り機能・ソート機能・絞り込み機能の追加、全ハードウェア横断の重複ゲーム検出・削除ツールの追加、上記に必要な共通JSモジュールの切り出し
- **Out**: `index.html`自体への機能追加(hardware_detail.htmlのみ対象と確定済み)、プレイ済み専用の新規データフィールド追加(既存の`collected_new`/`collected_old`を流用する方針で確定済み)、認証・アクセス制御の追加、ビルドツール/フレームワークの導入

## Constraints
- GitHub Pages(実体はNetlifyホスティング)+ Netlify Functions + GitHub Contents APIによる保存パターンを継続すること
- ビルドステップを追加しない(静的HTML/JS構成を維持)
- Netlify Functions無料枠の同期実行タイムアウト(既定10秒)を考慮し、複数ファイル更新時はSHA取得(GET)を並列化・PUTのみ逐次化する設計とすること
- GitHub Contents APIへの書き込みは二次レート制限(900ポイント/分、書き込み1回5ポイント)内に収まるよう設計すること

## Boundary Strategy
- **Why this split**: `hardware_detail.html`の表示・編集機能拡張(お気に入り/ソート/絞り込み)と、全ハードウェア横断のデータ整合性ツール(重複削除)は、UI画面・データスコープ・保存対象ファイル数が明確に異なるため、別specとして分離しレビュー境界を明確にする。
- **Shared seams to watch**: 両specとも同じGitHub保存パターン(Netlify Function経由のContents API PUT)と共通JSモジュール(`scripts/`以下)を利用するため、共通モジュールのAPIを変更する場合は両specに影響が及ぶ。

## Specs (dependency order)
- [x] game-favorites-filters -- hardware_detail.htmlにお気に入り機能・ソート機能・絞り込み機能を追加し、GitHub保存に対応する。Dependencies: none (完了。本番デプロイ後に見つかった関連バグ修正・仕様調整も反映済み)
- [ ] duplicate-game-cleanup -- 全ハードウェア・全カテゴリを横断してゲームタイトルの重複を検出し、選択削除してGitHubに保存するツールを追加する。Dependencies: none

## Phase 2: プレイ状況追跡・攻略メモ生成(2026-07-22 discovery)

### Overview
「クリア済み」の二値管理を「プレイ状況」(未プレイ/プレイ中/全クリア)の3状態管理に置き換え、あわせてプレイ状況が変化したゲームについて、既存の手書き攻略メモ(`C:\Users\T\Desktop\Game`配下の`【ハード略称】タイトル.md`形式)と同じ構成のMDファイルをAIエージェントが調査・生成できるようにする。ライブサイトからのリアルタイムAI呼び出しは追加課金(Anthropic API等の従量課金)が必要になるため不採用とし、Claude Codeなど手元のAIセッションでオフライン・バッチ生成する運用とする。

### Approach Decision(Phase 2)
- **Chosen**: プレイ状況のUI/データ変更(ライブサイト)と、MD生成手順・ツール(オフライン、SKILL.md文書化)を2つのspecに分離する。MD生成はどの特定AIプロバイダにも依存しない、SKILL.md形式の再利用可能な手順として文書化する。
- **Why**: ライブサイト上のAI API呼び出しは追加課金・APIキー管理・新たな公開エンドポイントのセキュリティリスク(update.jsで既に指摘した認証欠如と同種の問題)を伴うため、コスト・リスクの観点からオフライン運用を選択。UI変更(ブラウザで動くコード)とMD生成手順(AIエージェントへの指示書)は実行環境・成果物の性質が全く異なるため、別specとして境界を分ける。
- **Rejected alternatives**:
  - ライブサイトでのリアルタイムAI生成: 追加課金が必須になり、ユーザーが「今のプランでは不可」と判断したため却下。
  - 1つのspecにまとめる: UI変更(ブラウザJS)とAI生成手順(オフラインskill/ドキュメント)は成果物の種類が異なりすぎるため、レビュー境界を明確にするために分離。

### Scope(Phase 2)
- **In**: 「クリア済み」列→「プレイ状況」列(未プレイ/プレイ中/全クリア)への変更とGitHub保存、既存game_clear/*.html方式からMDファイル参照方式への置き換え、AIエージェント向けのMD生成手順(SKILL.md)、対象レコード抽出・生成先配置・レコードとの紐付けの仕組み
- **Out**: ライブサイト上でのリアルタイムAI API呼び出し、特定AIプロバイダへの依存実装、生成されたMD内容の正確性保証、sort/filter機能へのプレイ状況統合(要望があれば別途検討)

### Constraints(Phase 2)
- ライブサイト(hardware_detail.html)側は既存のGitHub Pages + Netlify Functions + GitHub Contents API保存パターンを継続し、新たな外部API呼び出しを追加しない
- MD生成はオフライン(Claude CodeなどのAIセッション)で行い、特定プロバイダのAPIに依存する実装をしない
- 新規MDファイルは既存の`C:\Users\T\Desktop\Game`のファイル構成(見出し・目次・折りたたみセクション・タイトルのカラーコード)を踏襲する。タイトルカラーコードは既定で黒(#000000)
- 対応するMDファイルが既に存在するレコードには生成処理を行わない(冪等性)

### Boundary Strategy(Phase 2)
- **Why this split**: `play-status-tracking`はブラウザ上で動くUI/データ変更(既存specと同じ技術スタック)、`walkthrough-notes-generation`はAIエージェント向けの手順書・オフラインツール(全く異なる実行環境)であり、責任範囲・レビュー観点が明確に異なるため分離する。
- **Shared seams to watch**: `walkthrough-notes-generation`は`play-status-tracking`が定義するデータフィールド(プレイ状況・MDファイル参照)を前提に動作するため、そのフィールド仕様を変更する場合は両specに影響が及ぶ。

### Specs (dependency order, Phase 2)
- [x] play-status-tracking -- hardware_detail.htmlの「クリア済み」列をプレイ状況(未プレイ/プレイ中/全クリア)に変更し、GitHub保存に対応する。既存game_clear/*.html方式を置き換える。Dependencies: none (完了。最終検証GO)
- [ ] walkthrough-notes-generation -- 既存の手書き攻略メモと同じ構成のMDファイルをAIエージェントがオフラインで生成できるよう、SKILL.mdと対象抽出・配置の仕組みを整備する。Dependencies: play-status-tracking
