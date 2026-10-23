import math
from pathlib import Path
import webbrowser

from Graph_Cycle import bidirectional_bfs


def draw_shortest_path(path, G, shortcuts, start_tree, end_tree, n, output_path):
    del G  # The edge categories below contain every generated edge.
    size = 1000
    center = size / 2
    radius = size * 0.4
    positions = [
        (
            center + radius * math.cos(2 * math.pi * i / n - math.pi / 2),
            center + radius * math.sin(2 * math.pi * i / n - math.pi / 2),
        )
        for i in range(n)
    ]
    cycle_edges = [(i, (i + 1) % n) for i in range(n)]
    path_edges = list(zip(path, path[1:]))

    def line(edge, color, width, opacity=1.0, dash=None):
        u, v = edge
        x1, y1 = positions[u]
        x2, y2 = positions[v]
        dashed = f' stroke-dasharray="{dash}"' if dash else ""
        return (
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" '
            f'x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" '
            f'stroke-width="{width}" stroke-opacity="{opacity}"{dashed}/>'
        )

    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" '
            f'height="{size}" viewBox="0 0 {size} {size}">'
        ),
        '<rect width="100%" height="100%" fill="white"/>',
        (
            f'<text x="{center}" y="32" text-anchor="middle" '
            f'font-family="sans-serif" font-size="22">Bidirectional shortest '
            f'path: {path[0]} to {path[-1]} (distance={len(path) - 1})</text>'
        ),
        (
            f'<text x="{center}" y="58" text-anchor="middle" '
            'font-family="sans-serif" font-size="15">Blue: cycle; red dashed: '
            'shortcut; thin green: reachability trees; thick green: shortest '
            'path</text>'
        ),
    ]
    svg.extend(line(edge, "steelblue", 1.5, 0.55) for edge in cycle_edges)
    svg.extend(line(edge, "red", 1.5, 0.5, "7 5") for edge in shortcuts)
    svg.extend(line(edge, "seagreen", 1.2, 0.45) for edge in start_tree)
    svg.extend(line(edge, "seagreen", 1.2, 0.45) for edge in end_tree)
    svg.extend(line(edge, "seagreen", 5, 0.95) for edge in path_edges)

    node_radius = 7 if n <= 80 else 3
    for vertex, (x, y) in enumerate(positions):
        color = "#9ecae1"
        radius_here = node_radius
        if vertex == path[0]:
            color = "orange"
            radius_here = 11
        elif vertex == path[-1]:
            color = "gold"
            radius_here = 11
        svg.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius_here}" '
            f'fill="{color}" stroke="black" stroke-width="0.7"/>'
        )
        if n <= 80:
            svg.append(
                f'<text x="{x:.2f}" y="{y - 11:.2f}" text-anchor="middle" '
                f'font-family="sans-serif" font-size="11">{vertex}</text>'
            )
    svg.append("</svg>")
    output_path.write_text("\n".join(svg), encoding="utf-8")


def main():
    # parameters
    n = 100
    start = 0
    end = n // 2
    lambda_ = 1
    G = {start: set()}
    p = (lambda_ / (2*n - 2)) * 2
    l = n / math.log(n)

    seed = 1
    output = Path("cycle_shortest_path_output")
    max_draw_nodes = 1000
    open_browser = True

    if max_draw_nodes < 0:
        raise ValueError("Require max_draw_nodes >= 0")

    (
        distance, path, shortcuts, start_tree, end_tree,
    ) = bidirectional_bfs(
        G,
        n,
        l,
        p,
        lambda_,
        start,
        end,
        seed,
        return_trees=True,
    )

    print(
        f"n={n}, l={l:.6g}, lambda={lambda_:g}, "
        f"p={p:.6g}, generated_vertices={len(G)}, shortcuts={len(shortcuts)}"
    )
    print(f"start={start}, end={end}, distance={distance}")
    print("shortest path:", path)

    if n <= max_draw_nodes:
        output.mkdir(parents=True, exist_ok=True)
        output_path = output / "shortest_path.svg"
        draw_shortest_path(
            path, G, shortcuts, start_tree, end_tree,
            n, output_path,
        )
        output_path = output_path.resolve()
        print(f"Output: {output_path}")
        if open_browser:
            opened = webbrowser.open(output_path.as_uri())
            if not opened:
                print("Could not open the browser automatically; open the SVG path above.")
    else:
        print(
            f"Drawing skipped: n={n} exceeds "
            f"max_draw_nodes={max_draw_nodes}"
        )


if __name__ == "__main__":
    main()
