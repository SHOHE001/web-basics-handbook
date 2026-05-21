"""DNS 名前解決: ドメイン名から IP アドレスを引く。

ブラウザが URL を開く瞬間、いちばん最初にやっている処理。
Python 標準ライブラリの socket だけで、リゾルバへの問い合わせは OS 任せ。

使い方:
    python 01_dns_lookup.py            # example.com を引く
    python 01_dns_lookup.py google.com
"""

import socket
import sys


def lookup(hostname: str) -> None:
    print(f"[hostname] {hostname}")

    # いちばんシンプルな解決。IPv4 を 1 つだけ返す
    ipv4 = socket.gethostbyname(hostname)
    print(f"  gethostbyname (IPv4, first): {ipv4}")

    # 拡張版。正式名と別名と、複数の IPv4 をまとめて返す
    canonical, aliases, addresses = socket.gethostbyname_ex(hostname)
    print(f"  canonical name:              {canonical}")
    print(f"  aliases:                     {aliases}")
    print(f"  all IPv4 addresses:          {addresses}")

    # getaddrinfo は IPv6 も込みで全部取れる本命 API
    print("  all addresses via getaddrinfo:")
    seen = set()
    for family, _, _, _, sockaddr in socket.getaddrinfo(hostname, None):
        family_name = "IPv6" if family == socket.AF_INET6 else "IPv4"
        addr = sockaddr[0]
        # 重複を弾く（プロトコル違いで同じ IP が複数回出てくるため）
        key = (family_name, addr)
        if key in seen:
            continue
        seen.add(key)
        print(f"    {family_name}: {addr}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    lookup(target)
