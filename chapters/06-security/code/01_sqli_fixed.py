"""Chapter 6: SQL インジェクション — 修正版

プレースホルダ (?) で値を別引数として渡すと、DB ライブラリが
「これは SQL の構造ではなく値だ」と解釈してくれる。
同じ攻撃文字列を渡しても「そんなユーザーはいない」となるだけで終わる。
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


def login_safe(conn: sqlite3.Connection, name: str, password: str):
    """OK: プレースホルダで値を渡す。文字列連結しない。"""
    sql = "SELECT id, name FROM users WHERE name = ? AND password = ?"
    print(f"  実行される SQL: {sql}   引数: {(name, password)}")
    cur = conn.cursor()
    cur.execute(sql, (name, password))
    return cur.fetchone()


def main() -> None:
    conn = setup_db()

    print("--- ケース 1: 普通のログイン ---")
    print(f"  結果: {login_safe(conn, 'alice', 'alice-pw')}")

    print("\n--- ケース 2: 間違ったパスワード ---")
    print(f"  結果: {login_safe(conn, 'alice', 'wrong')}")

    print("\n--- ケース 3: 同じ攻撃文字列を渡す ---")
    row = login_safe(conn, "' OR '1'='1' --", "anything")
    print(f"  結果: {row}")
    if row is None:
        print("  → 攻撃は通らない。値として扱われたので一致するユーザーがいない")


if __name__ == "__main__":
    main()
