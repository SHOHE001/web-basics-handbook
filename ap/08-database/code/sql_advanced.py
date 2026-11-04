"""AP Chapter 8: 一段上の SQL を sqlite3 で試す。

図書館の貸出を題材に、
- 外部結合と COUNT(*) / COUNT(列) の違い
- EXISTS（相関副問合せ）
- CASE
- ウィンドウ関数（RANK）
- 条件付き更新による二重引当ての防止
を実行する。DB はメモリ上に作る。

使い方:
    python sql_advanced.py
"""

import sqlite3

SCHEMA = """
CREATE TABLE 会員 (会員番号 TEXT PRIMARY KEY, 氏名 TEXT NOT NULL);
CREATE TABLE 書籍 (
    書籍番号 TEXT PRIMARY KEY, 書名 TEXT NOT NULL, ジャンル TEXT NOT NULL,
    貸出回数 INTEGER NOT NULL, 在庫 INTEGER NOT NULL
);
CREATE TABLE 貸出 (
    貸出番号 INTEGER PRIMARY KEY, 会員番号 TEXT REFERENCES 会員(会員番号),
    書籍番号 TEXT REFERENCES 書籍(書籍番号), 返却期限 TEXT NOT NULL, 返却日 TEXT
);

INSERT INTO 会員 VALUES ('M1', '青木'), ('M2', '井上'), ('M3', '上田');
INSERT INTO 書籍 VALUES
  ('B1', 'Web のしくみ', 'IT', 12, 1),
  ('B2', 'SQL 入門', 'IT', 8, 2),
  ('B3', '銀河鉄道の夜', '文学', 15, 1),
  ('B4', '注文の多い料理店', '文学', 9, 1);
INSERT INTO 貸出 VALUES
  (1, 'M1', 'B1', '2026-10-20', '2026-10-18'),
  (2, 'M1', 'B3', '2026-11-01', NULL),
  (3, 'M2', 'B2', '2026-11-20', NULL);
"""


def show(conn: sqlite3.Connection, title: str, sql: str) -> None:
    print(f"\n== {title} ==")
    cursor = conn.execute(sql)
    print("  " + " | ".join(d[0] for d in cursor.description))
    for row in cursor.fetchall():
        print("  " + " | ".join("NULL" if v is None else str(v) for v in row))


def borrow(conn: sqlite3.Connection, book: str) -> bool:
    """在庫が 1 以上のときだけ減らす。更新できた件数で成否を判定する。"""
    with conn:
        cursor = conn.execute("UPDATE 書籍 SET 在庫 = 在庫 - 1 WHERE 書籍番号 = ? AND 在庫 >= 1", (book,))
    return cursor.rowcount == 1


def main() -> None:
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)

    show(conn, "外部結合: COUNT(*) と COUNT(列) の違い（上田さんは貸出 0 件）", """
SELECT 会員.氏名, COUNT(*) AS COUNT_星, COUNT(貸出.貸出番号) AS COUNT_列
FROM 会員 LEFT OUTER JOIN 貸出 ON 会員.会員番号 = 貸出.会員番号
GROUP BY 会員.会員番号 ORDER BY 会員.会員番号;
""")

    show(conn, "EXISTS: 返却期限を過ぎて未返却の本がある会員", """
SELECT 会員番号, 氏名 FROM 会員
WHERE EXISTS (
  SELECT * FROM 貸出
  WHERE 貸出.会員番号 = 会員.会員番号 AND 貸出.返却日 IS NULL AND 貸出.返却期限 < '2026-11-04'
);
""")

    show(conn, "CASE: 貸出回数で区分", """
SELECT 書名, CASE WHEN 貸出回数 >= 10 THEN '人気' ELSE '通常' END AS 区分 FROM 書籍;
""")

    show(conn, "ウィンドウ関数: ジャンルごとの順位", """
SELECT ジャンル, 書名, 貸出回数,
  RANK() OVER (PARTITION BY ジャンル ORDER BY 貸出回数 DESC) AS 順位
FROM 書籍 ORDER BY ジャンル, 順位;
""")

    print("\n== 条件付き更新: 在庫 1 冊の B1 を 2 人が続けて借りようとする ==")
    print("  1 人目:", "成功" if borrow(conn, "B1") else "在庫なし")
    print("  2 人目:", "成功" if borrow(conn, "B1") else "在庫なし")

    conn.close()


if __name__ == "__main__":
    main()
