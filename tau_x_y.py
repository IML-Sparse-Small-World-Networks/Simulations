import heapq
import math
import secrets

import numpy as np
#import matplotlib.pyplot as plt
#import networkx as nx


def dijkstra(adj, start):
    distances = [math.inf] * len(adj)
    predecessors = [None] * len(adj)
    distances[start] = 0.0

    queue = [(0.0, start)]

    while queue:
        distance, u = heapq.heappop(queue)

        if distance > distances[u]:
            continue

        for v, weight in adj[u].items():
            new_distance = distance + weight

            if new_distance < distances[v]:
                distances[v] = new_distance
                predecessors[v] = u
                heapq.heappush(queue, (new_distance, v))

    return distances, predecessors


def get_path(adj, predecessors, start, end):
    path = []
    current = end

    while current is not None:
        path.append(current)
        if current == start:
            break
        current = predecessors[current]

    if path[-1] != start:
        return [], []

    path.reverse()

    path_weights = [
        adj[u][v]
        for u, v in zip(path, path[1:])
    ]

    return path, path_weights


def main():
    # Parameters
    n = 100000
    l = n / math.log(n)
    lambda_ = 1/4
    p = lambda_ / (2*l - 2)

    r = np.random.default_rng(seed=secrets.randbits(64))

    # Weighted adjacency list.
    # None temporarily marks an edge whose weight is not assigned yet.
    adj = [{} for _ in range(n)]

    # Original cycle edges
    cycle_edges = []

    for i in range(n):
        j = (i + 1) % n
        adj[i][j] = None
        adj[j][i] = None
        cycle_edges.append((i, j))

    # Generate shortcuts, sampling each undirected pair once.
    shortcuts = []

    for i in range(n):
        for j in range(i + 1, n):
            distance = min(j - i, n - (j - i))

            if 2 <= distance <= l and r.random() < p:
                adj[i][j] = None
                adj[j][i] = None
                shortcuts.append((i, j))

    # Assign one weight per undirected edge.
    rate = 1.0
    scale = 1 / rate
    #mu = l**2 * alpha / n

    for i in range(n):
        for j in sorted(adj[i]):
            if j <= i:
                continue

            is_neighbor = min(j - i, n - (j - i)) == 1
            weight = r.exponential(scale=scale)

            #if not is_neighbor:
            #    weight *= mu

            adj[i][j] = weight
            adj[j][i] = weight

    '''
    print("Number of vertices:", n)
    print("Shortcut probability:", p)
    print("Number of shortcut edges:", len(shortcuts))
    print("Shortcut edges:", shortcuts)

    print("Weighted adjacency list (vertex: {neighbor: weight}):")
    for u, neighbors in enumerate(adj):
        print(f"{u}: {neighbors}")

    
    # Construct NetworkX graph directly from the adjacency list.
    G = nx.Graph()
    G.add_nodes_from(range(n))

    for u, neighbors in enumerate(adj):
        for v, weight in neighbors.items():
            if u < v:
                G.add_edge(u, v, weight=weight)
    
    pos = nx.circular_layout(G)

    plt.figure(figsize=(10, 10))
    nx.draw_networkx_nodes(G, pos, node_size=40)

    nx.draw_networkx_edges(
        G, pos,
        edgelist=cycle_edges,
        edge_color="steelblue",
        width=0.05,
    )

    nx.draw_networkx_edges(
        G, pos,
        edgelist=shortcuts,
        edge_color="red",
        style="dashed",
        width=0.1,
        alpha=0.6,
    )
    '''

    # Find shortest path using the adjacency list.
    start_vertex = 0
    end_vertex = n // 2

    distances, predecessors = dijkstra(adj, start_vertex)
    path, path_weights = get_path(
        adj, predecessors, start_vertex, end_vertex
    )

    #print("Vertex path:", path)
    #print("Path weights list:", path_weights)
    #print("Total weights:", sum(path_weights))

    path_edges = list(zip(path, path[1:]))

    shortcut_count = sum(
        min(abs(u - v), n - abs(u - v)) > 1
        for u, v in path_edges
    )

    print("len path:", len(path))
    print("num shortcut edges:", shortcut_count)

    '''
    nx.draw_networkx_edges(
        G, pos,
        edgelist=path_edges,
        edge_color="green",
        width=10,
        alpha=0.6,
    )

    plt.title(f"Small-World Network: n={n}, l={l}, α={alpha}")
    plt.axis("off")
    plt.show()
    '''


if __name__ == "__main__":
    main()
