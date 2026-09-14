import sys
import csv
import numpy as np
import secrets

import opt_Dijkstras_Algorithm as Dijkstras

'''
    @params
    Trial n l p start_vertex end_vertex 

    Trial = trial #
    n = number nodes
    l = up to how many neighboring nodes we can add a shortcut
    p = probability of a shortcut existing between nodes
    start_vertex = starting vertex
    end_vertex = ending vertex

'''

def run_trial(trial, n, l, p, start_vertex, end_vertex, rng=None):
    """
    Build one random ring + shortcuts graph, run Dijkstra, and return the
    result row as a list: [trial, n, l, p, start_vertex, end_vertex,
    FirstPassageTime, Distance].
 
    Returns the row directly instead of writing to disk itself, so callers
    (e.g. simulate.py) can batch many rows into one open file handle rather
    than opening/closing data.csv once per trial.
    """
    if rng is None:
        # np.random.default_rng() already seeds itself from OS entropy;
        # no need to burn cycles drawing a number up to 2**10000 first.
        rng = np.random.default_rng()
 
    l_int = int(l)
    rate = 1.0
    scale = 1 / rate
 
    # Build the adjacency list directly - no dense n x n matrix. The graph
    # is sparse by construction (ring + up to l shortcuts per side), so a
    # dense matrix wastes O(n^2) memory and time for O(n*l) worth of edges.
    adj = [[] for _ in range(n)]
 
    def add_edge(i, j):
        weight = rng.exponential(scale=scale)
        adj[i].append((j, weight))
        adj[j].append((i, weight))
 
    # ring edges
    for i in range(n):
        j = (i + 1) % n
        add_edge(i, j)
 
    # shortcut edges: only consider (i, j) pairs that could possibly be
    # within distance l on the cycle. This is mathematically equivalent to
    # scanning every pair and filtering by distance, but touches O(n*l)
    # pairs instead of O(n^2).
    shortcuts = []
    for i in range(n):
        for delta in range(2, l_int + 1):
            j = (i + delta) % n
            if rng.random() < p:
                add_edge(i, j)
                shortcuts.append((i, j))
 
    distances, predecessors = Dijkstras.dijkstra(adj, n, start_vertex=start_vertex)
    path, path_weights = Dijkstras.get_path(distances, predecessors, start_vertex, end_vertex)
 
    first_passage_time = sum(path_weights)
    distance = len(path) - 1 if path else float('inf')  # hop count; inf if unreachable
 
    return [trial, n, l, p, start_vertex, end_vertex, first_passage_time, distance]


def main():
    trial = sys.argv[0]
    n = 100
    l = n / 10
    p = 0.7
    start_vertex = 0
    end_vertex = n // 2
 
    row = run_trial(trial, n, l, p, start_vertex, end_vertex)
 
    with open('data.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(row)

    
    
if __name__ == "__main__":
    main()
