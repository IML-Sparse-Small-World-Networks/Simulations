"""Dijkstra with a min-heap and an adjacency list.
Convert your existing weighted matrix W once with matrix_to_adjacency_list(W).
The adjacency list stores (neighbor, weight) pairs for each vertex.
"""
import heapq


def matrix_to_adjacency_list(matrix):
    """Convert an n x n weighted matrix (0 = no edge) to a list of neighbors."""
    n = len(matrix)
    return [
        [(v, float(matrix[u][v])) for v in range(n) if matrix[u][v] != 0]
        for u in range(n)
    ]


def dijkstra(graph, graph_vertices, n, start_vertex=0):
    """Compute shortest distances using an adjacency list and min-heap."""
    distances = [float('inf')] * n
    predecessors = [None] * n
    distances[start_vertex] = 0
    priority_queue = [(0, start_vertex)]

    while priority_queue:
        current_distance, u = heapq.heappop(priority_queue)
        if current_distance > distances[u]:
            continue

        for v, weight in graph[u]:
            new_distance = current_distance + weight
            if new_distance < distances[v]:
                distances[v] = new_distance
                predecessors[v] = u
                heapq.heappush(priority_queue, (new_distance, v))

    return distances, predecessors


def get_path(graph, predecessors, start_vertex, end_vertex):
    """Reconstruct the path and its edge weights from an adjacency list."""
    path = []
    current = end_vertex
    while current is not None:
        path.append(current)
        if current == start_vertex:
            break
        current = predecessors[current]
    path.reverse()
    if not path or path[0] != start_vertex:
        return [], []

    weights = []
    for u, v in zip(path, path[1:]):
        weights.append(next(weight for neighbor, weight in graph[u] if neighbor == v))
    return path, weights
