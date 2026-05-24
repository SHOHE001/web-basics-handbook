# Chapter 5: Web アプリ ★実装重め

> Status: 完了

## この章で学ぶこと

- **Web サイト** と **Web アプリ** の違い
- **Web フレームワーク** が何を肩代わりしてくれるのか（FastAPI を例に）
- **ルーティング**: URL とコードを結びつける仕組み
- **REST API** の考え方（リソース + メソッド）
- ブラウザの JavaScript から **`fetch`** で自分の API を叩く
- <mark>**CORS**</mark>（Cross-Origin Resource Sharing）— ブラウザの仕様で生まれるエラーを意図的に出して、自分で直す

## 前提知識

- [Chapter 3](../03-http/README.md)（HTTP）と [Chapter 4](../04-data-format/README.md)（データ形式）。とくに「メソッド」「ステータスコード」「`Content-Type: application/json`」が頭に入っていれば OK。
- Python を「`def` で関数が書ける、`pip install` でライブラリを入れられる」くらいに触ったことがあること。

## 本文

### 1. Web サイトと Web アプリの違い

呼び方の境目は曖昧ですが、ざっくりこういう区別。

| | Web サイト | Web アプリ |
|---|---|---|
| 主な役割 | **情報を読ませる** | **ユーザーの操作で状態が変わる** |
| 例 | Wikipedia、ニュース記事、企業の会社案内 | Twitter / X、Gmail、Google Maps、Notion |
| サーバーの仕事 | 既にできた HTML を返す | リクエストごとに **計算してから** 返す |

Wikipedia は記事を読むだけ。Twitter は **「いいね」を押すと数字が増える**、つまりサーバーの中の状態（DB のレコード）が書き換わる。後者を支えているのが **Web アプリ** と呼ばれる仕組みです。

**実例**: 同じブラウザで開いていても、`https://ja.wikipedia.org/wiki/HTML` は静的なページ（≒ Web サイト寄り）、`https://twitter.com/home` はログイン状態とタイムラインの計算がリクエストごとに走る（Web アプリ）。

### 2. Web フレームワークの役割

Chapter 3 で生ソケットで HTTP を書きました。あれを「リクエストを受けて適切なレスポンスを返す」アプリに育てようとすると、次のような **退屈で間違えやすい仕事** を毎回手書きすることになります。

- ポートを開いてリクエストを待ち受ける
- リクエスト行・ヘッダー・ボディをパースする
- メソッドとパスを見て、対応する処理に振り分ける
- レスポンスのステータスライン・ヘッダー・ボディを組み立てる
- 文字コード、エラーハンドリング、複数リクエストの同時処理 …

<mark>**Web フレームワークは、この「定型処理」を全部肩代わりして、「URL とそれに対する処理」だけを書けばよくしてくれるライブラリ**</mark>です。

Python の代表的なフレームワーク:

| | 特徴 |
|---|---|
| **FastAPI** | 型ヒントを書くだけで自動でドキュメント生成・バリデーション。最近の主流 |
| **Flask** | シンプルで小さい。古典 |
| **Django** | 大きい。DB から管理画面まで全部入り。会社の業務システム向け |

この章では **FastAPI** を使います。

### 3. 最小の FastAPI アプリ

```python
# app.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, Web!"}
```

立ち上げる:

```bash
uvicorn app:app --reload
```

これだけで `http://127.0.0.1:8000/` を開くと `{"message":"Hello, Web!"}` が返ってきます。

裏で起きていること:

1. **uvicorn** という ASGI サーバーが ポート 8000 で待ち受ける
2. ブラウザから GET / が来る
3. FastAPI が `@app.get("/")` を見つけて `root()` を呼ぶ
4. 返ってきた dict を <mark>**自動で JSON にして `Content-Type: application/json` を付けて**</mark>返す

Chapter 3 で手書きしていた `Content-Type: ...` も `Content-Length: ...` も自分で書かなくていい。これがフレームワークの威力。

**実例**: 起動した状態で `http://127.0.0.1:8000/docs` を開くと、書いたエンドポイントが **Swagger UI** という対話式のドキュメントになっている。これも FastAPI が型ヒントから自動生成しているもの。

### 4. ルーティング

「URL のパス + メソッド」 ↔ 「Python の関数」 を結びつけるのが <mark>**ルーティング**</mark>。

```python
@app.get("/items")                  # GET /items        → 一覧
def list_items(): ...

@app.get("/items/{item_id}")        # GET /items/3      → 1 件取得
def get_item(item_id: int): ...

@app.post("/items")                 # POST /items       → 作成
def create_item(item: Item): ...

@app.delete("/items/{item_id}")     # DELETE /items/3   → 削除
def delete_item(item_id: int): ...
```

- `{item_id}` のような中括弧は <mark>**パスパラメータ**</mark>。関数の引数に同じ名前で受け取れる
- `?q=python` のような <mark>**クエリパラメータ**</mark> は、関数の引数（パスパラに無いもの）として自動で渡される
- POST のボディ（JSON）は、Pydantic というライブラリの **モデルクラス**（`Item`）に自動で詰めてくれる

**実例**: Twitter の URL を見ると `https://twitter.com/<ユーザー名>/status/<ツイートID>` という構造。これも内部的には `/{username}/status/{tweet_id}` のようなルーティングが書かれていて、`username` と `tweet_id` が関数に渡って、対応するツイートを返している、と想像できる。

### 5. REST API の考え方

<mark>**REST API**</mark> は API の設計スタイルの 1 つで、ざっくり「**リソースを URL で表し、操作を HTTP メソッドで表す**」というルール。

| やりたいこと | メソッド + URL |
|---|---|
| 投稿の一覧を見る | `GET /posts` |
| 投稿を 1 件見る | `GET /posts/42` |
| 投稿を新規作成 | `POST /posts` |
| 投稿を更新 | `PUT /posts/42` または `PATCH /posts/42` |
| 投稿を削除 | `DELETE /posts/42` |

URL に動詞を入れない（×`/getPost?id=42`）のが REST 流。**動詞は HTTP メソッドが担当する**、という分業です。

世の中の API がきれいに REST で書かれているとは限りませんが、用語と発想は基礎として共通なので押さえておく価値があります。

### 6. フロントエンド（ブラウザの JS）から API を叩く

ブラウザの JavaScript から API を呼ぶ標準的なやり方が、Chapter 3 でも触れた `fetch`。

```js
// 一覧を取得
const res = await fetch("http://127.0.0.1:8000/items");
const items = await res.json();          // ボディを JSON としてパース
console.log(items);

// 新規作成（POST + JSON ボディ）
await fetch("http://127.0.0.1:8000/items", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "apple", price: 100 }),
});
```

`fetch` は Promise を返すので `await` で待つ。レスポンスのボディは `res.json()` か `res.text()` で読む。

> [!TIP]
> `await fetch(...)` の戻り値は <mark>**レスポンスのヘッダー部分だけ受け取った状態**</mark>。ボディはまだ読まれていない。だから `res.json()` でもう一度 `await` する必要がある。慣れないうちに `await` が 1 つ足りなくて「`[object Promise]`」と表示されがち。

### 7. CORS — Web アプリ初心者の最初の関門

ここからが Chapter 5 の本番。

#### 7-1. 何が起きるか

`http://127.0.0.1:5500` でホストしている HTML から、`http://127.0.0.1:8000` の API を `fetch` で叩く。これをやると、ブラウザの開発者ツールに <mark>**赤いエラー**</mark> が出ます。

```
Access to fetch at 'http://127.0.0.1:8000/items' from origin
'http://127.0.0.1:5500' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

このメッセージはほぼ全ての Web 開発者が一度は見るやつ。

#### 7-2. なぜ起きるか

ブラウザには <mark>**同一オリジンポリシー（Same-Origin Policy）**</mark> という安全装置があります。

**オリジン** = `スキーム + ホスト + ポート` の組。
- `http://127.0.0.1:5500` と `http://127.0.0.1:8000` は **ポートが違う** → 別オリジン
- `https://example.com` と `http://example.com` は **スキームが違う** → 別オリジン

「自分が読み込まれたオリジンと違うサーバーへ JS から自由にアクセスされると危険」（あなたの銀行サイトに勝手にお金を送るリクエストが飛ばせてしまう、など）なので、**ブラウザがそれを禁止している**。

ただ、Web アプリは「フロントを A サーバー、API を B サーバー」のように **意図的に別オリジンに分ける** ことも多い。そこで「**サーバー側が『このオリジンからのアクセスは許可するよ』と宣言すれば許す**」という抜け道が用意されています。これが <mark>**CORS（Cross-Origin Resource Sharing）**</mark>。

> [!IMPORTANT]
> ここで重要なのは、<mark>**ブラウザは「検証者」であって「制御者」ではない**</mark>こと。「ブラウザが禁止している」と言うと「ブラウザ側で何か設定すれば通る」と読めますが、実態は **「サーバーが許可ヘッダーを返してくるか確認して、なければ JS から結果を読ませない」** という監視役。だから <mark>**サーバーが許可ヘッダーを返さない限り、クライアント側を何度書き換えても通らない**</mark>。

#### 7-3. どう直すか

サーバー（FastAPI）側で、許可するオリジンを宣言する。

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],   # ← ここに「許可するオリジン」を書く
    allow_methods=["*"],
    allow_headers=["*"],
)
```

これでサーバーがレスポンスヘッダーに `Access-Control-Allow-Origin: http://127.0.0.1:5500` を付けるようになり、ブラウザが「OK、サーバーが許してるから読んでよし」と判断してくれる。

> [!CAUTION]
> <mark>**CORS は「サーバー側」で直す**</mark>。クライアント（HTML や JS）をいくらいじっても直らない。「fetch のオプションを変えてエラーを回避できないか」と探しがちですが、**根本的にサーバーが許可ヘッダーを返さない限り通らない**。これは仕組みであって、バグではない。

#### 7-4. 開発中に `allow_origins=["*"]` でいいの？

「とりあえず全部許可」する `allow_origins=["*"]` は <mark>**開発中だけにする**</mark>。本番ではフロントが乗っているドメインだけを明示するのが原則。`*` は Cookie 付きのリクエスト（`credentials: "include"`）と一緒には使えないというブラウザ仕様もあって、いずれ困ります。

## 手を動かすパート

`code/` 配下に最小構成の Web アプリ一式を置いてあります。

```
code/
├── app.py            # FastAPI のサーバー本体（インメモリの簡易 TODO API）
├── index.html        # ブラウザから fetch する HTML
├── README.md         # 動かす手順とつまずきポイント
└── requirements.txt  # この章だけの依存（fastapi + uvicorn）
```

ざっくりの流れ:

```bash
cd chapters/05-web-app/code

# 1. 依存をインストール（ルートの requirements.txt にも追記済み）
pip install -r requirements.txt

# 2. API サーバーを起動
uvicorn app:app --reload
# → http://127.0.0.1:8000/docs を開いて API の対話ドキュメントが見られる

# 3. 別ターミナルで、HTML を配信する簡易サーバーを立ち上げる
#    （python の標準ライブラリだけで OK）
python -m http.server 5500
# → http://127.0.0.1:5500/index.html を開く
```

`index.html` のボタンを押すと、ブラウザの JS が `http://127.0.0.1:8000` の API を `fetch` で叩きます。

#### ★ つまずきポイントを意図的に体験する

`app.py` の冒頭付近に **`USE_CORS = True`** という変数があります。これを `False` にしてサーバーを再起動 → ブラウザで再操作してみてください。**CORS エラーが赤字で出る** のが見えます。

`True` に戻して再起動すると、エラーが消えて、ちゃんと API のレスポンスが画面に出る。**この往復を 1 回体験する** ことがこの章のゴールです。

## つまずきポイント

> [!CAUTION]
> このセクションは「最初に Web アプリを書いたとき**ほぼ確実に踏む**罠」のリスト。動かないときはまずここを疑う。

- <mark>**`uvicorn app:app` の意味**</mark>: 「`app.py` というファイルの中の `app` という変数」を読み込む、という指定。ファイル名と変数名を間違えると `Error loading ASGI app` で落ちる
- <mark>**ポートかぶり**</mark>: 同じ PC で `uvicorn` を 2 重起動すると `[Errno 48] Address already in use`。古いほうを `Ctrl + C` で止めるか、`--port 8001` で別ポートに逃がす
- <mark>**`fetch` の戻り値はヘッダーだけ**</mark>: ボディは `res.json()` か `res.text()` で再度 `await` しないと取れない
- <mark>**CORS はサーバー側で直す**</mark>: クライアントをいくらいじっても直らない（最重要）
- <mark>**`localhost` と `127.0.0.1` は別オリジン扱い**</mark>: ブラウザは「文字列が違えば別オリジン」と判断するので、`allow_origins=["http://localhost:5500"]` と書いてブラウザで `http://127.0.0.1:5500` を開くと CORS で落ちる。地味にハマる
- **`--reload` は開発専用**: コードを保存するたびに自動再起動して便利だが、本番ではオフにする
- **`/docs` を活用する**: 自分の API を `curl` や `fetch` で叩く前に、まず `/docs`（Swagger UI）からポチポチ動かしてみると「自分の API がどう見えるか」が体感できる

## 次の章へ

API を立てて、フロントから叩いて、CORS の壁を 1 回越えた。次は **[Chapter 6: セキュリティ](../06-security/README.md)** で、その API を **どう攻撃されるか・どう守るか** を学びます。SQL インジェクションと XSS をローカルで再現してから修正する、攻撃側の視点も含めた章です。

## 重要な単語まとめ

| 用語 | 一言で言うと | 身近な実例 |
|---|---|---|
| **Web フレームワーク** | HTTP の定型処理を肩代わりするライブラリ | Flask, FastAPI, Django, Ruby on Rails |
| **FastAPI** | Python の現代的な Web フレームワーク。型ヒント前提 | `@app.get("/")` でルートを書く |
| **ASGI / WSGI** | Python の Web サーバーとアプリの接続規格 | uvicorn は ASGI、gunicorn は WSGI |
| **uvicorn** | FastAPI を動かす ASGI サーバー | `uvicorn app:app --reload` |
| **ルーティング** | URL とコードを結びつける仕組み | `@app.get("/items/{id}")` |
| **パスパラメータ** | URL のパスに埋め込む変数 | `/users/42` の `42` |
| **クエリパラメータ** | URL の `?` 以降のキー = 値 | `/search?q=python` の `q=python` |
| **REST API** | リソース + メソッドで設計する API スタイル | `GET /posts/42`, `DELETE /posts/42` |
| **`fetch`** | ブラウザの JS から HTTP を叩く標準 API | `await fetch("/api/items")` |
| **オリジン** | `スキーム + ホスト + ポート` の組 | `http://127.0.0.1:8000` |
| **同一オリジンポリシー** | 別オリジンへのアクセスを基本禁止するブラウザの安全装置 | 銀行サイトに勝手にリクエストされない仕組み |
| **CORS** | サーバーが「このオリジンは許可」と宣言する仕組み | `Access-Control-Allow-Origin` ヘッダー |
| **プリフライト** | 本リクエストの前にブラウザが送る `OPTIONS` 問い合わせ | カスタムヘッダーや PUT/DELETE で発動 |
| **Swagger UI / OpenAPI** | API の対話式ドキュメント | `/docs` で自動表示される画面 |
