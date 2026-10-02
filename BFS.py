from collections import deque

def bfs(adj, start=0):
    n = len(adj)
    visited = [False] * n
    parent = [-1] * n
    depth = [0] * n
    visited[start] = True
    queue = deque([start])
    discovered = 1

    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if visited[v]:
                if v != parent[u]:
                    return depth[u] + 1, discovered   # cycle found
            else:
                visited[v] = True
                parent[v] = u
                depth[v] = depth[u] + 1
                discovered += 1
                queue.append(v)
    return max(depth), discovered    

'''

def bfs(graph, n, start_node):
    visited = [False] * n
    parent = [None] * n
    depth = [0] * n
    queue = deque([start_node])
    visited[start_node] = True

    edge_list = []
    short_cut_edges = []
    cycle_edges = []
    
    while queue:
        u = queue.popleft()

        for v in range(n):
            if graph[u][v] != 0:
                if visited[v]:
                    if v != parent[u]:
                        return edge_list, short_cut_edges, cycle_edges, depth[u] + 1

                # First time seeing v
                else:
                    visited[v] = True
                    parent[v] = u
                    depth[v] = depth[u] + 1

                    queue.append(v)
                    edge_list.append((u, v))
                    if abs(u - v) > 1:
                        short_cut_edges.append((u, v))
                    else:
                        cycle_edges.append((u, v))
    '''