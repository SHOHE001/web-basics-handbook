"""CSV を読み込んで dict のリストに変換し、JSON で書き出す。

「同じデータでも形式を変えれば違うアプリで使える」体験。
CSV → Excel で開ける、JSON → API のレスポンスに使える、というイメージ。

使い方:
    python 02_csv_parse.py
    python 02_csv_parse.py sample.csv
"""

import csv
import json
import sys
from pathlib import Path


def csv_to_dicts(path: Path) -> list[dict]:
    """CSV を読み込んで dict のリストに変換する。

    csv.DictReader は 1 行目をヘッダーとして自動で使ってくれる。
    値は全部文字列で読まれるので、必要なら自分で型変換する。
    """
    rows: list[dict] = []
    # newline="" は CSV を読むときの定番のおまじない（改行コードの違いを吸収）
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 自前で型変換: 数字や bool を Python の型に直す
            row["age"] = int(row["age"])
            row["is_student"] = row["is_student"].lower() == "true"
            rows.append(row)
    return rows


def main() -> None:
    here = Path(__file__).parent
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else here / "sample.csv"
    if not csv_path.is_absolute():
        csv_path = here / csv_path

    print(f"=== {csv_path.name} を読み込む ===")
    rows = csv_to_dicts(csv_path)
    for row in rows:
        print(f"  {row}")

    print()
    print("=== JSON に変換して書き出す ===")
    json_path = here / "sample.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"  -> {json_path.name} に書き出した")

    print()
    print("=== JSON ファイルの中身（先頭部分） ===")
    print(json_path.read_text(encoding="utf-8")[:300])


if __name__ == "__main__":
    main()
