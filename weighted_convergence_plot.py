# Plot shortest-path sum(weights) / ln(n)

import csv
import math
from pathlib import Path
import statistics


INPUT = Path("weighted_convergence_data_output/weighted_distance_trials.csv")
OUTPUT = Path("weighted_convergence_data_output/weighted_distance_convergence.svg")


def read_trials(path):
    rows = []

    with path.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            n = int(row["n"])
            rows.append({
                "n": n,
                "trial": int(row["trial"]),
                "value": float(row["distance"]) / math.log(n),
            })

    if not rows:
        raise ValueError(f"No trial data found in {path}")

    return rows


def summarize(rows):
    groups = {}

    for row in rows:
        groups.setdefault(row["n"], []).append(row["value"])

    result = []

    for n, values in sorted(groups.items()):
        sd = statistics.stdev(values) if len(values) > 1 else 0.0
        result.append({
            "n": n,
            "count": len(values),
            "mean": statistics.fmean(values),
            "sem": sd / math.sqrt(len(values)),
        })

    return result


def draw_plot(path, rows, summaries):
    width, height = 1100, 720
    left, right, top, bottom = 105, 65, 100, 90
    plot_width = width - left - right
    plot_height = height - top - bottom

    log_values = [math.log10(row["n"]) for row in summaries]
    min_log, max_log = min(log_values), max(log_values)
    values = [row["value"] for row in rows]
    min_y, max_y = min(values), max(values)
    padding = max((max_y - min_y) * 0.08, 0.05)
    min_y -= padding
    max_y += padding

    def x_position(n):
        if min_log == max_log:
            return left + plot_width / 2
        return left + (
            (math.log10(n) - min_log) / (max_log - min_log) * plot_width
        )

    def y_position(value):
        return top + (max_y - value) / (max_y - min_y) * plot_height

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text { font-family: Arial, sans-serif; fill: #222; }</style>',
        f'<text x="{width/2}" y="35" text-anchor="middle" '
        f'font-size="22">Weighted distance convergence</text>',
        f'<text x="{width/2}" y="62" text-anchor="middle" '
        f'font-size="13">sum(weights) / ln(n)</text>',
    ]

    for index in range(6):
        value = min_y + index * (max_y - min_y) / 5
        tick_y = y_position(value)
        svg.extend([
            f'<line x1="{left}" y1="{tick_y:.2f}" x2="{width-right}" '
            f'y2="{tick_y:.2f}" stroke="#e5e7eb"/>',
            f'<text x="{left-12}" y="{tick_y+5:.2f}" text-anchor="end" '
            f'font-size="12">{value:.3f}</text>',
        ])

    for row in summaries:
        tick_x = x_position(row["n"])
        svg.extend([
            f'<line x1="{tick_x:.2f}" y1="{top}" x2="{tick_x:.2f}" '
            f'y2="{height-bottom}" stroke="#eeeeee"/>',
            f'<text x="{tick_x:.2f}" y="{height-bottom+25}" '
            f'text-anchor="middle" font-size="12">{row["n"]:,}</text>',
        ])

    svg.extend([
        f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" '
        f'y2="{height-bottom}" stroke="#222"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" '
        f'y2="{height-bottom}" stroke="#222"/>',
        f'<text x="{left+plot_width/2}" y="{height-28}" '
        f'text-anchor="middle" font-size="15">n (logarithmic scale)</text>',
        f'<text x="28" y="{top+plot_height/2}" text-anchor="middle" '
        f'font-size="15" transform="rotate(-90 28 {top+plot_height/2})">'
        f'sum(weights) / ln(n)</text>',
    ])

    for row in rows:
        jitter = ((row["trial"] * 17) % 13 - 6) * 0.7
        svg.append(
            f'<circle cx="{x_position(row["n"])+jitter:.2f}" '
            f'cy="{y_position(row["value"]):.2f}" r="3" '
            f'fill="#7da7b8" fill-opacity="0.30"/>'
        )

    points = " ".join(
        f'{x_position(row["n"]):.2f},{y_position(row["mean"]):.2f}'
        for row in summaries
    )
    svg.append(
        f'<polyline points="{points}" fill="none" stroke="#2457c5" '
        f'stroke-width="2.5"/>'
    )

    for row in summaries:
        point_x = x_position(row["n"])
        point_y = y_position(row["mean"])
        upper_y = y_position(row["mean"] + row["sem"])
        lower_y = y_position(row["mean"] - row["sem"])
        svg.extend([
            f'<line x1="{point_x:.2f}" y1="{upper_y:.2f}" '
            f'x2="{point_x:.2f}" y2="{lower_y:.2f}" '
            f'stroke="#2457c5" stroke-width="2"/>',
            f'<line x1="{point_x-5:.2f}" y1="{upper_y:.2f}" '
            f'x2="{point_x+5:.2f}" y2="{upper_y:.2f}" '
            f'stroke="#2457c5" stroke-width="2"/>',
            f'<line x1="{point_x-5:.2f}" y1="{lower_y:.2f}" '
            f'x2="{point_x+5:.2f}" y2="{lower_y:.2f}" '
            f'stroke="#2457c5" stroke-width="2"/>',
            f'<circle cx="{point_x:.2f}" cy="{point_y:.2f}" r="6" '
            f'fill="#2457c5" stroke="white" stroke-width="1.5">'
            f'<title>n={row["n"]}, mean={row["mean"]:.6f}, '
            f'SEM={row["sem"]:.6f}, trials={row["count"]}</title></circle>',
        ])

    svg.extend([
        f'<circle cx="{left+18}" cy="{top+18}" r="5" fill="#2457c5"/>',
        f'<text x="{left+31}" y="{top+23}" font-size="12">mean +/- 1 SEM</text>',
        f'<circle cx="{left+175}" cy="{top+18}" r="3" '
        f'fill="#7da7b8" fill-opacity="0.55"/>',
        f'<text x="{left+187}" y="{top+23}" font-size="12">individual trial</text>',
        '</svg>',
    ])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(svg), encoding="utf-8")


def main():
    rows = read_trials(INPUT)
    summaries = summarize(rows)
    draw_plot(OUTPUT, rows, summaries)

    for row in summaries:
        print(
            f'n={row["n"]:>11,}  mean={row["mean"]:.6f}  '
            f'SEM={row["sem"]:.6f}  trials={row["count"]}'
        )

    print(f"Plot: {OUTPUT.resolve()}")


if __name__ == "__main__":
    main()
