"""TCP コネクションを張って、何もせずに閉じる。

「ブラウザでページが出るまでの 5 段階」のうち、
1) 名前解決 → 2) TCP コネクション確立 までを Python の socket で再現する。

ここで作ったコネクションに HTTP リクエスト本文を書き込むと、
Chapter 3 で扱う「生の HTTP」になる。

使い方:
    python 03_tcp_connect.py                       # example.com:80
    python 03_tcp_connect.py example.com 443
    python 03_tcp_connect.py 1.1.1.1 80
"""

import socket
import sys


def connect(hostname: str, port: int) -> None:
    print(f"[1] resolving {hostname} ...")
    ip = socket.gethostbyname(hostname)
    print(f"    -> {ip}")

    print(f"[2] opening TCP socket and connecting to {ip}:{port} ...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(5.0)
        sock.connect((ip, port))

        local = sock.getsockname()
        remote = sock.getpeername()
        print("    connected!")
        print(f"      local  (me):    {local[0]}:{local[1]}")
        print(f"      remote (peer):  {remote[0]}:{remote[1]}")

    print("[3] closed.")


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    connect(host, port)
