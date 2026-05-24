# Chapter 5: 動かし方

## 準備

```bash
cd chapters/05-web-app/code
pip install -r requirements.txt
```

ルートの `requirements.txt` にも `fastapi` / `uvicorn` を追記済みなので、そちらから入れても OK。

## 1. API サーバーを起動

```bash
uvicorn app:app --reload
```

- `http://127.0.0.1:8000/` — ルート（メッセージが返る）
- `http://127.0.0.1:8000/docs` — Swagger UI（対話式ドキュメント）

`--reload` を付けると、`app.py` を保存するたびに自動再起動する。

## 2. フロントエンドを起動

**別ターミナル** で:

```bash
cd chapters/05-web-app/code
python -m http.server 5500
```

ブラウザで `http://127.0.0.1:5500/index.html` を開く。

> なぜ別サーバーが必要か: `file:///.../index.html` で直接開くと、ブラウザは `fetch` のオリジンを `null` 扱いにして CORS の挙動がおかしくなる。**HTTP で配信されたページから fetch する** ことが、Web アプリの素直なセットアップ。

## 3. CORS エラーを意図的に体験する

1. `app.py` の冒頭の `USE_CORS = True` を **`False`** に変える
2. uvicorn を `Ctrl + C` で止めて、もう一度 `uvicorn app:app --reload` で起動
3. ブラウザの `http://127.0.0.1:5500/index.html` を再読み込み
4. 「追加」「再読み込み」を押すと **赤いエラー枠** が出る。開発者ツール（F12）の Console にも CORS エラーが出ているはず
5. `USE_CORS = True` に戻して再起動 → 動くようになる

この **「壊れる → 直す」** の往復が、Chapter 5 の体験のキモ。

## つまずきメモ

- `uvicorn app:app` の `app:app` は `app.py の中の app という変数`
- ポートが埋まっている → 古い uvicorn を `Ctrl + C` で止めるか、`--port 8001` などで逃がす
- ブラウザのキャッシュで HTML が更新されない → `Ctrl + Shift + R` でハードリロード
- `index.html` を `file:///...` で開いてしまうと挙動が変。必ず `http://127.0.0.1:5500/index.html` 経由で開く
