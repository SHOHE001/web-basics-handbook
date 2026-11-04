"""FE Chapter 6: SQL を sqlite3 で実際に動かす。

本文の「注文の記録」を第 3 正規形まで分けた 4 つの表を作り、
SELECT・GROUP BY・HAVING・JOIN・副問合せ・トランザクションを試す。
DB はメモリ上に作るので、実行のたびに初期状態から始まる。

使い方:
    python sql_practice.py
"""

import sqlite3

SCHEMA = """
CREATE TABLE 顧客 (
    顧客番号 TEXT PRIMARY KEY,
    顧客名   TEXT NOT NULL
);
CREATE TABLE 商品 (
    商品番号 TEXT PRIMARY KEY,
    商品名   TEXT NOT NULL,
    単価     INTEGER NOT NULL CHECK (単価 >= 0)
);
CREATE TABLE 注文 (
    注文番号 INTEGER PRIMARY KEY,
    注文日   TEXT NOT NULL,
    顧客番号 TEXT NOT NULL REFERENCES 顧客(顧客番号)
);
CREATE TABLE 注文明細 (
    注文番号 INTEGER REFERENCES 注文(注文番号),
    商品番号 TEXT REFERENCES 商品(商品番号),
    数量     INTEGER NOT NULL,
    PRIMARY KEY (注文番号, 商品番号)
);

INSERT INTO 顧客 VALUES ('C01', '青木'), ('C02', '井上');
INSERT INTO 商品 VALUES ('P1', 'ノート', 200), ('P2', 'ペン', 100), ('P3', '消しゴム', 80);
INSERT INTO 注文 VALUES (1001, '2026-11-01', 'C01'), (1002, '2026-11-02', 'C02');
INSERT INTO 注文明細 VALUES (1001, 'P1', 3), (1001, 'P2', 5), (1002, 'P1', 1);
"""


def show(conn: sqlite3.Connection, title: str, sql: str) -> None:
    """SQL を実行して、見出し付きで結果を表示する。"""
    print(f"\n== {title} ==")
    print(sql.strip())
    cursor = conn.execute(sql)
    headers = [d[0] for d in cursor.description]
    print("→", " | ".join(headers))
    for row in cursor.fetchall():
        print("  ", " | ".join(str(v) for v in row))


def main() -> None:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite は外部キー制約を明示的にオンにする
    conn.executescript(SCHEMA)

    show(conn, "選択と並べ替え", "SELECT 商品名, 単価 FROM 商品 WHERE 単価 >= 100 ORDER BY 単価 DESC;")

    show(conn, "JOIN（正規化した表をつなぎ直す）", """
SELECT 注文.注文番号, 顧客.顧客名, 商品.商品名, 注文明細.数量, 商品.単価 * 注文明細.数量 AS 金額
FROM 注文明細
JOIN 注文 ON 注文明細.注文番号 = 注文.注文番号
JOIN 顧客 ON 注文.顧客番号 = 顧客.顧客番号
JOIN 商品 ON 注文明細.商品番号 = 商品.商品番号;
""")

    show(conn, "GROUP BY と HAVING（合計 1,000 円以上の注文）", """
SELECT 注文明細.注文番号, SUM(商品.単価 * 注文明細.数量) AS 合計
FROM 注文明細 JOIN 商品 ON 注文明細.商品番号 = 商品.商品番号
GROUP BY 注文明細.注文番号
HAVING SUM(商品.単価 * 注文明細.数量) >= 1000;
""")

    show(conn, "副問合せ（平均単価より高い商品）",
         "SELECT 商品名, 単価 FROM 商品 WHERE 単価 > (SELECT AVG(単価) FROM 商品);")

    # トランザクション: 2 つの更新のうち 2 つ目が制約違反で失敗 → 両方取り消される
    print("\n== トランザクション（途中で失敗したらロールバック）==")
    try:
        with conn:  # with ブロックを抜けるときに、成功ならコミット、例外ならロールバック
            conn.execute("UPDATE 商品 SET 単価 = 220 WHERE 商品番号 = 'P1'")
            conn.execute("UPDATE 商品 SET 単価 = -1 WHERE 商品番号 = 'P2'")  # CHECK 制約に違反
    except sqlite3.IntegrityError as exc:
        print("失敗したのでロールバック:", exc)
    show(conn, "ロールバック後（P1 の単価も 200 のまま）", "SELECT 商品番号, 単価 FROM 商品;")

    # 外部キー制約: 存在しない顧客の注文は入れられない
    print("\n== 参照制約 ==")
    try:
        conn.execute("INSERT INTO 注文 VALUES (1003, '2026-11-03', 'C99')")
    except sqlite3.IntegrityError as exc:
        print("存在しない顧客 C99 は参照できない:", exc)

    conn.close()


if __name__ == "__main__":
    main()
