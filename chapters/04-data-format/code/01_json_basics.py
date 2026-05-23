"""JSON と Python の dict / list の相互変換。

JSON は「ただの文字列」。
それを Python が読める dict / list に変える（パース）のが json.loads。
逆に dict を JSON の文字列に変えるのが json.dumps。

使い方:
    python 01_json_basics.py
"""

import json


def main() -> None:
    # 1) JSON 文字列 → Python オブジェクト
    json_text = """
    {
      "name": "Alice",
      "age": 22,
      "is_student": true,
      "favorites": ["python", "music", null],
      "address": {"city": "Tokyo", "zip": "100-0001"}
    }
    """

    data = json.loads(json_text)
    print("=== json.loads でパース後 ===")
    print(f"  type        : {type(data).__name__}")
    print(f"  name        : {data['name']}  (type: {type(data['name']).__name__})")
    print(f"  age         : {data['age']}  (type: {type(data['age']).__name__})")
    print(f"  is_student  : {data['is_student']}  (type: {type(data['is_student']).__name__})")
    print(f"  favorites   : {data['favorites']}  (type: {type(data['favorites']).__name__})")
    print(f"  address.city: {data['address']['city']}")
    print()

    # JSON の null → Python の None
    # JSON の true/false → Python の True/False
    # JSON の数値 → int or float
    # JSON のオブジェクト → dict
    # JSON の配列 → list

    # 2) Python オブジェクト → JSON 文字列
    obj = {
        "title": "Web 技術の基本",
        "chapters": [1, 2, 3, 4],
        "completed": False,
        "author": None,
        "日本語キー": "値も日本語",  # 日本語も普通に扱える
    }

    # ensure_ascii=False を付けないと日本語が \uXXXX エスケープになる
    text = json.dumps(obj, ensure_ascii=False, indent=2)
    print("=== json.dumps でシリアライズ後 ===")
    print(text)
    print()

    # 3) よくあるハマりポイント
    print("=== よくある間違い ===")

    # ダメな JSON: シングルクオート
    bad = "{'name': 'Alice'}"
    try:
        json.loads(bad)
    except json.JSONDecodeError as exc:
        print(f"  シングルクオートは NG: {exc}")

    # ダメな JSON: 末尾カンマ
    bad2 = '{"name": "Alice",}'
    try:
        json.loads(bad2)
    except json.JSONDecodeError as exc:
        print(f"  末尾カンマも NG: {exc}")

    # ダメな JSON: コメント
    bad3 = '{"name": "Alice"} // これはコメント'
    try:
        json.loads(bad3)
    except json.JSONDecodeError as exc:
        print(f"  コメントも NG: {exc}")


if __name__ == "__main__":
    main()
