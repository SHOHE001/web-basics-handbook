"""Chapter 6: SQL インジェクション — ★ 脆弱なコード（学習目的）

文字列連結で SQL を組み立てると、'OR' 攻撃で誰でもログインできてしまう。
このスクリプトを動かして「攻撃が成立する」のを自分の目で見ること。

★ このコードを実サービスに書いてはいけません。
"""

import sqlite3


def setup_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, password TEXT)")
    cur.executemany(
        "INSERT INTO users (name, password) VALUES (?, ?)",
        [("admin", "very-secret"), ("alice", "alice-pw"), ("bob", "bob-pw")],
    )
    conn.commit()
    return conn


def login_vulnerable(conn: sqlite3.Connection, name: str, password: str):
    """★ 文字列連結で SQL を組み立てる典型的なダメ実装。"""
    sql = (
        "SELECT id, name FROM users "
        f"WHERE name = '{name}' AND password = '{password}'"
    )
    print(f"  実行される SQL: {sql}")
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchone()


def main() -> None:
    conn = setup_db()

    print("--- ケース 1: 普通のログイン ---")
    print(f"  結果: {login_vulnerable(conn, 'alice', 'alice-pw')}")

    print("\n--- ケース 2: 間違ったパスワード ---")
    print(f"  結果: {login_vulnerable(conn, 'alice', 'wrong')}")

    print("\n--- ケース 3: ★ SQL インジェクション攻撃 ---")
    # name 欄に「' OR '1'='1' --」と入れる。
    # 末尾の `--` は SQL のコメント開始記号で、AND password = ... を丸ごと無効化する。
    attack_name = "' OR '1'='1' --"
    attack_pw = "anything"
    row = login_vulnerable(conn, attack_name, attack_pw)
    print(f"  結果: {row}")
    if row is not None:
        print("  → ★ パスワードを知らないのにログインに成功してしまった！")
        print(f"  → 最初にヒットしたユーザー: {row}")


if __name__ == "__main__":
    main()
