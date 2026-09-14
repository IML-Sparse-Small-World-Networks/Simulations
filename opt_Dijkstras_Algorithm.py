import heapq



def dijkstra(adj, n, start_vertex=0):
    """
    Single-source shortest paths.
 
    adj: adjacency list, adj[u] = [(v, weight), ...] for every neighbor v of u.
         Build this once per graph instead of passing a dense n x n matrix -
         for a sparse graph (like the ring + shortcuts here) this avoids an
         O(n) scan per node and lets the heap do its job.
    n: number of vertices
    start_vertex: source vertex (defaults to 0, matching the original behavior)
    """
    distances = [float('inf')] * n
    predecessors = [None] * n
    distances[start_vertex] = 0
    visited = [False] * n
    pq = [(0.0, start_vertex)]
 
    while pq:
        dist_u, u = heapq.heappop(pq)
        if visited[u]:
            continue
        visited[u] = True
 
        for v, w in adj[u]:
            if not visited[v]:
                alt = dist_u + w
                if alt < distances[v]:
                    distances[v] = alt
                    predecessors[v] = u
                    heapq.heappush(pq, (alt, v))
 
    return distances, predecessors

def get_path(distances, predecessors, start_vertex, end_vertex):
    """
    Reconstruct the shortest path from start_vertex to end_vertex.
 
    Edge weights are recovered as distances[v] - distances[u] along the
    path, which is exact because Dijkstra's predecessor tree guarantees
    distances[v] == distances[u] + weight(u, v) for every tree edge - no
    need to re-look-up the graph.
    """
    if predecessors[end_vertex] is None and end_vertex != start_vertex:
        return [], []  # unreachable
 
    path = [end_vertex]
    current = end_vertex
    while current != start_vertex:
        current = predecessors[current]
        if current is None:
            return [], []  # unreachable
        path.insert(0, current)
 
    weights = []
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        weights.append(distances[v] - distances[u])
 
    return path, weights