import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from networkx import from_numpy_array, predecessor

import Dijkstras_Algorithm as Dijkstras

def main():
    # parameters
    n = 100
    l = n/10
    alpha = 3
    p = alpha/n

    # random graph
    r = np.random.default_rng(seed=123)
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

        for i in range(n):
            for j in range(i + 1, n):
                if A[i, j] == 1:
                    weight = r.exponential(scale=scale)
                    W[i, j] = weight
                    W[j, i] = weight

    print("Number of vertices:", n)
    print("Shortcut probability:", p)
    print("Number of shortcut edges:", len(shortcuts))
    print("Shortcut edges:", shortcuts)
    print("Adjacency matrix:")
    print(A)

    # drawing graph with network
    G = from_numpy_array(W)

    pos = nx.circular_layout(G)

    cycle_edges = []
    for i in range(n):
        cycle_edges.append((i, (i+1)%n))


    plt.figure(figsize=(10, 10))

    nx.draw_networkx_nodes(G,pos,node_size=40)

    # original edges
    nx.draw_networkx_edges(G,pos,edgelist=cycle_edges,edge_color="steelblue",width=0.5)
    # shortcut edges
    nx.draw_networkx_edges(G,pos,edgelist=shortcuts,edge_color="red",style="dashed",width=2,alpha=0.6)



    graph_vertices = []
    for i in range(n):
        graph_vertices.append(i)


    start_vertex = 0
    end_vertex = n//2
    distances, predecessors = Dijkstras.dijkstra(W, graph_vertices, n)

    path = Dijkstras.get_path(
        predecessors,
        start_vertex,
        end_vertex
    )


    edges = []
    for i in range(len(path)-1):
        edges.append((path[i], path[i+1]))

    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color="green", width=5, alpha=0.6)
    plt.title(
        f"Small-World Network: n={n}, l={l}, α={alpha}"
    )
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    main()
