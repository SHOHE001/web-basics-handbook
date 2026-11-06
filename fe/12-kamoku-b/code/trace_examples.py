"""FE Chapter 12: 擬似言語の例を Python に置き換えて、トレース表を表示する。

擬似言語の配列は「要素番号 1 から」、Python のリストは「0 から」。
ここでは擬似言語の書き方に合わせて i を 1 から回し、
リストを読むときだけ data[i - 1] として 1 つずらしている。

使い方:
    python trace_examples.py
"""


def gcd_with_trace(a: int, b: int) -> int:
    """擬似言語:
    ○整数型: gcd(整数型: a, 整数型: b)
      整数型: r
      while (b ≠ 0)
        r ← a mod b
        a ← b
        b ← r
      endwhile
      return a
    """
    print(f"gcd({a}, {b}) のトレース")
    print(f"{'回':>3} | {'b≠0':^5} | {'r':>4} | {'a':>4} | {'b':>4}")
    print(f"{'開始':>2} | {'':^5} | {'':>4} | {a:>4} | {b:>4}")
    count = 0
    while b != 0:          # while (b ≠ 0)
        count += 1
        r = a % b          # r ← a mod b
        a = b              # a ← b
        b = r              # b ← r
        print(f"{count:>3} | {'真':^4} | {r:>4} | {a:>4} | {b:>4}")
    print(f"{count + 1:>3} | {'偽':^4} | → ループを抜ける")
    print(f"戻り値: {a}\n")
    return a


def count_above_with_trace(data: list[int], border: int) -> int:
    """擬似言語:
    ○整数型: countAbove(整数型の配列: data, 整数型: border)
      整数型: count, i
      count ← 0
      for (i を 1 から dataの要素数 まで 1 ずつ増やす)
        if (data[i] > border)
          count ← count + 1
        endif
      endfor
      return count
    """
    print(f"countAbove({data}, {border}) のトレース")
    print(f"{'i':>3} | {'data[i]':>7} | {'data[i] > border':^16} | {'count':>5}")
    count = 0
    for i in range(1, len(data) + 1):      # i を 1 から 要素数 まで
        value = data[i - 1]                # 擬似言語の data[i] は Python では data[i - 1]
        is_above = value > border          # if (data[i] > border)
        if is_above:
            count += 1                     # count ← count + 1
        print(f"{i:>3} | {value:>7} | {'真' if is_above else '偽':^15} | {count:>5}")
    print(f"戻り値: {count}\n")
    return count


def main() -> None:
    assert gcd_with_trace(48, 18) == 6
    assert count_above_with_trace([3, 8, 5, 10], 5) == 2

    # 境界値の確認: border と同じ値（5）は数えない
    assert count_above_with_trace([5, 5, 6], 5) == 1


if __name__ == "__main__":
    main()
