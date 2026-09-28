import numpy as np
import csv
import matplotlib.pyplot as plt
import networkx as nx

import BFS as BFS

def main(n_, l_, p_, lambda__, alpha_):
    # parameters
    
    n = n_                              # number of vertices
    l = l_                              # shortcut range
    p = p_                              # probability of shortcut Binom dist
    lambda_ = lambda__                  # new lambda var for alpha
    alpha = alpha_                      # shortcut constant multiplier passed directly to main function

    # random graph
    rng = np.random.default_rng()
    random_num = rng.integers(1, 5001)
    r = np.random.default_rng(seed=random_num)
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

    # drawing graph with network

    G = nx.Graph()
    edge_list = BFS.bfs(A, n, 0)
    G.add_edges_from(edge_list)
    bfs_tree = nx.bfs_tree(G, source=0)
    pos = nx.drawing.layout.bfs_layout(G, start=0)
    plt.figure(figsize=(7, 7))
    nx.draw(bfs_tree, pos, with_labels=True, node_size=300, node_color="lightblue", font_size=12, font_weight="bold", arrows=True)
    plt.title("BFS Tree Visualization")
    plt.savefig("bfs_tree.png", dpi=300, bbox_inches="tight")

    

    

    '''
    cycle_edges = []
    for i in range(n):
        cycle_edges.append((i, (i+1)%n))


    #plt.figure(figsize=(10, 10))


    graph_vertices = []
    for i in range(n):
        graph_vertices.append(i)
        
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
    '''

if __name__ == "__main__":
    '''
    Standarized the variables with "_" suffix to pass to main() function
    Two for loops. One for l and one for l**2
    Automatically outputs data to 'data.csv'
    Run 'script.py' to generate bar graphs
    If you change the '10' in the for loops below, change 
                    the '10' in the script.py for loops as well
    '''
    
    n_ = 50                               # number of vertices
    l_ = int(n_/10)                              # shortcut range
    lambda__ = 10                           # new lambda var for alpha
    p_ = lambda__/(2*l_ - 2)                 # probability of shortcut Binom dist    
    alpha_1 = 1                             # shortcut constant multipliers passed directly to main function
    main(n_, l_, p_, lambda__, alpha_1)


    '''
    alpha_2 = l_
    alpha_3 = l_**2


    with open('data1.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["n","l","p","lambda","alpha","shortcuts","path_weight","len_path","shortcuts_taken",])
            writer.writerow([f"alpha = {alpha_1}", "", "", "", "", "", "", "", ""])

    print("Starting alpha = 1 ...")
    for i in range(10):
        print(f"Starting run {i + 1}...")
        main(n_, l_, p_, lambda__, alpha_1)
    
    with open('data2.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([f"alpha = {alpha_2}", "", "", "", "", "", "", "", ""])

    print("Starting alpha = l ...")
    for i in range(10):
        print(f"Starting run {i + 1}...")
        main(n_, l_, p_, lambda__, alpha_2)

    with open('data3.csv', mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([f"alpha = {alpha_2}", "", "", "", "", "", "", "", ""])
    

    print("Starting alpha = l**2 ...")
    for i in range(10):
        print(f"Starting run {i + 1}...")
        main(n_, l_, p_, lambda__, alpha_3)
    
    print("finished!")
    '''
    
