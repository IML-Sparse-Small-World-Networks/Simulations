import heapq
import random

#from ER_graph_simulation import graph_vertices
#from ER_graph_simulation import n


def dijkstra(graph, graph_vertices, n):
    distances = [float('inf')] * n
    predecessors = [None] * n
    distances[0] = 0
    visited = [False] * n
    for _ in range(n):
        min_distance = float('inf')
        u = None
        for i in range(n):
            if not visited[i] and distances[i] < min_distance:
                min_distance = distances[i]
                u = i

        if u is None:
            break

        visited[u] = True

        for v in range(n):
            if graph[u][v] != 0 and not visited[v]:
                alt = distances[u] + graph[u][v]
                if alt < distances[v]:
                    distances[v] = alt
                    predecessors[v] = u

    return distances, predecessors

def get_path(graph, predecessors, start_vertex, end_vertex):
    path = []
    current = end_vertex

    while current != start_vertex:
        path.insert(0, current)

        current = predecessors[current]

    if current == None:
        return [], []

    weights = []

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        weights.append(graph[u][v])

    return path, weights

