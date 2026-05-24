# Chapter 5 の API を Render にデプロイする手順

Chapter 7 の手を動かすパート。Chapter 5 の `chapters/05-web-app/code/app.py`（FastAPI の TODO API）を、**Render** という PaaS にデプロイして、世界から見える URL で叩けるようにする。

> Render を例に挙げているのは「GitHub 連携で push したら自動デプロイ」「HTTPS 自動」「無料枠あり」「クレジットカード登録なしで開始できる」の 4 点が揃っているため。Fly.io / Railway / Vercel などでも考え方は同じ。

---

## 0. 前提

- このリポジトリが GitHub にある（このハンドブック自体が GitHub に置かれている前提）
- Render のアカウント（無料）: https://render.com

## 1. デプロイ用ファイルを 1 つ追加する

Render は「リポジトリのどこを起動するか」を知りたいだけなので、ファイル 1 つで足りる。

`chapters/05-web-app/code/` の中の `requirements.txt` はすでに `fastapi` と `uvicorn` を含んでいる。これを Render が読んで `pip install` してくれる。

起動コマンドは、ローカルとは違って `--host 0.0.0.0` と Render が払い出すポート（`$PORT`）を使う:

```
uvicorn app:app --host 0.0.0.0 --port $PORT
```

これだけ覚える。

## 2. Render の Web Service を作る

1. Render ダッシュボードで **「New +」→「Web Service」**
2. **「Build and deploy from a Git repository」** を選ぶ → `web-basics-handbook` を選択
3. 設定:
   - **Name**: 好きな名前（例: `my-todo-api`）。URL に使われる
   - **Region**: 近いリージョン（Singapore など）
   - **Branch**: `main`
   - **Root Directory**: `chapters/05-web-app/code`  ← ★ ここがミソ。サブディレクトリを指定する
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free
4. **「Create Web Service」** を押す

## 3. ビルドログを眺める

Render の画面で、`pip install` → 起動 → `Your service is live` のログが流れる。だいたい 2〜3 分。

完了すると `https://my-todo-api.onrender.com` のような URL が払い出される。

## 4. 動作確認

```bash
# ルート
curl https://my-todo-api.onrender.com/

# 一覧（最初は空）
curl https://my-todo-api.onrender.com/items

# 新規作成
curl -X POST https://my-todo-api.onrender.com/items \
  -H "Content-Type: application/json" \
  -d '{"name": "デプロイ成功！"}'

# 再び一覧
curl https://my-todo-api.onrender.com/items
```

**ブラウザで** `https://my-todo-api.onrender.com/docs` を開くと、Chapter 5 で見た Swagger UI が、今度は **https の本番 URL で** 開ける。これがゴール。

## 5. ハマりどころ

- **`uvicorn app:app` の `app:app` が解決できない**:
  Root Directory が間違っている。`chapters/05-web-app/code` を指定したか確認
- **`Address already in use` っぽいエラー**:
  `--port $PORT` を書き忘れて固定ポートで起動している
- **`CORS` で叩けない**:
  Chapter 5 の `app.py` の `allow_origins` に本番のフロント URL を追加する必要がある
- **無料プランは寝る**:
  Render の Free プランは一定時間アクセスが無いとサービスが「スリープ」する。初回アクセスに数十秒かかったらこれ。コールドスタートはトレードオフ
- **本番では `USE_CORS = False` のデプロイをしない**:
  Chapter 5 で CORS の体験用に置いたスイッチ。本番では必ず `True` のまま

## 6. このあとできること

- **環境変数** を Render の画面から設定して、コードから `os.environ["..."]` で読む（DB の URL や API キーをコードに直書きしない練習）
- **GitHub の `main` に push** すると Render が自動で再デプロイする = これが <mark>**CI/CD**</mark> の最小形
- **Render の DB（PostgreSQL）** を作って、インメモリ `dict` を本物の DB に置き換える（次の学習ステップ）

---

ここまで通せば、「ローカル → 世界に公開」のフルパスが 1 回つながったことになります。Chapter 7 の本文の「全体の地図」を、もう一度読み返してみてください。今度は地図上のどの部分が「自分が今やったところ」か、はっきり見えるはず。
