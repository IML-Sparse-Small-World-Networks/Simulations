"""Simulate minimum-weight paths in a cycle with random local shortcuts."""

import csv
import heapq
import json
import math
import secrets


import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def make_graph(n, ell, p, rng):
    """Generate the weighted cycle and shortcuts efficiently."""
    graph = [{} for _ in range(n)]

    # Cycle edges
    for i in range(n):
        j = (i + 1) % n
        weight = rng.exponential()
        graph[i][j] = weight
        graph[j][i] = weight

    # Largest eligible shortcut distance
    max_d = min(math.ceil(ell) - 1, n // 2)

    # Shortcut edges
    if p > 0:
        for i in range(n):
            limit = max_d

            # Avoid sampling antipodal pairs twice
            if n % 2 == 0 and i >= n // 2:
                limit = min(limit, n // 2 - 1)

            d = 1

            while True:
                d += rng.geometric(p)

                if d > limit:
                    break

                j = (i + d) % n
                weight = rng.exponential()

                graph[i][j] = weight
                graph[j][i] = weight

    return graph



def shortest_paths(graph, target, sources, n):
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
            path.append(current)

        paths[start] = path

    return paths


def main():
    n = 500000 # int(input("n (number of vertices): "))
    lambda_ = 1.0  # float(input("lambda: "))
    ell = n**(1/2) # float(input("ell: "))
    trials = 30 # int(input("trials: "))
    m = 30 # int(input("m: "))
    
    #show_plot = "y" # input("Plot first trial? (y/n): ").strip().lower() == "y"

    if n < 3 or m < 0 or trials < 1 or ell <= 1 or lambda_ < 0:
        raise ValueError("Require n >= 3, m >= 0, trials >= 1, ell > 1, lambda >= 0.")

    p = lambda_ / (2 * ell - 2)
    if p > 1:
        raise ValueError("Shortcut probability p must not exceed 1.")

    target = n // 2
    low = math.floor((n-m))
    high = math.floor((m))
    # Wrap source vertex labels around the cycle; avoid duplicates.
    #sources = sorted({v % n for v in range(low, high + 1)})
    sources = sorted({v % n for v in range(-m, m + 1)})

    rng = np.random.default_rng()
    with open("shortest_paths.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["trial", "paths"])
        for trial in range(1, trials + 1):
            print(f"Trial {trial}/{trials}: Generating graph...", flush=True)

            graph = make_graph(n, ell, p, rng)

            print(f"Trial {trial}/{trials}: Finding shortest paths...", flush=True)

            paths = shortest_paths(graph, target, sources, n)

            writer.writerow([trial, json.dumps(paths)])
            file.flush()

            #plot_graph(graph, paths, n)
            print(f"Trial {trial}/{trials}: Complete!", flush=True)

    print("Saved shortest_paths.csv")



if __name__ == "__main__":
    main()



'''
def plot_graph(graph, paths, n):
    """Draw cycle edges, shortcuts, and shortest paths."""

    # Convert adjacency list to NetworkX graph
    G = nx.Graph()
    G.add_nodes_from(range(n))

    for u, neighbors in enumerate(graph):
        for v, weight in neighbors.items():
            if u < v:
                G.add_edge(u, v, weight=weight)

    pos = nx.circular_layout(G)

    # Separate cycle edges from shortcuts
    cycle = [(i, (i + 1) % n) for i in range(n)]
    cycle_set = {frozenset(edge) for edge in cycle}

    shortcuts = [
        (u, v) for u, v in G.edges()
        if frozenset((u, v)) not in cycle_set
    ]

    # Collect edges belonging to shortest paths
    path_edges = set()

    for path in paths.values():
        for u, v in zip(path[:-1], path[1:]):
            path_edges.add(tuple(sorted((u, v))))

    plt.figure(figsize=(9, 9))

    # Draw vertices and labels
    nx.draw_networkx_nodes(
        G, pos, node_color="lightblue", node_size=50
    )
    nx.draw_networkx_labels(
        G, pos, font_size=7
    )

    # Draw cycle edges in black
    nx.draw_networkx_edges(
        G, pos, edgelist=cycle,
        edge_color="black", width=2
    )

    # Draw shortcuts in red
    nx.draw_networkx_edges(
        G, pos, edgelist=shortcuts,
        edge_color="red", width=1.5, alpha=0.7
    )

    # Highlight shortest paths in green
    nx.draw_networkx_edges(
        G, pos, edgelist=list(path_edges),
        edge_color="green", width=4
    )

    plt.title(f"Shortest paths to target (n={n})")
    plt.axis("off")
    plt.tight_layout()
    plt.show()

'''