import math
import secrets
import csv
import numpy as np

import data_collection
#import matplotlib.pyplot as plt
#import networkx as nx


def main(n_, l_, lambda__, p_, t_):
    # Parameters
    n =  n_
    l = l_
    lambda_ = lambda__
    p = p_
    t = t_
    rate = 1.0
    scale = 1 / rate
    num_edges = 0
    r = np.random.default_rng(seed=secrets.randbits(64))

    # Weighted adjacency list.
    adj = [{} for _ in range(n)]

    # Original cycle edges.
    cycle_edges = []

    for i in range(n):
        j = (i + 1) % n
        weight = r.exponential(scale=scale)
        if (weight < t):
            num_edges += 1
        adj[j][i] = weight
        cycle_edges.append((i, j))

    # Generate shortcuts with independent probability p
    # for every pair at cyclic distance 2 <= distance <= l.
    shortcuts = []
    max_distance = min(math.floor(l), n // 2)
    

    if p > 0:
        for distance in range(2, max_distance + 1):
            # Avoid counting opposite pairs twice when n is even.
            num_pairs = n // 2 if 2 * distance == n else n

            i = int(r.geometric(p)) - 1

            while i < num_pairs:
                j = (i + distance) % n

                # Assign one exponential weight per undirected edge.
                weight = r.exponential(scale=scale)
                if (weight < t):
                    num_edges += 1
                adj[i][j] = weight
                adj[j][i] = weight
                shortcuts.append((i, j))
                i += int(r.geometric(p))

    print("Number of vertices:", n)
    print("Shortcut probability:", p)
    print("Number of shortcut edges:", len(shortcuts))
    print("T: ", t)
    print("Num edges < t: ", num_edges)
    print("Average number edges w(i,j) < t: ", str(2 * num_edges / n))
    data = [t, 2 * num_edges / n]
    with open("data.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(data)

   

if __name__ == "__main__":
    n = 300000  # Increase to 100000 for larger simulations.
    l = n / math.log(n)
    lambda_ = 1 
    p = lambda_ / (2 * l - 2)
    t_array = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
    trials = 10
    with open("data.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow("")
    
    for t in t_array:
        header1 = ["n", "l", "lambda", "p", "t"]
        header2 = [n, l, lambda_, p, t]
        with open("data.csv", mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header1)
            writer.writerow(header2)
        for _ in range(trials):
            main(n, l, lambda_, p, t)

    data_collection.collect_data(trials)
    data_collection.plot_data(n)






'''
# Construct NetworkX graph from the weighted adjacency list.
G = nx.Graph()
G.add_nodes_from(range(n))

for u, neighbors in enumerate(adj):
    for v, weight in neighbors.items():
        if u < v:
            G.add_edge(u, v, weight=weight)

# Place vertices in cycle order around a circle.
pos = nx.circular_layout(G)

plt.figure(figsize=(10, 10))

nx.draw_networkx_nodes(
    G,
    pos,
    node_size=12 if n <= 1000 else 1,
    node_color="steelblue",
)

nx.draw_networkx_edges(
    G,
    pos,
    edgelist=cycle_edges,
    edge_color="steelblue",
    width=0.8,
    label="Cycle edges",
)

nx.draw_networkx_edges(
    G,
    pos,
    edgelist=shortcuts,
    edge_color="red",
    width=0.6,
    alpha=0.6,
    label="Shortcuts",
)

plt.title(
    f"Small-World Network: n={n}, "
    f"ℓ={l:.2f}, λ={lambda_}"
)
plt.legend()
plt.axis("off")
plt.tight_layout()
plt.show()
'''
