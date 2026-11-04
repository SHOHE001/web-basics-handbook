"""FE Chapter 1 の計算問題を Python で確かめる。

- CPU の MIPS 値
- キャッシュメモリを使ったときの実効アクセス時間
- HDD の平均回転待ち時間

数値を書き換えれば、問題集の答え合わせにそのまま使える。

使い方:
    python cpu_calc.py
"""


def mips(clock_hz: float, cpi: float) -> float:
    """1 秒あたりの命令数（百万命令単位）を返す。"""
    instructions_per_sec = clock_hz / cpi
    return instructions_per_sec / 1e6


def effective_access_time(cache_ns: float, memory_ns: float, hit_rate: float) -> float:
    """実効アクセス時間（ナノ秒）を返す。hit_rate は 0〜1。"""
    return cache_ns * hit_rate + memory_ns * (1 - hit_rate)


def average_rotational_wait_ms(rpm: float) -> float:
    """平均回転待ち時間（ミリ秒）を返す。平均すると半周待つ。"""
    one_rotation_ms = 60 / rpm * 1000
    return one_rotation_ms / 2


def main() -> None:
    # 例題 1: 2 GHz、CPI = 4
    value = mips(clock_hz=2e9, cpi=4)
    print(f"MIPS: {value:.0f} MIPS（1 命令あたり {1 / (value * 1e6) * 1e9:.1f} ナノ秒）")

    # 例題 2: キャッシュ 10ns、主記憶 60ns、ヒット率 90%
    eat = effective_access_time(cache_ns=10, memory_ns=60, hit_rate=0.9)
    print(f"実効アクセス時間: {eat:.1f} ナノ秒")

    # 例題 3: 毎分 6,000 回転の HDD
    wait = average_rotational_wait_ms(rpm=6000)
    print(f"平均回転待ち時間: {wait:.1f} ミリ秒")


if __name__ == "__main__":
    main()
