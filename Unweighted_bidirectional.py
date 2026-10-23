import math
import random

def reveal_edges(G, n_, l_, p_, r, u, expanded, shortcuts):
    n = n_
    G.setdefault(u, set())

    for v in ((u - 1) % n, (u + 1) % n):
        G.setdefault(v, set())
        G[u].add(v)
        G[v].add(u)

    # Geometric gaps jump directly between successful Bernoulli(p_) trials.
    # This has the same shortcut distribution as checking every candidate,
    # but is much faster when p_ is small and n is large.
    if p_ > 0:
        L = int(l_)
        max_regular_distance = min(L, (n - 1) // 2)
        regular_count = 2 * max(0, max_regular_distance - 1)
        has_opposite = n % 2 == 0 and L >= n // 2
        candidate_count = regular_count + int(has_opposite)
        log_failure = math.log1p(-p_) if p_ < 1 else None
        position = -1

        while True:
            if p_ == 1:
                gap = 1
            else:
                gap = int(math.log1p(-r.random()) / log_failure) + 1
            position += gap
            if position >= candidate_count:
                break

            if position < regular_count:
                distance = 2 + position // 2
                if position % 2 == 0:
                    v = (u - distance) % n
                else:
                    v = (u + distance) % n
            else:
                v = (u + n // 2) % n

            if v in expanded:
                continue
            G.setdefault(v, set())
            G[u].add(v)
            G[v].add(u)
            shortcuts.append((u, v))

    expanded.add(u)


def _expand_layer(
    G, n, l, p, r, frontier, depth_this, depth_other, parent_this,
    expanded, shortcuts,
):
    next_frontier = []
    best = None
    for u in frontier:
        reveal_edges(G, n, l, p, r, u, expanded, shortcuts)
        for v in sorted(G[u]):
            # Ignore collisions
            if depth_this[v] != -1:
                continue
            if depth_other[v] != -1:
                candidate = (depth_this[u] + 1 + depth_other[v], u, v)
                if best is None or candidate[0] < best[0]:
                    best = candidate
                continue
            depth_this[v] = depth_this[u] + 1
            parent_this[v] = u
            next_frontier.append(v)
    return next_frontier, best


def _path_to_root(parent, vertex):
    path = []
    while vertex != -1:
        path.append(vertex)
        vertex = parent[vertex]
    return path


def _join_paths(parent_start, parent_end, start_side, end_side):
    from_start = _path_to_root(parent_start, start_side)
    from_start.reverse()
    return from_start + _path_to_root(parent_end, end_side)


def _tree_edges(parent):
    return [
        (parent_vertex, vertex)
        for vertex, parent_vertex in enumerate(parent)
        if parent_vertex != -1
    ]


def bidirectional_bfs(
    G, n_, l_, p_, lambda_, start=0, end=None, seed=1,
    return_trees=False,
):
    n = n_
    end = n // 2 if end is None else end

    G.setdefault(start, set())
    G.setdefault(end, set())
    if start == end:
        result = (0, [start], [])
        return result + ([], []) if return_trees else result

    r = random.Random(seed)
    expanded = set()
    shortcuts = []
    depth_start = [-1] * n
    depth_end = [-1] * n
    parent_start = [-1] * n
    parent_end = [-1] * n
    depth_start[start] = 0
    depth_end[end] = 0
    frontier_start = [start]
    frontier_end = [end]

    while frontier_start and frontier_end:
        frontier_start, meeting = _expand_layer(
            G, n, l_, p_, r, frontier_start, depth_start, depth_end,
            parent_start, expanded, shortcuts,
        )
        if meeting is not None:
            distance, start_side, end_side = meeting
            path = _join_paths(parent_start, parent_end, start_side, end_side)
            result = (distance, path, shortcuts)
            if return_trees:
                return result + (_tree_edges(parent_start), _tree_edges(parent_end))
            return result

        frontier_end, meeting = _expand_layer(
            G, n, l_, p_, r, frontier_end, depth_end, depth_start,
            parent_end, expanded, shortcuts,
        )
        if meeting is not None:
            distance, end_side, start_side = meeting
            path = _join_paths(parent_start, parent_end, start_side, end_side)
            result = (distance, path, shortcuts)
            if return_trees:
                return result + (_tree_edges(parent_start), _tree_edges(parent_end))
            return result

    raise ValueError("No path exists between start and end")


def main():
    # parameters
    start = 0
    n = 100000
    lambda_ = 1
    G = {start: set()}
    p = (lambda_ / (2*n - 2)) * 2
    l = n / math.log(n)

    end = n // 2
    seed = 1

    distance, path, shortcuts = bidirectional_bfs(G,n,l,p,lambda_,start,end,seed,)

    print(
        f"n={n}, l={l:.6g}, lambda={lambda_:g}, "
        f"p={p:.6g}, generated_vertices={len(G)}, shortcuts={len(shortcuts)}"
    )
    print(f"start={start}, end={end}, distance={distance}")
    print("shortest path:", path)


if __name__ == "__main__":
    main()
