from collections import deque

def bfs(graph, n, start_node):
    visited = [False] * n
    queue = deque([start_node])

    visited[start_node] = True

    edge_list = []
    
    while queue:
        u = queue.popleft()
        print(u, end=" ")

        for v in range(n):
            if (graph[u][v] != 0 and not visited[v]):
                visited[v] = True
                queue.append(v)
                edge_list.append((u,v))

    return edge_list