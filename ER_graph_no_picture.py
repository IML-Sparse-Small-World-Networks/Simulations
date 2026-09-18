import numpy as np
import matplotlib.pyplot as plt

import Dijkstras_Algorithm as Dijkstras
from datetime import datetime

def main():
    # parameters
    n = 1000
    l = n/10
    alpha = 5
    p = alpha/n


    now = datetime.now().second

    # random graph
    r = np.random.default_rng(seed=now)
    A = np.zeros((n, n), dtype=int)

    for  i in range(n):
        j = (i + 1) % n
        A[i, j] = 1
        A[j, i] = 1

    # generating shortcuts

    shortcuts = []

    for i in range(n):
        for j in range(i+1, n): # j > i
            distance = min((j-i), n - (j-i))

            if (2 <= distance <= l):
                if r.random() < p:
                    A[i, j] = 1
                    A[j, i] = 1
                    shortcuts.append((i, j))
    # weights
    rate = 1.0  # lambda
    scale = 1 / rate

    W = np.zeros((n, n), dtype=float)
    mu = l * alpha/n

    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] == 1:
                is_neighbor = (j == i + 1) or (i == 0 and j == n - 1)

                if is_neighbor:
                    weight = r.exponential(scale=scale)
                else:
                    weight = mu * r.exponential(scale=scale)

                W[i, j] = weight
                W[j, i] = weight


    print("Number of vertices:", n)
    print("Shortcut probability:", p)
    print("Number of shortcut edges:", len(shortcuts))
    #print("Shortcut edges:", shortcuts)
    print("Adjacency matrix:")
    #print(A)

    # drawing graph with network


    cycle_edges = []
    for i in range(n):
        cycle_edges.append((i, (i+1)%n))


    plt.figure(figsize=(10, 10))


    graph_vertices = []
    for i in range(n):
        graph_vertices.append(i)


    start_vertex = 0
    end_vertex = n//2
    distances, predecessors = Dijkstras.dijkstra(W, graph_vertices, n)

    path, path_weights = Dijkstras.get_path(
        W,
        predecessors,
        start_vertex,
        end_vertex
    )

    print("Vertex path:", path)
    #print("Path weights list:", path_weights)
    print("Total weights:", sum(path_weights))


    shortcut_edges = 0
    edges = []
    for i in range(len(path)-1):
        edges.append((path[i], path[i+1]))
        if (abs(path[i] - path[i+1]) > 1):
            shortcut_edges += 1

    print("len path:", len(path))
    print("num shortcut edges: ", shortcut_edges)


if __name__ == "__main__":
    main()
