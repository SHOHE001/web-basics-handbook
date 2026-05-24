"""Chapter 6: XSS — 修正版

html.escape() で特殊文字を実体参照に変換してから貼る。
<script> は &lt;script&gt; に変わり、ブラウザは「ただの文字列」として表示する。
"""

import html
from pathlib import Path


posts = [
    {"name": "alice", "body": "今日はいい天気でした。"},
    {"name": "bob",   "body": "明日は雨らしい。"},
    {"name": "attacker", "body": "<script>alert('XSS! Cookie=' + document.cookie)</script>"},
]


def render_safe(posts: list[dict]) -> str:
    """OK: html.escape() でエスケープしてから埋め込む。"""
    items = []
    for p in posts:
        safe_name = html.escape(p["name"])
        safe_body = html.escape(p["body"])
        items.append(f"<li><b>{safe_name}</b>: {safe_body}</li>")
    return (
        "<!DOCTYPE html>\n<html lang='ja'><head><meta charset='utf-8'>"
        "<title>fixed</title></head><body>"
        "<h1>掲示板（修正版）</h1><ul>" + "\n".join(items) + "</ul></body></html>"
    )


def main() -> None:
    out = Path(__file__).parent / "fixed.html"
    out.write_text(render_safe(posts), encoding="utf-8")
    print(f"  生成: {out}")
    print("  → ブラウザで開いても alert は出ない。<script> が文字列として表示されるだけ")


if __name__ == "__main__":
    main()
