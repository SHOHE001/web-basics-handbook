# Antigravity（AGY）用：文章の書き直しの指示文

ローカルの Antigravity で、このハンドブックの文章を「内容はそのまま、自然な日本語」に書き直してもらうための手順と、エージェントに貼り付ける指示文です。

## 準備（PC で 1 回だけ）

```bash
git clone https://github.com/SHOHE001/web-basics-handbook.git
cd web-basics-handbook
git checkout claude/busy-pasteur-1bxgui
```

すでに clone 済みなら `git fetch origin` と `git checkout claude/busy-pasteur-1bxgui` と `git pull` を実行します。そのあと、このフォルダを Antigravity で開き、エージェントのチャットに下の「指示文」を貼り付けます。

## 指示文（ここから下をエージェントに貼り付ける）

このリポジトリは、非エンジニアの大学生向けの IT 学習ハンドブックです。次の対象ファイルの文章を、**内容はそのままに、日本語として自然で読みやすい文章に** 書き直してください。

### 対象ファイル

`chapters/`・`fe/`・`ap/`・`sc/` の下にある `README.md` すべて（`code/` フォルダの中は除く。全部で 41 ファイル）。1 ファイルずつ順番に作業してください。

### 守ること

- 事実・数値・用語・例・主張を変えない。情報を足さない、削らない、順番を入れ替えない
- 次の部分は **1 文字も変えない**:
  - 見出しの行（`#` で始まる行）と、`> Status:` の行
  - コードブロック（```` ``` ```` で囲まれた範囲）
  - インラインコード（`` ` `` で囲まれた部分）
  - リンクの URL 部分（`[文字](ここ)` の「ここ」）。リンクの文字の方は自然にしてよい
- Markdown の構造を保つ: 段落、箇条書きの項目数、番号付きリストの項目数、表の行数と列数
- `<mark>…</mark>` の数を変えない（中の言い回しは自然にしてよい）。`**太字**` の数も変えない
- `> [!CAUTION]` などの注意書きの行はそのまま残す
- 文体は、その章ですでに多い方（「です・ます」または「だ・である」）にそろえる
- 表の中の文も、短く自然な表現にしてよい。ただし列の区切り `|` の数は変えない

### 1 ファイル書き直すごとにやること

1. 次のコマンドで検査する（Python 3.11 以上。API キーは不要）

   ```bash
   python tools/rewrite_with_gemini.py --check
   ```

2. `[不合格]` が出たら、表示された理由（変わってしまった数字・見出し・記号など）を直して、もう一度検査する
3. 2 回直しても合格しないファイルは、次のコマンドで元に戻して、次のファイルに進む

   ```bash
   python tools/rewrite_with_gemini.py --check --revert
   ```

### 全部終わったら

1. もう一度 `python tools/rewrite_with_gemini.py --check` を実行し、`不合格 0 件` を確認する
2. 次のコマンドでコミットとプッシュをする

   ```bash
   git add chapters fe ap sc
   git commit -m "Rewrite chapter prose for natural Japanese (content unchanged)"
   git push origin claude/busy-pasteur-1bxgui
   ```

3. 最後に、合格したファイル数と、元に戻したファイルの一覧を報告する

## 終わったあと

プッシュが済んだら Claude Code のセッションに伝えてください。差分を読んで、意味が変わっていないかを人の目でも確認します。そのあと gen8 で次を実行すると、もの文読書室にも反映されます。

```bash
cd ~/web-basics-handbook && git pull && bash tools/deploy_reading_room.sh
```
