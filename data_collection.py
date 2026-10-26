import csv
import math
import matplotlib.pyplot as plt

def collect_data(trials):
    averages = {}
    lambda_ = None
    with open("data.csv", mode="r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if not row or row[0] == "n":
                continue
            if len(row) == 5:  # n, l, lambda, p, t
                lambda_ = float(row[2])
            elif len(row) == 2:  # t, number of edges per vertex
                t, value = map(float, row)
                averages.setdefault(t, []).append(value)

    with open("averaged_data.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["t", "average", "theory"])
        for t, values in sorted(averages.items()):
            if len(values) != trials:
                raise ValueError(f"Expected {trials} trials for t={t}, found {len(values)}")
            average = sum(values) / trials
            theory = (2 + lambda_) * (1 - math.exp(-t))
            writer.writerow([t, average, theory])
            print(f"t={t:.1f}: average={average:.6f}, theory={theory:.6f}")


def plot_data(n):
    t_values = []
    averages = []
    theory = []

    with open("averaged_data.csv", mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            t_values.append(float(row["t"]))
            averages.append(float(row["average"]))
            theory.append(float(row["theory"]))

    plt.plot(t_values, averages, "o", label="Simulation average")
    plt.plot(t_values, theory, "-", label=r"Theory: $(2+\lambda)(1-e^{-t})$")

    plt.xlabel("t")
    plt.ylabel("Average number of edges below t per vertex")
    plt.title(f"Simulation vs. Theory (n = {n:,})")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("average_data.png")
    plt.show()