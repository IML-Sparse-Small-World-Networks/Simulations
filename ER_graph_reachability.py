import csv
from collections import deque
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np



n = 10000
l = 100
shortcut_lambda = 100
k = 5
source = 0
seed = 12
output = Path("reachability_output")
max_draw_nodes = 1000
export_details = False



def generate_graph(n, l, shortcut_lambda, seed):
    if n < 4 or not 2 <= l <= n // 2:
        raise ValueError("Require n >= 4 and 2 <= l <= n//2")
    p = shortcut_lambda / (2 * n - 2)
    if not 0 <= p <= 1:
        raise ValueError("shortcut_lambda / (2*n - 2) must be in [0, 1]")

    rng = np.random.default_rng(seed)
    adjacency = [[] for _ in range(n)]
    for i in range(n):
        j = (i + 1) % n
        adjacency[i].append(j)
        adjacency[j].append(i)

    shortcuts = []

    def add_shortcuts(count, pair_at):
        if p == 0:
            return
        position = -1
        while True:
            position += 1 if p == 1 else int(rng.geometric(p))
            if position >= count:
                break
            i, j = pair_at(position)
            adjacency[i].append(j)
            adjacency[j].append(i)
            shortcuts.append((i, j))

    max_regular_offset = min(l, (n - 1) // 2)
    if max_regular_offset >= 2:
        add_shortcuts(
            n * (max_regular_offset - 1),
            lambda index: (
                index % n,
                (index % n + 2 + index // n) % n,
            ),
        )
    if n % 2 == 0 and l == n // 2:
        add_shortcuts(n // 2, lambda index: (index, index + n // 2))
    return adjacency, shortcuts, p


def expand_layers(adjacency, source, k):
    n = len(adjacency)
    if not 0 <= source < n or k < 0:
        raise ValueError("Require 0 <= source < n and k >= 0")
    depth = [-1] * n
    parent = [-1] * n
    layers = [[source]]
    depth[source] = 0
    queue = deque([source])
    while queue:
        u = queue.popleft()
        if depth[u] == k:
            continue
        for v in adjacency[u]:
            if depth[v] != -1:
                continue
            depth[v] = depth[u] + 1
            parent[v] = u
            if len(layers) <= depth[v]:
                layers.append([])
            layers[depth[v]].append(v)
            queue.append(v)
    return layers, depth, parent


def reachable_edges(adjacency, depth, parent):
    for u, neighbors in enumerate(adjacency):
        if depth[u] < 0:
            continue
        for v in neighbors:
            if depth[v] >= 0 and u < v:
                kind = "cycle" if (u - v) % len(adjacency) in (1, len(adjacency) - 1) else "shortcut"
                yield u, v, kind, parent[v] == u or parent[u] == v


def write_csv(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def draw_tree(path, layers, parent, n, extra_edges=None):
    children = {v: [] for layer in layers for v in layer}
    for layer in layers[1:]:
        for v in layer:
            children[parent[v]].append(v)

    x_position = {}
    leaf_index = 0
    stack = [(layers[0][0], False)]
    while stack:
        u, ready = stack.pop()
        if not children[u]:
            x_position[u] = leaf_index
            leaf_index += 1
        elif ready:
            x_position[u] = (x_position[children[u][0]] + x_position[children[u][-1]]) / 2
        else:
            stack.append((u, True))
            stack.extend((v, False) for v in reversed(children[u]))

    span = max(1, leaf_index - 1)
    fig, ax = plt.subplots(figsize=(min(24, max(9, leaf_index * 0.25)), max(4, len(layers) * 1.7)))
    depth_by_node = {v: d for d, layer in enumerate(layers) for v in layer}
    for u, v, _kind, is_tree in (() if extra_edges is None else extra_edges):
        if not is_tree:
            x_u, x_v = x_position[u] / span, x_position[v] / span
            d_u, d_v = depth_by_node[u], depth_by_node[v]
            if d_u == d_v:
                # 同层边用弧线画，避免穿过这一层的其他节点。
                t = np.linspace(0, 1, 60)
                arc_height = 0.15 + 0.25 * abs(x_v - x_u)
                ax.plot(x_u + (x_v - x_u) * t,
                        -d_u - arc_height * 4 * t * (1 - t),
                        color="seagreen", linestyle=":", linewidth=2, zorder=0)
            else:
                ax.plot([x_u, x_v], [-d_u, -d_v],
                        color="seagreen", linestyle=":", linewidth=2, zorder=0)
    for d, layer in enumerate(layers[1:], start=1):
        for v in layer:
            u = parent[v]
            is_cycle = (u - v) % n in (1, n - 1)
            ax.plot(
                [x_position[u] / span, x_position[v] / span], [-d + 1, -d],
                color="steelblue" if is_cycle else "firebrick",
                linestyle="-" if is_cycle else "--", linewidth=2, alpha=0.65,
            )
    count = sum(map(len, layers))
    for d, layer in enumerate(layers):
        ax.scatter([x_position[v] / span for v in layer], [-d] * len(layer),
                   s=55 if count <= 80 else 9, color="orange" if d == 0 else "#263c73", zorder=3)
        if count <= 80:
            for v in layer:
                ax.annotate(str(v), (x_position[v] / span, -d), xytext=(0, 6),
                            textcoords="offset points", ha="center", fontsize=8)
    ax.set_yticks([-d for d in range(len(layers))], [f"k={d} ({len(layer)})" for d, layer in enumerate(layers)])
    ax.set_xticks([])
    ax.set_xlim(-0.03, 1.03)
    ax.set_ylim(-len(layers) + 0.4, 0.5)
    title = "Reachable subgraph" if extra_edges is not None else "BFS discovery tree"
    legend = "Blue: ring edge; red dashed: shortcut"
    if extra_edges is not None:
        cycle_rank = sum(not is_tree for _, _, _, is_tree in extra_edges)
        title += f" (independent cycles={cycle_rank})"
        legend += "; green dotted: non-tree edge"
    ax.set_title(f"{title} from node {layers[0][0]} (n={n})\n{legend}")
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main():
    if max_draw_nodes < 0:
        raise ValueError("Require max_draw_nodes >= 0")
    adjacency, shortcuts, p = generate_graph(n, l, shortcut_lambda, seed)
    layers, depth, parent = expand_layers(adjacency, source, k)
    output.mkdir(parents=True, exist_ok=True)
    cumulative = 0
    counts = []
    for d, layer in enumerate(layers):
        cumulative += len(layer)
        counts.append((d, len(layer), cumulative))
    write_csv(output / "layer_counts.csv", ["k", "new_nodes", "cumulative_nodes"], counts)

    discovered = cumulative
    if n <= max_draw_nodes or export_details:
        write_csv(output / "nodes.csv", ["node", "k", "parent"],
                  ((v, d, parent[v] if parent[v] != -1 else "") for d, layer in enumerate(layers) for v in layer))
        write_csv(output / "reachable_edges.csv", ["from", "to", "edge_type", "in_tree"],
                  reachable_edges(adjacency, depth, parent))
    if discovered <= max_draw_nodes:
        draw_tree(output / "reachability_tree.png", layers, parent, n)
        all_edges = list(reachable_edges(adjacency, depth, parent))
        draw_tree(output / "reachability_graph.png", layers, parent, n, all_edges)

    print(f"n={n}, l={l}, lambda={shortcut_lambda:g}, p={p:.6g}, shortcuts={len(shortcuts)}")
    print(f"source={source}, K={k}, reached={discovered}/{n}")
    print("new nodes by layer:", [len(layer) for layer in layers])
    print(f"Output: {output.resolve()}")


if __name__ == "__main__":
    main()
