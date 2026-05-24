"""Chapter 5: FastAPI でつくる超ミニ TODO API

機能:
- GET    /items         一覧
- GET    /items/{id}    1 件取得
- POST   /items         新規作成
- DELETE /items/{id}    削除

データは「メモリ上の dict」だけ。サーバーを再起動すると消える。
DB の話は学習スコープを広げすぎるので、Chapter 7 まで持ち越し。
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ----------------------------------------------------------------------
# 学習用スイッチ:
#   CORS の体験用。False にして再起動 → ブラウザから fetch すると
#   開発者ツールに赤字で CORS エラーが出る。True に戻すと通る。
# ----------------------------------------------------------------------
USE_CORS = True


app = FastAPI(title="Chapter 5: TODO API")

if USE_CORS:
    app.add_middleware(
        CORSMiddleware,
        # 開発中なので 5500 と 8000 を許可。
        # 本番では「フロントが乗っているドメイン」だけを書くのが原則。
        allow_origins=[
            "http://127.0.0.1:5500",
            "http://localhost:5500",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )


# --- データモデル -------------------------------------------------------

class ItemIn(BaseModel):
    """POST のリクエストボディ用。クライアントから受け取る項目だけ。"""

    name: str
    done: bool = False


class Item(ItemIn):
    """レスポンス用。サーバー側で振った id を付ける。"""

    id: int


# --- インメモリの「DB もどき」----------------------------------------

_items: dict[int, Item] = {}
_next_id: int = 1


# --- ルート -----------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Chapter 5 TODO API. See /docs for the OpenAPI UI."}


@app.get("/items", response_model=list[Item])
def list_items():
    return list(_items.values())


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="item not found")
    return _items[item_id]


@app.post("/items", response_model=Item, status_code=201)
def create_item(item_in: ItemIn):
    global _next_id
    item = Item(id=_next_id, **item_in.model_dump())
    _items[_next_id] = item
    _next_id += 1
    return item


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="item not found")
    del _items[item_id]
    return None
