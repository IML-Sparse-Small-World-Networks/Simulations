from collections import deque
import numpy as np
import math

r = np.random.default_rng(seed=123)

def bfs(G, n_, l_, p_, lambda_, start=0):
    n = n_
    visited = [False] * n
    parent = [-1] * n
    depth = [0] * n
    visited[start] = True
    queue = deque([start])
    discovered = 1

    while queue:
        u = queue.popleft()
        G[u].add((u-1)%n)
        G[u].add((u+1)%n)
        for i in range(-1 * l_, l_ + 1):
            if math.abs(l_) <= 1:
                continue
            if r.random() < p_:
                G[u].add(l_)
                

        for v in G[u]:
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

def main(n_, l_, lambda_):
    G = [{0}]

    p = (lambda_ / (2*n_ - 2))
