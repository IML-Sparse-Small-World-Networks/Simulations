import heapq
import math
import random
import time


def _geometric_successes(number_of_candidates, p, r):

    if p >= 1:
        for position in range(number_of_candidates):
            yield position
        return

    log_failure = math.log1p(-p)
    position = -1

    while True:
        gap = int(math.log1p(-r.random()) / log_failure) + 1
        position += gap

        if position >= number_of_candidates:
            return

        yield position


def generate_weighted_cycle_graph(G, n_, l_, p_, rate, mu, seed):
    n = n_
    r = random.Random(seed)

    L = min(int(l_), n // 2)
    max_regular_distance = min(L, (n - 1) // 2)
    number_of_regular_candidates = n * max(0, max_regular_distance - 1)
    has_opposite_vertices = n % 2 == 0 and L >= n // 2
    number_of_opposite_candidates = n // 2 if has_opposite_vertices else 0
    number_of_candidates = (
        number_of_regular_candidates + number_of_opposite_candidates
    )

    shortcuts = []

    for position in _geometric_successes(number_of_candidates, p_, r):
        if position < number_of_regular_candidates:
            distance = 2 + position // n
            i = position % n
            j = (i + distance) % n
        else:
            i = position - number_of_regular_candidates
            j = i + n // 2

        shortcuts.append((i, j))

    for i in range(n):
        j = (i + 1) % n
        weight = r.expovariate(rate)
        G[i][j] = weight
        G[j][i] = weight

    for i, j in shortcuts:
        weight = mu * r.expovariate(rate)
        G[i][j] = weight
        G[j][i] = weight

    return shortcuts


def _minimum_distance(heap, distances, settled):
    while heap:
        distance, vertex = heap[0]

        if settled[vertex] or distance != distances[vertex]:
            heapq.heappop(heap)
            continue

        return distance

    return math.inf


def _pop_minimum(heap, distances, settled):
    while heap:
        distance, vertex = heapq.heappop(heap)

        if settled[vertex] or distance != distances[vertex]:
            continue

        return distance, vertex

    return math.inf, None


def _path_from_start(predecessors, vertex):
    path = []

    while vertex is not None:
        path.append(vertex)
        vertex = predecessors[vertex]

    path.reverse()
    return path


def _path_to_end(predecessors, vertex):
    path = []

    while vertex is not None:
        path.append(vertex)
        vertex = predecessors[vertex]

    return path


def bidirectional_dijkstra(G, start_vertex, end_vertex):
    n = len(G)

    if not 0 <= start_vertex < n or not 0 <= end_vertex < n:
        raise ValueError("start_vertex and end_vertex must be valid vertices")

    if start_vertex == end_vertex:
        return 0.0, [start_vertex], [], 0, 0

    distances_start = [math.inf] * n
    distances_end = [math.inf] * n
    predecessors_start = [None] * n
    predecessors_end = [None] * n
    settled_start = [False] * n
    settled_end = [False] * n

    distances_start[start_vertex] = 0.0
    distances_end[end_vertex] = 0.0
    heap_start = [(0.0, start_vertex)]
    heap_end = [(0.0, end_vertex)]

    best_distance = math.inf
    best_bridge = None
    number_settled_start = 0
    number_settled_end = 0

    while heap_start and heap_end:
        minimum_start = _minimum_distance(
            heap_start,
            distances_start,
            settled_start,
        )
        minimum_end = _minimum_distance(
            heap_end,
            distances_end,
            settled_end,
        )

        # stopping condition
        if minimum_start + minimum_end >= best_distance:
            break

        if minimum_start <= minimum_end:
            current_distance, u = _pop_minimum(heap_start,distances_start,settled_start,)

            if u is None:
                break

            settled_start[u] = True
            number_settled_start += 1

            if distances_end[u] < math.inf:
                candidate = current_distance + distances_end[u]
                if candidate < best_distance:
                    best_distance = candidate
                    best_bridge = (u, u)

            for v, weight in G[u].items():
                if weight < 0:
                    raise ValueError("Dijkstra requires nonnegative weights")

                new_distance = current_distance + weight

                if new_distance < distances_start[v]:
                    distances_start[v] = new_distance
                    predecessors_start[v] = u
                    heapq.heappush(heap_start, (new_distance, v))

                if distances_end[v] < math.inf:
                    candidate = current_distance + weight + distances_end[v]
                    if candidate < best_distance:
                        best_distance = candidate
                        best_bridge = (u, v)
        else:
            current_distance, u = _pop_minimum(
                heap_end,
                distances_end,
                settled_end,
            )

            if u is None:
                break

            settled_end[u] = True
            number_settled_end += 1

            if distances_start[u] < math.inf:
                candidate = distances_start[u] + current_distance
                if candidate < best_distance:
                    best_distance = candidate
                    best_bridge = (u, u)

            for v, weight in G[u].items():
                if weight < 0:
                    raise ValueError("Dijkstra requires nonnegative weights")

                new_distance = current_distance + weight

                if new_distance < distances_end[v]:
                    distances_end[v] = new_distance
                    predecessors_end[v] = u
                    heapq.heappush(heap_end, (new_distance, v))

                if distances_start[v] < math.inf:
                    candidate = distances_start[v] + weight + current_distance
                    if candidate < best_distance:
                        best_distance = candidate
                        best_bridge = (v, u)

    if best_bridge is None:
        raise ValueError("No path exists between start and end")

    start_side, end_side = best_bridge
    path_start = _path_from_start(predecessors_start, start_side)
    path_end = _path_to_end(predecessors_end, end_side)

    if start_side == end_side:
        path = path_start + path_end[1:]
    else:
        path = path_start + path_end

    path_weights = [
        G[path[i]][path[i + 1]]
        for i in range(len(path) - 1)
    ]

    return (
        best_distance,
        path,
        path_weights,
        number_settled_start,
        number_settled_end,
    )


def main():
    # parameters
    start = 0
    n = 1000000
    lambda_ = 1 / 4
    G = [{} for _ in range(n)]
    l = n / math.log(n)
    p = lambda_ / (2 * l - 2)

    end = n // 2
    seed = 1
    rate = 1.0
    mu = 1

    generation_start = time.perf_counter()
    shortcuts = generate_weighted_cycle_graph(
        G,
        n,
        l,
        p,
        rate,
        mu,
        seed,
    )
    generation_seconds = time.perf_counter() - generation_start

    search_start = time.perf_counter()
    (
        distance,
        path,
        path_weights,
        number_settled_start,
        number_settled_end,
    ) = bidirectional_dijkstra(G, start, end)
    search_seconds = time.perf_counter() - search_start

    shortcut_count = 0
    shortcut_jumps = []

    for i in range(len(path) - 1):
        difference = abs(path[i] - path[i + 1])

        if difference != 1 and difference != n - 1:
            shortcut_count += 1
            shortcut_jumps.append(difference)


    print(f"start={start}, end={end}")
    print("Vertex path:", path)
    #print("Path weights list:", path_weights)
    print("Total weights:", distance)
    print("Number shortcuts path:", shortcut_count)
    print("Shortcut jumps:", shortcut_jumps)
    #print("Settled vertices: "f"start side={number_settled_start}, end side={number_settled_end}")
    print(f"Graph generation time: {generation_seconds:.6f} seconds")
    print(f"Bidirectional Dijkstra time: {search_seconds:.6f} seconds")


if __name__ == "__main__":
    main()
