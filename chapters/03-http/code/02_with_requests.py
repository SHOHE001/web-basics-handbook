"""01_raw_http.py と同じことを `requests` ライブラリで書く。

たった 1 行で、TCP 接続・HTTP リクエスト組み立て・レスポンス解析が
全部内部でやられている。便利さの裏で何が起きているかは
01_raw_http.py を読むと体感できる。

事前に `pip install -r requirements.txt` で requests を入れておく。

使い方:
    python 02_with_requests.py
    python 02_with_requests.py https://example.org
"""

import sys

import requests


def fetch(url: str) -> None:
    # 01 と違って HTTPS でも書ける（TLS は requests の中でよしなにやってくれる）
    response = requests.get(
        url,
        headers={
            "User-Agent": "web-basics-handbook/ch3",
            "Accept": "text/html",
        },
        timeout=5.0,
    )

    print(f"=== {url} ===")
    print(f"status     : {response.status_code} {response.reason}")
    print(f"http ver   : {response.raw.version}  # 11=HTTP/1.1, 20=HTTP/2 など")
    print(f"encoding   : {response.encoding}")
    print(f"body bytes : {len(response.content)}")
    print()

    print("=== ヘッダー（一部） ===")
    for key in ("Content-Type", "Content-Length", "Server", "Date", "Set-Cookie"):
        if key in response.headers:
            print(f"  {key}: {response.headers[key]}")

    print()
    print("=== ボディの先頭 300 文字 ===")
    print(response.text[:300])


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    fetch(url)
