"""Simulate weighted shortest paths and save per-trial summaries only."""

import csv
import heapq
import json
import math

import numpy as np


def make_graph(n, ell, p, rng):
    """Undirected cycle with independent Exp(1) edge weights and local shortcuts."""
    graph = [{} for _ in range(n)]

    for i in range(n):
        j = (i + 1) % n
        weight = rng.exponential()
        graph[i][j] = graph[j][i] = weight

    max_d = min(math.ceil(ell) - 1, n // 2)
    if p > 0:
        for i in range(n):
            limit = max_d
            if n % 2 == 0 and i >= n // 2:
                limit = min(limit, n // 2 - 1)

            d = 1
            while True:
                d += rng.geometric(p)  # Skip failed Bernoulli shortcut trials
                if d > limit:
                    break
                j = (i + d) % n
                weight = rng.exponential()
                graph[i][j] = graph[j][i] = weight

    return graph


def shortest_paths(graph, target, sources):
    """Dijkstra from the target; stop when all sources are finalized."""
    n = len(graph)
    distances = [math.inf] * n
    parents = [None] * n
    distances[target] = 0
    heap = [(0, target)]
    remaining = set(sources)

    while heap and remaining:
        distance, u = heapq.heappop(heap)
        if distance > distances[u]:
            continue
        remaining.discard(u)

        for v, weight in graph[u].items():
            new_distance = distance + weight
            if new_distance < distances[v]:
                distances[v] = new_distance
                parents[v] = u
                heapq.heappush(heap, (new_distance, v))

    paths = {}
    for start in sources:
        path = [start]
        current = start
        while current != target:
            current = parents[current]
            if current is None:
                raise RuntimeError(f"No path from {start} to {target}")
            path.append(current)
        paths[start] = path
    return paths


def average_distance(paths):
    """Average hop count along the minimum-weight paths."""
    return sum(len(path) - 1 for path in paths) / len(paths)


def longest_common_subsequence(paths):
    """Common suffix of paths in the same shortest-path tree."""
    common = []
    for vertices in zip(*(reversed(path) for path in paths)):
        if len(set(vertices)) != 1:
            break
        common.append(vertices[0])
    return common[::-1]


def main():
    n = 1000000
    lambda_ = 1.5
    ell = math.sqrt(n)
    trials = 30
    m = 30

    if n < 3 or m < 0 or trials < 1 or ell <= 1 or lambda_ < 0:
        raise ValueError("Require n >= 3, m >= 0, trials >= 1, ell > 1, lambda >= 0.")
    p = lambda_ / (2 * ell - 2)
    if p > 1:
        raise ValueError("Shortcut probability p must not exceed 1.")

    target = n // 2
    sources = sorted({v % n for v in range(-m, m + 1)})
    rng = np.random.default_rng()

    with open("path_summary.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["trial", "num_paths", "average_distance_hops",
                         "common_subsequence", "common_subsequence_vertices"])

        for trial in range(1, trials + 1):
            print(f"Trial {trial}/{trials}: Generating graph...", flush=True)
            graph = make_graph(n, ell, p, rng)
            print(f"Trial {trial}/{trials}: Finding shortest paths...", flush=True)
            paths = shortest_paths(graph, target, sources)

            path_list = list(paths.values())
            common = longest_common_subsequence(path_list)
            writer.writerow([trial, len(path_list), average_distance(path_list),
                             json.dumps(common), len(common)])
            file.flush()
            del graph, paths
            print(f"Trial {trial}/{trials}: Complete!", flush=True)

    print("Saved path_summary.csv")


if __name__ == "__main__":
    main()
