"""py ".\reuse graph, heapq, adj list\ER_graph_no_picture_reuse_graph.py"""
import math
import time
import numpy as np
import dijkstras_heapq as Dijkstras


def create_graph(n, l, p):
    """Create one weighted cycle with random shortcuts, no adjacency matrix."""
    r = np.random.default_rng()
    adj = [{} for _ in range(n)]

    # Connect each vertex to its two neighbors on the cycle.
    for i in range(n):
        j = (i + 1) % n
        adj[i][j] = None
        adj[j][i] = None

    # Generate shortcuts using geometric jumps over unsuccessful trials.
    shortcuts = []
    max_distance = min(math.floor(l), n // 2)

    if p > 0:
        for distance in range(2, max_distance + 1):
            # At distance n/2, each pair would otherwise appear twice.
            num_pairs = n // 2 if 2 * distance == n else n
            i = int(r.geometric(p)) - 1
            while i < num_pairs:
                j = (i + distance) % n

                adj[i][j] = None
                adj[j][i] = None
                shortcuts.append((i, j))

                i += int(r.geometric(p))

    # Assign one exponential base weight per undirected edge.
    shortcut_set = {tuple(sorted(edge)) for edge in shortcuts}
    edges = []
    for i in range(n):
        for j in adj[i]:
            if i < j:
                base_weight = float(r.exponential(scale=1.0))
                is_shortcut = (i, j) in shortcut_set
                edges.append((i, j, base_weight, is_shortcut))

    return edges, shortcuts


def make_adjacency_list(n, edges, alpha):
    """Keep the same graph and base weights, scaling shortcut weights."""
    graph = [[] for _ in range(n)]
    for u, v, base_weight, is_shortcut in edges:
        weight = base_weight * alpha if is_shortcut else base_weight
        graph[u].append((v, weight))
        graph[v].append((u, weight))
    return graph


def main():
    n = 100000
    l = n // 10
    lambda_ = 10
    p = lambda_ / (2 * l - 2)
    alpha_values = [1, l, l ** 2]

    if n < 4 or l < 2 or not (0 < p <= 1):
        raise ValueError('Require n >= 4, l >= 2, and 0 < p <= 1')

    # One timer includes graph creation, list construction, and 30 searches.
    start_time = time.perf_counter()
    edges, shortcuts = create_graph(n, l, p)
    print(f'Created one graph with {n} vertices and {len(shortcuts)} shortcuts')

    for alpha in alpha_values:
        print(f'\nStarting alpha = {alpha} ...')
        graph = make_adjacency_list(n, edges, alpha)

        for trial in range(10):
            start_vertex = trial
            end_vertex = (start_vertex + n // 2) % n
            distances, _ = Dijkstras.dijkstra(graph, range(n), n, start_vertex)
            print(
                f'Trial {trial + 1}: start = {start_vertex}, '
                f'end = {end_vertex}, '
                f'shortest distance = {distances[end_vertex]:.4f}'
            )

    total_time = time.perf_counter() - start_time
    print(f'\nFinished! Total runtime: {total_time:.6f} seconds')


if __name__ == '__main__':
    main()
