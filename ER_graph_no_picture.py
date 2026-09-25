import numpy as np
import csv
import matplotlib.pyplot as plt

import Dijkstras_Algorithm as Dijkstras
from datetime import datetime

def main(n_, l_, p_, lambda__, alpha_):
    # parameters
    
    n = n_                              # number of vertices
    l = l_                              # shortcut range
    p = p_                              # probability of shortcut Binom dist
    lambda_ = lambda__                  # new lambda var for alpha
    alpha = alpha_                      # shortcut constant multiplier passed directly to main function
    

    # random graph
    now = datetime.now().second
    r = np.random.default_rng(seed=now)
    A = np.zeros((n, n), dtype=int)

    for  i in range(n):
        j = (i + 1) % n                 # underlying cycle
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
                is_neighbor = (j == i + 1) or (i == 0 and j == n - 1)

                if is_neighbor:
                    weight = r.exponential(scale=scale)
                else:
                    weight = alpha * r.exponential(scale=scale)

                W[i, j] = weight
                W[j, i] = weight


    print("Number of vertices:", n)
    print("Shortcut probability:", p)
    print("Number of shortcut edges:", len(shortcuts))
    #print("Shortcut edges:", shortcuts)
    #print("Adjacency matrix:")
    #print(A)

    # drawing graph with network


    cycle_edges = []
    for i in range(n):
        cycle_edges.append((i, (i+1)%n))


    #plt.figure(figsize=(10, 10))


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

    # record trial data
    data = [n, l, p, lambda_, alpha, len(shortcuts), sum(path_weights), len(path), shortcut_edges]
    with open('data.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)

if __name__ == "__main__":
    n_ = 1000                            # number of vertices
    l_ = n_/10                            # shortcut range
    p_ = 5/n_                             # probability of shortcut Binom dist
    lambda__ = 10                        # new lambda var for alpha
    alpha_1 = (l_ * lambda__)/(2*l_-2)      # shortcut constant multiplier passed directly to main function
    alpha_2 = (l_**2 * lambda__)/(2*l_-2)   # second alpha

    with open('data.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
            "n",
            "l",
            "p",
            "lambda",
            "alpha",
            "shortcuts",
            "path_weight",
            "len_path",
            "shortcuts_taken",
            ])
            writer.writerow([f"alpha = {alpha_1}", "", "", "", "", "", "", "", ""])

    print("Starting alpha = (l * lambda_) / (2*l - 2)...")
    for i in range(10):
        print(f"Starting run {i + 1}...")
        main(n_, l_, p_, lambda__, alpha_1)

    with open('data.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([f"alpha = {alpha_2}", "", "", "", "", "", "", "", ""])

    print("Starting alpha = (l**2 * lambda_) / (2*l - 2)...")
    for i in range(10):
        print(f"Starting run {i + 1}...")
        main(n_, l_, p_, lambda__, alpha_2)

    print("finished!")

    
