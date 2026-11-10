"""Summarize shortest paths from shortest_paths.csv, one row per trial."""

import csv
import json


def average_distance(paths):
    """Mean number of edges (hops) in the paths."""
    return sum(len(path) - 1 for path in paths) / len(paths)


def longest_common_subsequence(paths):
    """Common suffix of paths from one shortest-path tree, ordered start to target.

    In a positive-weight undirected graph, shortest paths to one fixed target
    merge but never split, so their common suffix is their LCS.
    """
    reversed_paths = [path[::-1] for path in paths]
    common = []
    for vertices in zip(*reversed_paths):
        if len(set(vertices)) != 1:
            break
        common.append(vertices[0])
    return common[::-1]

'''
def analyze_csv(input_file="shortest_paths.csv", output_file="path_summary.csv"):
    with open(input_file, newline="", encoding="utf-8") as infile, \
         open(output_file, "w", newline="", encoding="utf-8") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.writer(outfile)
        writer.writerow(["trial", "num_paths", "average_distance_hops",
                         "common_subsequence", "common_subsequence_vertices"])

        for row in reader:
            path_dict = json.loads(row["paths"])
            paths = list(path_dict.values())
            if not paths:
                raise ValueError(f"Trial {row['trial']} contains no paths")

            common = longest_common_subsequence(paths)
            writer.writerow([row["trial"], len(paths), average_distance(paths),
                             json.dumps(common), len(common)])

    print(f"Saved {output_file}")
'''
import csv

def analyze_csv(input_file="6path_summary.csv",
                     output_file="6ratio_path_summary.csv"):

    with open(input_file, "r", newline="") as infile, \
         open(output_file, "w", newline="") as outfile:

        reader = csv.DictReader(infile)

        fieldnames = reader.fieldnames + ["ratio"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            average = float(row["average_distance_hops"])
            length = int(row["common_subsequence_vertices"])

            row["ratio"] = average / length if length > 0 else None

            writer.writerow(row)

    print(f"Saved {output_file}")

if __name__ == "__main__":
    analyze_csv()
