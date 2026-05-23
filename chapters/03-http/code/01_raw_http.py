"""生ソケットで HTTP リクエストを手書きして送る。

Chapter 2 の 03_tcp_connect.py で開いた TCP ソケットに、
たった数行のテキストを書き込むだけで Web ページが取れる。
それを実演するスクリプト。

ポイント:
- 改行は LF ではなく CRLF (\\r\\n)
- ヘッダーとボディの間に空行 1 つ (\\r\\n\\r\\n)
- HTTPS だと TLS が要るので、ここはあえて HTTP (ポート 80)

使い方:
    python 01_raw_http.py
    python 01_raw_http.py example.org
"""

import socket
import sys


def fetch(host: str, path: str = "/", port: int = 80) -> None:
    # 1) TCP コネクション確立
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(5.0)
        sock.connect((host, port))

        # 2) HTTP リクエストを「テキスト」として組み立てる
        #    Host ヘッダーは HTTP/1.1 では必須。
        #    Connection: close を付けないと、サーバーが接続を持ち続けてしまい
        #    recv が終わらなくなる（Keep-Alive のせい）。
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"User-Agent: web-basics-handbook/ch3\r\n"
            f"Accept: text/html\r\n"
            f"Connection: close\r\n"
            f"\r\n"  # ← ヘッダー終端の空行。これを忘れるとリクエストが壊れる
        )

        print("=== 送信したリクエスト ===")
        print(request)

        # 3) バイト列にして送信
        sock.sendall(request.encode("ascii"))

        # 4) レスポンスを最後まで受け取る
        chunks: list[bytes] = []
        while True:
            data = sock.recv(4096)
            if not data:
                break
            chunks.append(data)

    response = b"".join(chunks)

    # 5) ヘッダーとボディに分割（最初の空行で区切られている）
    header_bytes, _, body_bytes = response.partition(b"\r\n\r\n")

    print("=== 受信したレスポンスヘッダー ===")
    print(header_bytes.decode("ascii", errors="replace"))
    print()
    print("=== ボディの先頭 300 バイト ===")
    print(body_bytes[:300].decode("utf-8", errors="replace"))
    print(f"\n(ボディ全体は {len(body_bytes)} バイト)")


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    fetch(host)
