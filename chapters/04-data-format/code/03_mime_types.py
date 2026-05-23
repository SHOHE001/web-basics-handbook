"""ファイル拡張子から MIME タイプを判定する。

サーバーが `Content-Type` を決めるときによくやる処理。
Python 標準の `mimetypes` モジュールが OS の MIME 辞書を引いてくれる。

使い方:
    python 03_mime_types.py
"""

import mimetypes


SAMPLES = [
    "index.html",
    "style.css",
    "app.js",
    "data.json",
    "data.csv",
    "photo.png",
    "photo.jpg",
    "icon.svg",
    "doc.pdf",
    "song.mp3",
    "movie.mp4",
    "archive.zip",
    "README.md",
    "unknown.xyz",  # 知らない拡張子
    "no_extension",  # 拡張子なし
]


def main() -> None:
    print(f"{'ファイル名':<20}{'MIME タイプ':<35}用途")
    print("-" * 80)

    for filename in SAMPLES:
        mime, encoding = mimetypes.guess_type(filename)
        mime = mime or "(不明)"
        note = describe(mime)
        print(f"{filename:<20}{mime:<35}{note}")


def describe(mime: str) -> str:
    """MIME タイプに簡単な日本語の説明を添える。"""
    if mime.startswith("text/"):
        return "テキスト系"
    if mime.startswith("image/"):
        return "画像"
    if mime.startswith("audio/"):
        return "音声"
    if mime.startswith("video/"):
        return "動画"
    if mime == "application/json":
        return "JSON（API でおなじみ）"
    if mime == "application/pdf":
        return "PDF"
    if mime == "application/zip":
        return "ZIP アーカイブ"
    if mime == "application/javascript":
        return "JavaScript"
    return ""


if __name__ == "__main__":
    main()
