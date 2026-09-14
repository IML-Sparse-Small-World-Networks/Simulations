import sys
import csv
import numpy as np
from datetime import datetime
import secrets

import Dijkstras_Algorithm as Dijkstras

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
def main():
    print("parameters")
    '''
    trial = sys.argv[0]
    n = int(sys.argv[1])
    l = float(sys.argv[2])
    p = float(sys.argv[3])
    start_vertex = int(sys.argv[4])
    end_vertex = int(sys.argv[5])
    '''
    trial = sys.argv[0]
    n = 100
    l = n/10
    p = 0.7
    start_vertex = 0
    end_vertex = n//2

    # generate random graph
    limit = 2**10000
    random_seed = secrets.randbelow(limit)
    r = np.random.default_rng(seed=random_seed)
    A = np.zeros((n, n), dtype=int)

    print("data for csv Trial, n, l, p, FirstPassageTime, Distance")
    data = [trial, n, l, p, start_vertex, end_vertex]
    for i in range(n):
        j = (i + 1) % n
        A[i, j] = 1
        A[j, i] = 1
    
    # generate shortcuts
    shortcuts = []
    for i in range(n):
        for j in range(i+1, n): # j > i
            distance = min((j-i), n - (j-i))

            if (2 <= distance <= l):
                if r.random() < p:
                    A[i, j] = 1
                    A[j, i] = 1
                    shortcuts.append((i, j))

    # generate weights
    rate = 1.0
    scale = 1/rate
    W = np.zeros((n,n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            if A[i,j] == 1:
                weight = r.exponential(scale=scale)
                W[i,j] = weight
                W[j,i] = weight

    # edges and vertices
    cycle_edges = []
    for i in range(n):
        cycle_edges.append((i, (i+1)%n))

    graph_vertices = []
    for i in range(n):
        graph_vertices.append(i)

    # calculate shortest path
    distances, predecessors = Dijkstras.dijkstra(W, graph_vertices, n)
    path, path_weights = Dijkstras.get_path(
        W,
        predecessors,
        start_vertex,
        end_vertex
    )
    
    # calculate FirstPassageTime
    FirstPassageTime=0
    for i in range(len(path_weights)-1):
        FirstPassageTime += path_weights[i]
    data.append(FirstPassageTime)
    
    # calculate optimal path distance
    data.append(len(path)-1)

    # write data to csv file
    with open('data.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        writer.writerow(data)

    
    
if __name__ == "__main__":
    main()
