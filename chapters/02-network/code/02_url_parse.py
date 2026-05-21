"""URL を構成要素に分解する。

scheme / userinfo / host / port / path / query / fragment が
URL のどこに対応しているのかを目で見て確認するためのスクリプト。

使い方:
    python 02_url_parse.py
    python 02_url_parse.py "https://example.com/search?q=web&lang=ja"
"""

import sys
from urllib.parse import parse_qs, urlparse


def explain(url: str) -> None:
    parts = urlparse(url)
    print(f"[input] {url}")
    print(f"  scheme:   {parts.scheme!r}")
    print(f"  username: {parts.username!r}")
    print(f"  password: {parts.password!r}")
    print(f"  hostname: {parts.hostname!r}")
    print(f"  port:     {parts.port!r}")
    print(f"  path:     {parts.path!r}")
    print(f"  query:    {parts.query!r}")
    print(f"  fragment: {parts.fragment!r}   # (not sent to the server)")

    if parts.query:
        print(f"  query (parsed): {parse_qs(parts.query)}")


if __name__ == "__main__":
    default = "https://user:pass@example.com:8080/foo/bar?x=1&y=2#section"
    target = sys.argv[1] if len(sys.argv) > 1 else default
    explain(target)
