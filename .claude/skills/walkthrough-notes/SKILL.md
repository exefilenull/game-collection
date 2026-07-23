---
name: walkthrough-notes
description: Generate a walkthrough note HTML for a game and link it to its data record
allowed-tools: Read, Write, Bash, Glob, Grep, WebSearch, WebFetch, AskUserQuestion
argument-hint: <ゲームタイトル>, <ハード名>
---

# walkthrough-notes Skill

## Role
これは`game_notes/SKILL.md`(プロバイダ非依存の手順書)をClaude Codeから`/`コマンドで呼び出すための薄いラッパーです。HTML構成・改行規則(`<br>`方式、見出しレベル別区切り本数)・タイトルのカラーコード規則・文体模倣の指針といった実体規則は`game_notes/SKILL.md`側にあり、このスキルでは重複させず、毎回そちらを読みに行くこと(`game_notes/SKILL.md`が唯一の正とし、このラッパーとは独立に更新されうる)。

## Input
`$ARGUMENTS`はゲームを特定する自由形式の文字列(例: `鉄拳3,ps1`、`スーパーマリオブラザーズ3 ファミコン`)。ハード名はカジュアルな略称・英略記(`ps1`, `PS1`, `switch`等)で入力されることを想定し、`data/*.json`内の実際の`hardware_name`キー(例: `PlayStation1`)と柔軟に照合すること。

## Execution Steps

### Step 1: 対象レコードの特定
- `data/*.json`全12ファイルを検索し、`$ARGUMENTS`のタイトル部分と一致する`soft_title`を持つレコードを探す(末尾の`☑`/`★`/`☆`等の装飾記号の有無は無視して照合してよい)
- **タイトルが一致するレコードが2件以上ヒットした場合(ハード違いの同名タイトル・続編違いなど)、ハード名の入力から自動的に絞り込んで単独候補にできる場合であっても、絶対に自動判定だけで確定しないこと。必ずAskUserQuestionで候補を全て提示し(category/hardware/soft_titleが分かるように)、ユーザーに選んでもらってから次のステップに進む。** ハード名の入力はあくまで選択肢を絞る・並び替えるための参考情報として使ってよいが、それ自体を「確定」の根拠にしない
- 候補が見つからない場合は、該当レコードが無い旨をユーザーに伝えて処理を中断する
- 該当レコードに既に`walkthrough_note_path`が空文字列以外の値で設定されている場合は、再生成せず「既に紐付け済みです」と伝え、既存パスを提示して終了する(冪等性)

### Step 2: 生成規則の読み込み
- `game_notes/SKILL.md`を全文読む
- 対象ゲームと近いジャンル・ハードの既存実例を`game_notes/`配下から2〜3件読み、文体・構成の参考にする

### Step 3: 調査してHTMLを作成する
- 対象ゲームについて調査し(一般知識、利用可能であればWebSearch)、`game_notes/SKILL.md`が定める構成(ステージ・アイテム等、ゲームに応じたセクション)を作成する
- 出力先は`game_notes/{category}/{hardware}/{title}.html`(`title`は対象レコードの`soft_title`から末尾の装飾記号を除いたもの。`game_notes/SKILL.md`のパス規則に従う)
- `game_notes/SKILL.md`の全ルールを厳守する: `white-space: pre-line`を使わない、改行は明示的な`<br>`、見出しレベル別の区切り本数(見出し大=3・見出し中=2・見出し小以下=1)、色指定がある場合はタイトル全体を`<span>`で囲む

### Step 4: レコードに紐付ける
- `python tools/link_walkthrough_note.py --file <data/*.jsonのパス> --hardware <hardware名> --title <完全一致するsoft_title> --path <作成したnoteのパス>`を実行する
- 成功(スキップやエラーではない)ことを確認する

### Step 5: 報告と次のアクションの確認
- 生成したファイルのパスと、作成したセクションの概要をユーザーに報告する
- コミット・プッシュするかどうかをユーザーに確認する(このプロジェクトでは、コミット・プッシュは作業の節目で必ず確認する。無断で行わない)

## Constraints
- `soft_title`の一致に自信が持てない場合は推測せず、AskUserQuestionでユーザーに確認する
- 既に`walkthrough_note_path`が設定されているレコードには絶対に上書き生成しない
- このスキルの実行中に`tools/find_missing_walkthrough_notes.py`・`tools/link_walkthrough_note.py`・`game_notes/SKILL.md`自体を変更しない(これらは本specで確立された安定した成果物であり、本スキルの対象外)
- 生成する攻略内容の正確性は保証しない(このspecの既定スコープ通り)。構造上の正しさ(HTML構成・改行規則等)を優先する
