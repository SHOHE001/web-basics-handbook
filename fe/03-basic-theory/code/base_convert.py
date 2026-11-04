"""FE Chapter 3 の基礎理論を Python で確かめる。

- 基数変換（2 進・10 進・16 進）
- 8 ビットの 2 の補数
- シフト演算
- 小数の誤差

使い方:
    python base_convert.py
"""

from decimal import Decimal


def to_binary_by_division(n: int) -> str:
    """2 で割り続けて余りを下から読む、手計算と同じ手順で 2 進数にする。"""
    if n == 0:
        return "0"
    remainders = []
    while n > 0:
        remainders.append(str(n % 2))
        n //= 2
    return "".join(reversed(remainders))  # 下から読む＝逆順にする


def twos_complement_8bit(n: int) -> str:
    """-128〜127 の整数を 8 ビットの 2 の補数表現にする。"""
    if not -128 <= n <= 127:
        raise ValueError("8 ビットで表せる範囲は -128〜127")
    return format(n & 0xFF, "08b")  # 0xFF との AND で下位 8 ビットを取り出す


def main() -> None:
    print("== 基数変換 ==")
    print("13 を 2 進数に（割り算の手順）:", to_binary_by_division(13))
    print("13 を 2 進数に（bin 関数）    :", bin(13))
    print("2 進数 1011 を 10 進数に       :", int("1011", 2))
    print("2 進数 10101111 を 16 進数に   :", hex(int("10101111", 2)))
    print("16 進数 FF を 10 進数に        :", int("FF", 16))

    print("\n== 2 の補数（8 ビット）==")
    for n in (5, -5, 127, -128):
        print(f"{n:>5} → {twos_complement_8bit(n)}")

    print("\n== シフト演算 ==")
    x = 6
    print(f"{x} を左に 2 ビットシフト → {x << 2}（{x} × 4）")
    print(f"{x} を右に 1 ビットシフト → {x >> 1}（{x} ÷ 2）")
    print(f"{x} × 10 を シフトと足し算で → {(x << 3) + (x << 1)}")

    print("\n== 小数の誤差 ==")
    print("0.1 + 0.2 =", 0.1 + 0.2)
    print("Decimal('0.1') + Decimal('0.2') =", Decimal("0.1") + Decimal("0.2"))


if __name__ == "__main__":
    main()
