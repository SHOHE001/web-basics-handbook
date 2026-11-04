"""AP Chapter 5: 動的計画法とダイクストラ法を Python で書く。

- フィボナッチ数: 素朴な再帰とメモ化で、呼び出し回数を比べる
- ナップサック問題（各品物 1 個まで）
- ダイクストラ法（重みが負でないグラフの最短距離）

使い方:
    python dp_graph.py
"""

import heapq

calls = 0


def fib_naive(n: int) -> int:
    global calls
    calls += 1
    if n <= 2:
        return 1
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_memo(n: int, memo: dict[int, int]) -> int:
    global calls
    calls += 1
    if n in memo:
        return memo[n]
    memo[n] = 1 if n <= 2 else fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]


def knapsack(items: list[tuple[int, int]], capacity: int) -> int:
    """items は (重さ, 価値) のリスト。最大の価値を返す。"""
    best = [0] * (capacity + 1)  # best[w]: 重さの上限が w のときの最大の価値
    for weight, value in items:
        # 大きい方から更新する。小さい方からだと同じ品物を何度も使ってしまう
        for w in range(capacity, weight - 1, -1):
            best[w] = max(best[w], best[w - weight] + value)
    return best[capacity]


def dijkstra(graph: dict[str, dict[str, int]], start: str) -> dict[str, int]:
    """各点への最短距離を返す。graph[u][v] は u から v への辺の重み。"""
    dist = {node: float("inf") for node in graph}
    dist[start] = 0
    queue = [(0, start)]  # (距離, 点) の優先度付きキュー
    done = set()
    while queue:
        d, u = heapq.heappop(queue)  # 未確定の中で距離が最小の点
        if u in done:
            continue
        done.add(u)  # 確定
        for v, weight in graph[u].items():
            if d + weight < dist[v]:
                dist[v] = d + weight
                heapq.heappush(queue, (dist[v], v))
    return dist


def main() -> None:
    global calls
    for n in (10, 20, 25):
        calls = 0
        value = fib_naive(n)
        naive_calls = calls
        calls = 0
        assert fib_memo(n, {}) == value
        print(f"fib({n}) = {value}: 素朴な再帰 {naive_calls} 回、メモ化 {calls} 回の呼び出し")

    items = [(2, 3), (3, 4), (4, 5), (5, 6)]  # (重さ, 価値)
    print(f"\nナップサック（上限 5）: 最大の価値 {knapsack(items, 5)}")  # 重さ 2 と 3 で価値 7

    graph = {
        "A": {"B": 4, "C": 1},
        "B": {"D": 1},
        "C": {"B": 2, "D": 5},
        "D": {},
    }
    print("\nダイクストラ法（A から）:", dijkstra(graph, "A"))  # A→C→B→D が 4


if __name__ == "__main__":
    main()
