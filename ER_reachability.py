from collections import deque
import numpy as np
import math
import networkx as nx
import matplotlib.pyplot as plt


r = np.random.default_rng(seed=123)

def bfs(G, n_, l_, p_, lambda_, start=0):
    n = n_
    visited = [False] * n
    parent = [-1] * n
    depth = [0] * n
    visited[start] = True
    queue = deque([start])
    discovered = 1

    expanded = set()
    L = int(l_)

    while queue:
        u = queue.popleft()

        # Create the cycle neighbors if they do not exist yet.
        for v in ((u - 1) % n, (u + 1) % n):
            G.setdefault(v, set())  # Preserve existing edges.
            G[u].add(v)
            G[v].add(u)

        # Generate shortcuts incident to u.
        for distance in range(2, L + 1):
            # A set avoids sampling the opposite vertex twice when n is even.
            candidates = {(u - distance) % n, (u + distance) % n}

            for v in candidates:
                if v in expanded:
                    # This edge was already sampled when v was processed.
                    continue

                if r.random() < p_:
                    # Create the shortcut endpoint only if the edge exists.
                    G.setdefault(v, set())
                    G[u].add(v)
                    G[v].add(u)

        expanded.add(u)


        for v in G[u]:
            if visited[v]:
                if v != parent[u]:
                    return depth[u] + 1, discovered   # cycle found
            else:
                visited[v] = True
                parent[v] = u
                depth[v] = depth[u] + 1
                discovered += 1
                queue.append(v)
    return max(depth), discovered    

def draw_graph(G, n):
    H = nx.Graph()
    H.add_nodes_from(G)

    for u, neighbors in G.items():
        for v in neighbors:
            H.add_edge(u, v)

    # Keep each vertex at its position on the original cycle.
    pos = {
        u: (math.cos(2 * math.pi * u / n),
            math.sin(2 * math.pi * u / n))
        for u in H.nodes()
    }

    edge_colors = [
        "gray" if (u - v) % n in (1, n - 1) else "red"
        for u, v in H.edges()
    ]

    plt.figure(figsize=(8, 8))
    nx.draw_networkx(
        H,
        pos=pos,
        with_labels=True,
        node_color="lightblue",
        node_size=600,
        edge_color=edge_colors,
        width=2,
        font_size=11,
    )
    plt.title("Generated graph — cycle edges: gray; shortcuts: red")
    plt.axis("equal")
    plt.axis("off")
    plt.tight_layout()
    plt.show()

def main():
    start = 0
    n = 50 + 50
    lambda_ = 1/4
    G = {start: set()}
    p = (lambda_ / (2*n - 2)) * 2
    l = n / math.log(n)

    result = bfs(G, n, l, p, lambda_, start)
    print(result)
    draw_graph(G, n)

if __name__ == "__main__":
        main()