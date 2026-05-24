"""Chapter 6: XSS — ★ 脆弱なコード（学習目的）

掲示板のような「ユーザー投稿を表示するページ」を、文字列連結だけで
組み立てると、<script> タグがそのままブラウザで実行されてしまう。

このスクリプトは vulnerable.html を生成するだけ。
ブラウザで開くと alert() が走るのが確認できる。
"""

from pathlib import Path


# 攻撃者が投稿したつもりの「悪意ある投稿」
posts = [
    {"name": "alice", "body": "今日はいい天気でした。"},
    {"name": "bob",   "body": "明日は雨らしい。"},
    {"name": "attacker", "body": "<script>alert('XSS! Cookie=' + document.cookie)</script>"},
]


def render_vulnerable(posts: list[dict]) -> str:
    """★ ユーザー入力をそのまま HTML に貼る典型的なダメ実装。"""
    items = []
    for p in posts:
        # 文字列連結で HTML を組み立ててしまう
        items.append(f"<li><b>{p['name']}</b>: {p['body']}</li>")
    return (
        "<!DOCTYPE html>\n<html lang='ja'><head><meta charset='utf-8'>"
        "<title>vulnerable</title></head><body>"
        "<h1>掲示板（脆弱版）</h1><ul>" + "\n".join(items) + "</ul></body></html>"
    )


def main() -> None:
    out = Path(__file__).parent / "vulnerable.html"
    out.write_text(render_vulnerable(posts), encoding="utf-8")
    print(f"  生成: {out}")
    print("  → ブラウザで開くと alert がポップアップする = XSS が成立している")


if __name__ == "__main__":
    main()
