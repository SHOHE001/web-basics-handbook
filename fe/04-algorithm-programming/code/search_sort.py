"""FE Chapter 4: 探索と整列を、比較回数を数えながら実行する。

Python の sorted() や in 演算子を使えば 1 行で済む処理を、あえて手で書く。
「データが増えると比較回数がどう増えるか」を体感するのが目的。

使い方:
    python search_sort.py
"""

import random


def linear_search(data: list[int], target: int) -> tuple[int, int]:
    """先頭から順に探す。(見つかった位置, 比較回数) を返す。見つからなければ位置は -1。"""
    comparisons = 0
    for i, value in enumerate(data):
        comparisons += 1
        if value == target:
            return i, comparisons
    return -1, comparisons


def binary_search(data: list[int], target: int) -> tuple[int, int]:
    """整列済みのデータを半分ずつ絞って探す。(位置, 比較回数) を返す。"""
    low, high = 0, len(data) - 1
    comparisons = 0
    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        if data[mid] == target:
            return mid, comparisons
        if data[mid] < target:
            low = mid + 1   # 右半分へ
        else:
            high = mid - 1  # 左半分へ
    return -1, comparisons


def selection_sort(data: list[int]) -> tuple[list[int], int]:
    """残りの中から最小値を探して先頭と交換する。(整列結果, 比較回数) を返す。"""
    a = data[:]
    comparisons = 0
    for i in range(len(a) - 1):
        min_index = i
        for j in range(i + 1, len(a)):
            comparisons += 1
            if a[j] < a[min_index]:
                min_index = j
        a[i], a[min_index] = a[min_index], a[i]
    return a, comparisons


def bubble_sort(data: list[int]) -> tuple[list[int], int]:
    """隣どうしを比べて逆なら交換する。(整列結果, 比較回数) を返す。"""
    a = data[:]
    comparisons = 0
    for end in range(len(a) - 1, 0, -1):
        for j in range(end):
            comparisons += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    return a, comparisons


def main() -> None:
    random.seed(0)  # 毎回同じ乱数にして、結果を再現できるようにする

    for n in (10, 100, 1000):
        data = random.sample(range(n * 10), n)
        target = data[-1]  # 線形探索では最悪に近い位置
        sorted_data = sorted(data)

        _, linear_count = linear_search(data, target)
        _, binary_count = binary_search(sorted_data, target)
        selection_result, selection_count = selection_sort(data)
        bubble_result, bubble_count = bubble_sort(data)
        assert selection_result == bubble_result == sorted_data

        print(f"--- データ数 n = {n} ---")
        print(f"  線形探索の比較回数   : {linear_count:>7}")
        print(f"  2 分探索の比較回数   : {binary_count:>7}")
        print(f"  選択ソートの比較回数 : {selection_count:>7}")
        print(f"  バブルソートの比較回数: {bubble_count:>7}")


if __name__ == "__main__":
    main()
