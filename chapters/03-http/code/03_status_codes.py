"""httpbin.org を使って、わざと色々なステータスコードを返してもらう。

httpbin.org は HTTP の挙動を試すための公開テストサーバー。
URL のパスを `/status/404` のようにすると、その番号で返してくれる。

ステータスコードに応じて挙動を分岐する書き方の練習。

使い方:
    python 03_status_codes.py
"""

import requests

ENDPOINTS = [
    ("https://httpbin.org/status/200", "成功"),
    ("https://httpbin.org/status/301", "リダイレクト（永続）"),
    ("https://httpbin.org/status/404", "Not Found"),
    ("https://httpbin.org/status/418", "I'm a teapot（ジョークコード）"),
    ("https://httpbin.org/status/500", "サーバーエラー"),
    ("https://httpbin.org/status/503", "メンテナンス中"),
]


def classify(code: int) -> str:
    """ステータスコードを大分類のラベルに変換する。"""
    if 200 <= code < 300:
        return "2xx 成功"
    if 300 <= code < 400:
        return "3xx リダイレクト"
    if 400 <= code < 500:
        return "4xx クライアント側のエラー"
    if 500 <= code < 600:
        return "5xx サーバー側のエラー"
    return "想定外"


def main() -> None:
    for url, note in ENDPOINTS:
        try:
            # allow_redirects=False で 3xx を追わずそのまま見る
            response = requests.get(url, allow_redirects=False, timeout=5.0)
        except requests.RequestException as exc:
            print(f"{url}: 失敗 ({exc})")
            continue

        code = response.status_code
        label = classify(code)
        ok_mark = "[OK]" if response.ok else "[NG]"  # 2xx 系のときだけ True
        print(f"{ok_mark} {code:>3}  {label:<25}  {note}  ({url})")

    print()
    print("ヒント:")
    print("  - response.ok は 2xx のときだけ True（3xx も False になる）")
    print("  - 4xx は「お前が悪い」、5xx は「サーバーが悪い」と覚える")
    print("  - 418 は HTTP のジョーク仕様（コーヒーポットに紅茶を頼んだら返す）")


if __name__ == "__main__":
    main()
