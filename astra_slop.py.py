"""First-passage times on a cycle with independent random shortcut edges.

Install: python -m pip install numpy scipy matplotlib
Run:     python tau_x_y.py --n 200000 --trials 20 --seed 42

Defaults match the original model: ell=floor(n/log(n)), expected shortcut
degree lambda=0.25, and independent Exp(rate=1) weights on ALL edges.
Each undirected edge has ONE weight, shared by its two orientations.
tau(x,y) is the minimum SUM OF WEIGHTS, not the number of path vertices.

By default, each trial generates a new graph and measures all pairs (x,x+d)
on it. Trials are independent; measurements at different d in the same trial
are correlated. --independent-pairs gives every pair its own fresh graphs.

Outputs: tau_trials.csv, tau_summary.csv, tau_plot.png, run_metadata.json.
The CSV is flushed after every graph, retaining completed trials if interrupted.
Use a different --output directory to keep multiple runs.

Examples:
  python tau_x_y.py --n 1000000 --trials 20 --lambda 0.25
  python tau_x_y.py --ell 5000 --p 0.000025 --distances 10 20 50 logn sqrt n/2
  python tau_x_y.py --unweighted --independent-pairs --output unweighted_results
  python tau_x_y.py --plot-only results/tau_trials.csv --output replotted

Why sampling is exact:
If M undirected pairs are eligible, first draw K ~ Binomial(M,p), then choose
K distinct pairs uniformly. Any particular subset S of size k has probability
P(K=k)/choose(M,k) = p**k * (1-p)**(M-k), exactly the independent Bernoulli model.
No list of all M candidate pairs is built. With sparse shortcuts, NumPy samples
integer indices without replacement using work proportional to sampled edges.
"""

import argparse
import csv
import json
import math
from pathlib import Path
import platform
from time import perf_counter

import numpy as np
import scipy
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra


def eligible_shortcut_count(n, ell):
    """Number of undirected pairs at cyclic distances 2 through ell inclusive."""
    count = n * (ell - 1)
    # At distance n/2, (u,u+n/2) and (u+n/2,u) are the same edge.
    if n % 2 == 0 and ell == n // 2:
        count -= n // 2
    return count


def sample_shortcuts(n, ell, p, rng):
    """Return endpoint arrays, sampling each eligible undirected edge once."""
    total = eligible_shortcut_count(n, ell)
    k = int(rng.binomial(total, p))
    # Pass an integer, NOT np.arange(total), which would allocate all candidates.
    edge_ids = rng.choice(total, size=k, replace=False, shuffle=False)

    # IDs 0..n-1 represent offset 2; the next n represent offset 3; etc.
    # The final offset has only n/2 IDs when ell=n/2 and n is even.
    u = edge_ids % n
    offset = edge_ids // n + 2
    v = (u + offset) % n
    return u, v


def make_graph(n, ell, p, rng, rate=1.0, unweighted=False):
    """Build a symmetric sparse matrix, storing O(n + realized shortcuts) entries."""
    shortcut_u, shortcut_v = sample_shortcuts(n, ell, p, rng)
    cycle_u = np.arange(n, dtype=np.int64)
    cycle_v = (cycle_u + 1) % n
    u = np.concatenate((cycle_u, shortcut_u))
    v = np.concatenate((cycle_v, shortcut_v))
    weights = (np.ones(len(u)) if unweighted
               else rng.exponential(scale=1.0 / rate, size=len(u)))

    graph = csr_matrix(
        (np.concatenate((weights, weights)),
         (np.concatenate((u, v)), np.concatenate((v, u)))),
        shape=(n, n),
    )
    return graph, len(shortcut_u)


def parse_distances(tokens, n):
    """Accept integer distances plus logn, sqrt, and n/<integer>; never eval input."""
    requested = tokens is not None
    if tokens is None:
        tokens = ['10', '20', '50', '100', 'logn', 'sqrt', 'n/10', 'n/4', 'n/2']
    distances = set()
    for token in tokens:
        if token in ('logn', 'log(n)'):
            value = math.floor(math.log(n))  # natural logarithm
        elif token in ('sqrt', 'sqrt(n)', 'n^1/2'):
            value = math.isqrt(n)
        elif token.startswith('n/'):
            divisor = int(token[2:])
            if divisor <= 0:
                raise ValueError('Distance denominators must be positive.')
            value = n // divisor
        else:
            value = int(token)
        if 1 <= value <= n // 2:
            distances.add(value)
        elif requested:
            raise ValueError(f'Distance {token!r} must lie between 1 and n//2.')
    if not distances:
        raise ValueError('No valid distances were selected.')
    return sorted(distances)


def summarize_and_plot(trials_path, output, show=False):
    """Read recorded observations; write summaries and a mean +/- sample-SD plot."""
    import matplotlib
    if not show:
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    with Path(trials_path).open(newline='') as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError('The trial CSV contains no completed observations.')
    # Keep replotting a mixed-parameter CSV from silently pooling different models.
    model_keys = ('n', 'ell', 'p', 'weight_model', 'rate', 'x', 'sampling_mode')
    if len({tuple(row[key] for key in model_keys) for row in rows}) != 1:
        raise ValueError('Plot one parameter configuration at a time.')
    first = rows[0]
    distances = sorted({int(row['cyclic_distance']) for row in rows})
    summaries = []
    samples = []
    for distance in distances:
        group = [row for row in rows if int(row['cyclic_distance']) == distance]
        values = np.array([float(row['tau']) for row in group])
        sd = float(values.std(ddof=1)) if len(values) > 1 else math.nan
        samples.append(values)
        summaries.append({
            **{key: first[key] for key in model_keys},
            'cyclic_distance': distance, 'y': group[0]['y'], 'trials': len(values),
            'mean_tau': float(values.mean()), 'std_tau': sd,
            'sem_tau': sd / math.sqrt(len(values)),
            'median_tau': float(np.median(values)),
            'min_tau': float(values.min()), 'max_tau': float(values.max()),
        })
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'tau_summary.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)

    fig, ax = plt.subplots(figsize=(10, 6), layout='constrained')
    for i, (distance, values) in enumerate(zip(distances, samples)):
        ax.scatter(np.full(len(values), distance), values, s=22,
                   color='#547f95', alpha=0.38,
                   label='Individual trials' if i == 0 else None, zorder=2)
    ax.errorbar(distances, [row['mean_tau'] for row in summaries],
                yerr=[row['std_tau'] if math.isfinite(row['std_tau']) else 0
                      for row in summaries],
                fmt='o-', color='#b54437', capsize=4, linewidth=1.8,
                label='Mean +/- 1 sample SD', zorder=3)
    ax.set_xscale('log')
    ax.set_xlabel('Cyclic distance d(x, y)  (logarithmic axis)')
    ylabel = ('Minimum number of edges' if first['weight_model'] == 'unit'
              else 'Minimum total edge weight')
    ax.set_ylabel(r'First-passage time $\tau(x,y)$ — ' + ylabel)
    n = int(first['n'])
    counts = [row['trials'] for row in summaries]
    trial_text = str(counts[0]) if min(counts) == max(counts) else f'{min(counts)}–{max(counts)}'
    weight_text = ('unit weights' if first['weight_model'] == 'unit'
                   else f"Exp(rate={float(first['rate']):g}) weights")
    ax.set_title('First-passage times on a cycle with random shortcuts\n'
                 f"n={n:,} | ell={int(first['ell']):,} | "
                 f"expected shortcut degree={float(first['expected_shortcut_degree']):g}\n"
                 f'{trial_text} trials per distance | {weight_text}', pad=12)
    ax.grid(axis='y', alpha=0.2)
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False)
    fig.savefig(output / 'tau_plot.png', dpi=180)
    if show:
        plt.show()
    plt.close(fig)
    return summaries


def run_trials(args):
    n = args.n
    if n < 3 or args.trials < 1 or args.seed < 0:
        raise ValueError('Require n>=3, trials>=1, and seed>=0.')
    if not 0 <= args.x < n:
        raise ValueError('x must lie between 0 and n-1.')
    if not math.isfinite(args.rate) or args.rate <= 0:
        raise ValueError('rate must be finite and positive.')
    raw_ell = n / math.log(n) if args.ell is None else args.ell
    if not math.isfinite(raw_ell) or not 1 <= raw_ell <= n / 2:
        # The default n/log(n) exceeds n/2 for very small n: clamp only the default.
        if args.ell is None:
            raw_ell = n // 2
        else:
            raise ValueError('ell must be finite and between 1 and n/2.')
    ell = math.floor(raw_ell)
    total = eligible_shortcut_count(n, ell)
    if total > np.iinfo(np.int64).max:
        raise ValueError('Too many candidate edges for 64-bit integer indexing.')
    eligible_degree = 2 * total // n
    if args.p is not None:
        p = args.p
    elif eligible_degree:
        p = args.lambda_ / eligible_degree
    elif args.lambda_ == 0:
        p = 0.0
    else:
        raise ValueError('No eligible shortcuts: use --lambda 0 or increase ell.')
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError('Require 0<=p<=1; lambda cannot exceed eligible shortcut degree.')
    distances = parse_distances(args.distances, n)
    mode = 'independent_pairs' if args.independent_pairs else 'shared_graph'
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    print(f'n={n:,}; ell={ell:,}; p={p:.8g}; E[shortcut degree]={eligible_degree*p:g}')
    print(f'Eligible pairs={total:,}; E[shortcuts]={total*p:,.1f}')
    print(f'x={args.x}; cyclic distances={distances}; mode={mode}', flush=True)

    metadata = {
        'n': n, 'ell': ell, 'p': p, 'eligible_shortcut_pairs': total,
        'expected_shortcut_degree': eligible_degree*p,
        'weight_model': 'unit' if args.unweighted else 'exponential',
        'rate': args.rate if not args.unweighted else None,
        'x': args.x, 'distances': distances, 'trials_per_distance': args.trials,
        'sampling_mode': mode, 'seed': args.seed,
        'seed_recipe': 'np.random.default_rng(np.random.SeedSequence([seed, trial, stream]))',
        'seed_stream': 'cyclic distance for independent_pairs; 0 for shared_graph',
        'trial_numbering': '1-based',
        'versions': {'python': platform.python_version(), 'numpy': np.__version__,
                     'scipy': scipy.__version__},
    }
    with (output / 'run_metadata.json').open('w') as handle:
        json.dump(metadata, handle, indent=2)

    common = {key: metadata[key] for key in (
        'n', 'ell', 'p', 'eligible_shortcut_pairs', 'expected_shortcut_degree',
        'weight_model', 'rate', 'sampling_mode', 'seed', 'x')}
    columns = list(common) + [
        'trial', 'graph_id', 'seed_stream', 'y', 'cyclic_distance', 'tau',
        'shortcut_edges', 'generation_seconds', 'dijkstra_seconds',
    ]
    graph_count = 0
    graph_seconds = 0.0
    search_seconds = 0.0
    started = perf_counter()
    trials_path = output / 'tau_trials.csv'
    with trials_path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for trial in range(1, args.trials + 1):
            groups = [[distance] for distance in distances] if args.independent_pairs else [distances]
            for group in groups:
                stream = group[0] if args.independent_pairs else 0
                rng = np.random.default_rng(np.random.SeedSequence([args.seed, trial, stream]))
                t0 = perf_counter()
                graph, shortcut_edges = make_graph(n, ell, p, rng, args.rate, args.unweighted)
                t1 = perf_counter()
                # Both orientations are stored with equal weight. directed=True
                # therefore gives undirected distances without making a transpose.
                # indices=x is essential: never compute an n-by-n all-pairs result.
                tau = dijkstra(graph, indices=args.x, directed=True,
                               return_predecessors=False, unweighted=args.unweighted)
                t2 = perf_counter()
                graph_count += 1
                graph_seconds += t1 - t0
                search_seconds += t2 - t1
                for distance in group:
                    y = (args.x + distance) % n
                    writer.writerow({
                        **common, 'trial': trial, 'graph_id': graph_count,
                        'seed_stream': stream, 'y': y, 'cyclic_distance': distance,
                        'tau': float(tau[y]), 'shortcut_edges': shortcut_edges,
                        'generation_seconds': t1 - t0, 'dijkstra_seconds': t2 - t1,
                    })
                handle.flush()
                del graph, tau  # Do not retain earlier graphs between trials.
            print(f'Trial {trial:>2}/{args.trials}: {perf_counter()-started:.2f}s elapsed', flush=True)
    elapsed = perf_counter() - started
    metadata.update(graphs_generated=graph_count, simulation_seconds=elapsed,
                    total_generation_seconds=graph_seconds,
                    total_dijkstra_seconds=search_seconds)
    with (output / 'run_metadata.json').open('w') as handle:
        json.dump(metadata, handle, indent=2)
    summarize_and_plot(trials_path, output, args.show)
    print(f'{graph_count} graphs in {elapsed:.2f}s (plotting excluded).')
    print(f'Generation: {graph_seconds:.2f}s; Dijkstra: {search_seconds:.2f}s.')
    print(f'Saved trials, summary, plot, and metadata to {output.resolve()}')


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--n', type=int, default=200000)
    parser.add_argument('--trials', type=int, default=20)
    parser.add_argument('--ell', type=float, help='Max shortcut cyclic distance; floored. Default: n/log(n).')
    probability = parser.add_mutually_exclusive_group()
    probability.add_argument('--lambda', dest='lambda_', type=float, default=0.25,
                             help='Expected shortcut degree per vertex (default: 0.25).')
    probability.add_argument('--p', type=float, help='Shortcut probability; alternative to --lambda.')
    parser.add_argument('--rate', type=float, default=1.0, help='Exponential rate for all edge weights.')
    parser.add_argument('--unweighted', action='store_true', help='Use unit weights on every edge.')
    parser.add_argument('--x', type=int, default=0)
    parser.add_argument('--distances', nargs='+', help='E.g. 10 20 50 logn sqrt n/2. Rounded down.')
    parser.add_argument('--independent-pairs', action='store_true')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--output', default='results')
    parser.add_argument('--show', action='store_true', help='Also display the plot interactively.')
    parser.add_argument('--plot-only', metavar='CSV', help='Replot an existing trial CSV without simulating.')
    args = parser.parse_args()
    try:
        if args.plot_only:
            summarize_and_plot(args.plot_only, args.output, args.show)
        else:
            run_trials(args)
    except (ValueError, OverflowError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
