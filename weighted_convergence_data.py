"""Collect weighted first-passage distances for increasing cycle sizes."""

from array import array
import csv
import gc
import heapq
import math
import os
from pathlib import Path
import random
import statistics
import time


RAW_FIELDS = ["n","trial","seed","lambda","rate","l","p","start","end","shortcuts","distance","distance_over_log_n","convergence_constant","settled_start","settled_end","generation_seconds","search_seconds",]


def convergence_constant(lambda_):
    return 2 / (lambda_- 1+ math.sqrt(lambda_ ** 2 + 6 * lambda_ + 1))


def _geometric_successes(number_of_candidates, p, r):

    log_failure = math.log1p(-p)
    position = -1

    while True:
        gap = int(math.log1p(-r.random()) / log_failure) + 1
        position += gap

        if position >= number_of_candidates:
            return

        yield position


class CompactWeightedCycleGraph:

    def __init__(self, n, l, p, rate, seed):
        self.n = n
        self.shortcut_head = array("i", [-1]) * n
        self.shortcut_to = array("I")
        self.shortcut_next = array("i")
        self.shortcut_weight = array("d")

        r = random.Random(seed)
        L = min(int(l), n // 2)
        max_regular_distance = min(L, (n - 1) // 2)
        regular_candidates = n * max(0, max_regular_distance - 1)
        has_opposite_vertices = n % 2 == 0 and L >= n // 2
        opposite_candidates = n // 2 if has_opposite_vertices else 0
        number_of_candidates = regular_candidates + opposite_candidates

        number_of_shortcuts = 0

        for position in _geometric_successes(number_of_candidates, p, r):
            if position < regular_candidates:
                distance = 2 + position // n
                u = position % n
                v = (u + distance) % n
            else:
                u = position - regular_candidates
                v = u + n // 2

            weight = r.expovariate(rate)
            self._add_shortcut_arc(u, v, weight)
            self._add_shortcut_arc(v, u, weight)
            number_of_shortcuts += 1

        # cycle_weight[i] belongs to the undirected edge {i, (i+1) mod n}.
        self.cycle_weight = array(
            "d",
            (r.expovariate(rate) for _ in range(n)),
        )
        self.number_of_shortcuts = number_of_shortcuts

    def _add_shortcut_arc(self, u, v, weight):
        edge_index = len(self.shortcut_to)
        self.shortcut_to.append(v)
        self.shortcut_weight.append(weight)
        self.shortcut_next.append(self.shortcut_head[u])
        self.shortcut_head[u] = edge_index

    def neighbors(self, u):
        left = u - 1 if u else self.n - 1
        right = u + 1 if u + 1 < self.n else 0

        yield left, self.cycle_weight[left]
        yield right, self.cycle_weight[u]

        edge_index = self.shortcut_head[u]

        while edge_index != -1:
            yield (
                self.shortcut_to[edge_index],
                self.shortcut_weight[edge_index],
            )
            edge_index = self.shortcut_next[edge_index]


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


def bidirectional_dijkstra_distance(graph, start, end):
    n = graph.n

    if start == end:
        return 0.0, 0, 0

    distances_start = array("d", [math.inf]) * n
    distances_end = array("d", [math.inf]) * n
    settled_start = bytearray(n)
    settled_end = bytearray(n)

    distances_start[start] = 0.0
    distances_end[end] = 0.0
    heap_start = [(0.0, start)]
    heap_end = [(0.0, end)]
    best_distance = math.inf
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

        if minimum_start + minimum_end >= best_distance:
            break

        if minimum_start <= minimum_end:
            current_distance, u = _pop_minimum(
                heap_start,
                distances_start,
                settled_start,
            )

            if u is None:
                break

            settled_start[u] = 1
            number_settled_start += 1

            if distances_end[u] < math.inf:
                best_distance = min(
                    best_distance,
                    current_distance + distances_end[u],
                )

            for v, weight in graph.neighbors(u):
                new_distance = current_distance + weight

                if new_distance < distances_start[v]:
                    distances_start[v] = new_distance
                    heapq.heappush(heap_start, (new_distance, v))

                if distances_end[v] < math.inf:
                    best_distance = min(
                        best_distance,
                        current_distance + weight + distances_end[v],
                    )
        else:
            current_distance, u = _pop_minimum(
                heap_end,
                distances_end,
                settled_end,
            )

            if u is None:
                break

            settled_end[u] = 1
            number_settled_end += 1

            if distances_start[u] < math.inf:
                best_distance = min(
                    best_distance,
                    distances_start[u] + current_distance,
                )

            for v, weight in graph.neighbors(u):
                new_distance = current_distance + weight

                if new_distance < distances_end[v]:
                    distances_end[v] = new_distance
                    heapq.heappush(heap_end, (new_distance, v))

                if distances_start[v] < math.inf:
                    best_distance = min(
                        best_distance,
                        distances_start[v] + weight + current_distance,
                    )

    if best_distance == math.inf:
        raise ValueError("No path exists between start and end")

    return best_distance, number_settled_start, number_settled_end


def trial_seed(base_seed, n, trial):
    return (base_seed << 40) ^ (n << 8) ^ trial


def read_trials(path):
    if not path.exists() or path.stat().st_size == 0:
        return []

    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def summarize_trials(rows, n_values, convergence_value):
    summaries = []

    for n in n_values:
        group = [row for row in rows if int(row["n"]) == n]

        if not group:
            continue

        distances = [float(row["distance"]) for row in group]
        normalized = [
            float(row["distance_over_log_n"])
            for row in group
        ]
        distance_sd = statistics.stdev(distances) if len(group) > 1 else 0.0
        normalized_sd = statistics.stdev(normalized) if len(group) > 1 else 0.0

        summaries.append({
            "n": n,
            "completed_trials": len(group),
            "mean_distance": statistics.fmean(distances),
            "distance_sd": distance_sd,
            "distance_sem": distance_sd / math.sqrt(len(group)),
            "mean_distance_over_log_n": statistics.fmean(normalized),
            "normalized_sd": normalized_sd,
            "normalized_sem": normalized_sd / math.sqrt(len(group)),
            "convergence_constant": convergence_value,
            "mean_minus_constant": (
                statistics.fmean(normalized) - convergence_value
            ),
            "mean_shortcuts": statistics.fmean(
                int(row["shortcuts"]) for row in group
            ),
            "mean_generation_seconds": statistics.fmean(
                float(row["generation_seconds"]) for row in group
            ),
            "mean_search_seconds": statistics.fmean(
                float(row["search_seconds"]) for row in group
            ),
        })

    return summaries


def write_summary(path, summaries):
    if not summaries:
        return

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)


def draw_convergence_plot(path, rows, *_unused):
    """Use the small standalone plotter while data collection is running."""
    from weighted_convergence_plot import draw_plot, summarize

    normalized_rows = [
        {
            "n": int(row["n"]),
            "trial": int(row["trial"]),
            "value": float(row["distance"]) / math.log(int(row["n"])),
        }
        for row in rows
    ]
    draw_plot(path, normalized_rows, summarize(normalized_rows))

def validate_existing_rows(rows, n_values, lambda_, convergence_value):
    allowed_n = set(n_values)

    for row in rows:
        if int(row["n"]) not in allowed_n:
            raise ValueError(
                "Existing CSV contains an n value not present in n_values"
            )
        if not math.isclose(float(row["lambda"]), lambda_):
            raise ValueError("Existing CSV uses a different lambda")
        if "rate" in row and not math.isclose(float(row["rate"]), 1.0):
            raise ValueError("Existing CSV does not use Exp(1) weights")
        if not math.isclose(
            float(row["convergence_constant"]),
            convergence_value,
        ):
            raise ValueError("Existing CSV uses a different constant")


def main():
    # parameters
    n_values = [
        10_000,
        100_000,
        1_000_000,
        2_000_000,
        5_000_000,
        10_000_000,
        20_000_000,
        50_000_000,
        100_000_000,
    ]
    number_of_trials = 50
    lambda_ = 1 / 4
    rate = 1.0
    start = 0
    first_seed = 1
    output = Path("weighted_convergence_data_output")

    # Use this environment variable only for a fast implementation check.
    if os.environ.get("FPP_QUICK_TEST") == "1":
        n_values = [1_000, 3_000]
        number_of_trials = 3
        output = Path("weighted_convergence_quick_test_output")

    output.mkdir(parents=True, exist_ok=True)
    raw_path = output / "weighted_distance_trials.csv"
    summary_path = output / "weighted_distance_summary.csv"
    plot_path = output / "weighted_distance_convergence.svg"
    convergence_value = convergence_constant(lambda_)

    existing_rows = read_trials(raw_path)
    validate_existing_rows(
        existing_rows,
        n_values,
        lambda_,
        convergence_value,
    )
    completed = {
        (int(row["n"]), int(row["trial"]))
        for row in existing_rows
    }

    print(f"lambda={lambda_:g}, Exp(rate={rate:g}) edge weights")
    print(f"conjectured convergence constant c={convergence_value:.10f}")
    print(f"completed trials already in CSV: {len(completed)}")

    needs_header = not raw_path.exists() or raw_path.stat().st_size == 0
    started = time.perf_counter()

    try:
        with raw_path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=RAW_FIELDS)

            if needs_header:
                writer.writeheader()
                handle.flush()

            for n in n_values:
                l = n / math.log(n)
                p = lambda_ / (2 * l - 2)
                end = n // 2

                for trial in range(1, number_of_trials + 1):
                    if (n, trial) in completed:
                        continue

                    seed = trial_seed(first_seed, n, trial)
                    generation_start = time.perf_counter()
                    graph = CompactWeightedCycleGraph(
                        n,
                        l,
                        p,
                        rate,
                        seed,
                    )
                    generation_seconds = (
                        time.perf_counter() - generation_start
                    )

                    search_start = time.perf_counter()
                    distance, settled_start, settled_end = (
                        bidirectional_dijkstra_distance(graph, start, end)
                    )
                    search_seconds = time.perf_counter() - search_start
                    normalized_distance = distance / math.log(n)

                    writer.writerow({
                        "n": n,
                        "trial": trial,
                        "seed": seed,
                        "lambda": lambda_,
                        "rate": rate,
                        "l": l,
                        "p": p,
                        "start": start,
                        "end": end,
                        "shortcuts": graph.number_of_shortcuts,
                        "distance": distance,
                        "distance_over_log_n": normalized_distance,
                        "convergence_constant": convergence_value,
                        "settled_start": settled_start,
                        "settled_end": settled_end,
                        "generation_seconds": generation_seconds,
                        "search_seconds": search_seconds,
                    })
                    handle.flush()
                    completed.add((n, trial))

                    print(
                        f"n={n:,}, trial={trial:02d}/{number_of_trials}, "
                        f"distance={distance:.6f}, "
                        f"distance/ln(n)={normalized_distance:.6f}, "
                        f"shortcuts={graph.number_of_shortcuts:,}, "
                        f"generation={generation_seconds:.3f}s, "
                        f"search={search_seconds:.3f}s",
                        flush=True,
                    )

                    del graph
                    gc.collect()

                current_rows = read_trials(raw_path)
                summaries = summarize_trials(
                    current_rows,
                    n_values,
                    convergence_value,
                )
                write_summary(summary_path, summaries)
                draw_convergence_plot(
                    plot_path,
                    current_rows,
                    summaries,
                    n_values,
                    number_of_trials,
                    lambda_,
                    convergence_value,
                )
    except KeyboardInterrupt:
        print("\nInterrupted; completed trials remain saved in the CSV.")
    finally:
        current_rows = read_trials(raw_path)
        summaries = summarize_trials(
            current_rows,
            n_values,
            convergence_value,
        )
        write_summary(summary_path, summaries)
        draw_convergence_plot(
            plot_path,
            current_rows,
            summaries,
            n_values,
            number_of_trials,
            lambda_,
            convergence_value,
        )

    print(f"Elapsed time: {time.perf_counter() - started:.2f} seconds")
    print(f"Raw trials: {raw_path.resolve()}")
    print(f"Summary: {summary_path.resolve()}")
    print(f"Plot: {plot_path.resolve()}")


if __name__ == "__main__":
    main()
