# web-basics-handbook

非エンジニアの大学生が、Claude Code で手を動かしながら Web 技術の基礎を学び、その知識を基本情報技術者試験の言葉で整理し直すための自分用ハンドブック。

## このプロジェクトの目的

- ブラウザの「裏側で何が起きているか」を、文章で読むだけでなく実際にコードで再現して理解する
- Web 技術の全体像（ネットワーク・HTTP・データ形式・Web アプリ・セキュリティ・運用）を一通り通しで触る
- 「あとから自分が読み返して思い出せる教科書」として残す
- 本編で身につけた知識を、基本情報技術者試験（FE）の出題分野に沿って整理し直す

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
├── fe/                    # 基本情報技術者試験 編（12 章）
│   ├── README.md          # 試験の概要・最新の制度情報・読み方
│   ├── 01-computer-components/ … 11-strategy/   # 科目 A の分野
│   └── 12-kamoku-b/       # 科目 B（擬似言語・トレース）
├── tools/                 # もの文読書室に置く静的 HTML を作るスクリプト
└── extras/                # 番外編
    ├── qa-log.md          # 「わからない」を Claude に聞いた記録
    └── supplements/       # 記録が 3 件たまると Claude が作る補強ページ
```

## 進捗

- [x] Chapter 1: Web とは何か
- [x] Chapter 2: ネットワーク
- [x] Chapter 3: HTTP
- [x] Chapter 4: データ形式
- [x] Chapter 5: Web アプリ
- [x] Chapter 6: セキュリティ
- [x] Chapter 7: 構築・運用

### 基本情報技術者試験 編

- [x] FE Chapter 1: コンピュータ構成要素
- [x] FE Chapter 2: ソフトウェアとマルチメディア
- [x] FE Chapter 3: 基礎理論
- [x] FE Chapter 4: アルゴリズムとプログラミング
- [x] FE Chapter 5: システム構成要素
- [x] FE Chapter 6: データベース
- [x] FE Chapter 7: ネットワーク
- [x] FE Chapter 8: 情報セキュリティ
- [x] FE Chapter 9: システム開発技術
- [x] FE Chapter 10: マネジメント系
- [x] FE Chapter 11: ストラテジ系
- [x] FE Chapter 12: 科目 B 対策

各章のステータスは章内 `README.md` 冒頭にも記載（執筆予定 / 執筆中 / 完了）。

## 読む場所（もの文読書室）

読み物としての公開先は GitHub ではなく **もの文読書室**（自宅サーバー gen8 の `~/monobun-reading-room` を配信している静的サイト）です。Markdown を HTML に変換して、読書室の中の `web-basics-handbook/` サブフォルダに置きます。

```bash
# gen8 の上で
cd ~/web-basics-handbook
git pull
bash tools/deploy_reading_room.sh
```

- 初回だけ、ビルド用の仮想環境 `.venv-build/` を作って `markdown` パッケージを入れます
- 読書室のほかのファイルには触らず、`web-basics-handbook/` だけを作り直します
- 読書室のトップ URL の後ろに `/web-basics-handbook/` を付けると目次が開きます

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

基本情報技術者試験 編は、章の順番と大分類を栢木厚『かやのき先生の基本情報技術者教室』（技術評論社）にならい、節の組み立てと本文は一から書き起こしています。試験制度の情報は IPA の公表内容（2026 年 11 月時点）に基づきます。
