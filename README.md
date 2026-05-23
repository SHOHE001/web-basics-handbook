# web-basics-handbook

非エンジニアの大学生が、Claude Code で手を動かしながら Web 技術の基礎を学ぶための自分用ハンドブック。

## このプロジェクトの目的

- ブラウザの「裏側で何が起きているか」を、文章で読むだけでなく実際にコードで再現して理解する
- Web 技術の全体像（ネットワーク・HTTP・データ形式・Web アプリ・セキュリティ・運用）を一通り通しで触る
- 「あとから自分が読み返して思い出せる教科書」として残す

## 構成

各章は **読み物としての本文（`README.md`）** と **手を動かす実装（`code/`）** の二段構えです。読むだけでも完結し、もう一歩踏み込みたい章では実際にコードを動かして体感します。

```
web-basics-handbook/
├── README.md              # このファイル
├── CLAUDE.md              # Claude Code 用の運用ルール・進捗
├── requirements.txt       # Python 依存パッケージ（章を進めるごとに追記）
├── .gitignore
├── chapters/              # 本編
│   ├── 01-what-is-web/    # Web とは何か
│   ├── 02-network/        # ネットワーク（IP / DNS / TCP）
│   ├── 03-http/           # HTTP ★実装重め
│   ├── 04-data-format/    # JSON / CSV / MIME
│   ├── 05-web-app/        # Flask / FastAPI ★実装重め
│   ├── 06-security/       # SQLi / XSS の再現と対策
│   └── 07-infra/          # 構築・運用
└── extras/                # 番外編
    ├── qa-log.md          # 「わからない」を Claude に聞いた記録
    └── supplements/       # 記録が 3 件たまると Claude が作る補強ページ
```

## 進捗

- [x] Chapter 1: Web とは何か
- [x] Chapter 2: ネットワーク
- [x] Chapter 3: HTTP
- [x] Chapter 4: データ形式
- [ ] Chapter 5: Web アプリ
- [ ] Chapter 6: セキュリティ
- [ ] Chapter 7: 構築・運用

各章のステータスは章内 `README.md` 冒頭にも記載（執筆予定 / 執筆中 / 完了）。

## セットアップ

Python 3.11 以上を想定。

```bash
# 仮想環境を作って有効化
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell の場合
# source .venv/bin/activate    # macOS / Linux の場合

# 依存パッケージのインストール
pip install -r requirements.txt
```

章ごとに必要なパッケージが増えていくので、進めるたびに `requirements.txt` を更新して `pip install -r requirements.txt` を再実行します。

## 学習のすすめ方

1. 章の `README.md` を最後まで読む（本文＋つまずきポイント）
2. 「手を動かすパート」がある章では `code/` 配下のスクリプトを実行
3. うまく動かなかったら、エラーメッセージごと Claude Code に貼って質問
4. **わからない単語が出てきたら遠慮なく Claude Code に聞く**。回答と一緒に `extras/qa-log.md` に記録され、同じ関連章で 3 件たまると補強ページを Claude が提案してくれます
5. 次の章へ

## 参考

章構成と扱うトピックは『この一冊で全部わかる Web 技術の基本 第2版』（SBクリエイティブ）を参考にしています。本文は書籍の引き写しではなく、自分の理解を整理しながら書き起こしたものです。
