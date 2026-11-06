"""AP Chapter 1 の計算を Python で確かめる。

- 情報量
- 待ち行列（M/M/1）の待ち時間と応答時間
- パイプラインの所要サイクル数
- アムダールの法則

使い方:
    python tech_calc.py
"""

import math


def information(p: float) -> float:
    """確率 p の出来事を知ったときの情報量（ビット）。"""
    return -math.log2(p)


def mm1(service_time: float, utilization: float) -> tuple[float, float]:
    """(平均待ち時間, 平均応答時間) を返す。"""
    wait = utilization / (1 - utilization) * service_time
    return wait, wait + service_time


def pipeline_cycles(stages: int, instructions: int) -> int:
    """k 段のパイプラインで n 命令を処理するサイクル数。"""
    return stages + (instructions - 1)


def amdahl(parallel_ratio: float, n: int) -> float:
    """並列化による全体の性能向上（倍）。"""
    return 1 / ((1 - parallel_ratio) + parallel_ratio / n)


def main() -> None:
    print(f"コインの表   : {information(1 / 2):.2f} ビット")
    print(f"サイコロの 1 : {information(1 / 6):.2f} ビット")

    print("\n利用率と待ち時間（サービス時間 1 秒）")
    for rho in (0.5, 0.8, 0.9, 0.95):
        wait, response = mm1(1.0, rho)
        print(f"  ρ = {rho:.2f}: 待ち {wait:5.1f} 秒、応答 {response:5.1f} 秒")

    print(f"\n5 段パイプラインで 100 命令: {pipeline_cycles(5, 100)} サイクル")

    print("\n80% が並列化できる処理")
    for n in (2, 4, 8, 1000):
        print(f"  {n:>4} 並列: {amdahl(0.8, n):.2f} 倍")


if __name__ == "__main__":
    main()
