from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


COMPARE_IMAGES = 1000
COMPARE_WORKERS = 8
COMPARE_LARGE_IMAGES = 5000
SHOW_PLOTS = False

PROJECT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = PROJECT_DIR / "results"
PLOT_DIR = RESULTS_DIR / "plots_all_laptops"


def load_results():
    files = sorted(
        RESULTS_DIR.glob("laptop*/results_all_laptop*.csv")
    )

    if not files:
        raise FileNotFoundError(
            "Keine CSVs gefunden. "
            "Zuerst visualize_laptop.py auf jedem Laptop ausführen."
        )

    return pd.concat(
        [pd.read_csv(path) for path in files],
        ignore_index=True,
    )


def save_plot(filename):
    plt.tight_layout()
    plt.savefig(PLOT_DIR / filename, dpi=150)

    if SHOW_PLOTS:
        plt.show()
    else:
        plt.close()


def plot_metric_by_worker(df, metric, ylabel, filename):
    for dataset in sorted(df["Datensatz"].unique()):
        group = df[
            (df["Datensatz"] == dataset)
            & (df["Bilder"] == COMPARE_IMAGES)
            & (df["Variante"] != "Baseline")
        ]

        plt.figure(figsize=(10, 6))

        for (laptop, variant), sub in group.groupby(
            ["Laptop", "Variante"]
        ):
            sub = sub.sort_values("Worker")
            plt.plot(
                sub["Worker"],
                sub[metric],
                marker="o",
                label=f"{variant} — Laptop {laptop}",
            )

        plt.title(
            f"{ylabel} — {dataset} — {COMPARE_IMAGES} Bilder"
        )
        plt.xlabel("Worker")
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.legend(fontsize=7)

        name = dataset.lower().replace(" ", "_")
        save_plot(f"{filename}_{name}.png")


def plot_runtime_by_image_count(df):
    for dataset in sorted(df["Datensatz"].unique()):
        group = df[df["Datensatz"] == dataset]

        plt.figure(figsize=(10, 6))

        for (laptop, variant), sub in group.groupby(
            ["Laptop", "Variante"]
        ):
            worker = 1 if variant == "Baseline" else COMPARE_WORKERS
            sub = sub[sub["Worker"] == worker].sort_values("Bilder")

            if not sub.empty:
                plt.plot(
                    sub["Bilder"],
                    sub["Laufzeit in s"],
                    marker="o",
                    label=f"{variant} — Laptop {laptop}",
                )

        plt.title(
            f"Baseline vs. parallele Varianten — {dataset}"
        )
        plt.xlabel("Bildanzahl")
        plt.ylabel("Laufzeit in s")
        plt.grid(True)
        plt.legend(fontsize=7)

        name = dataset.lower().replace(" ", "_")
        save_plot(f"runtime_by_image_count_{name}.png")


def plot_runtime_by_worker(df):
    for dataset in sorted(df["Datensatz"].unique()):
        group = df[
            (df["Datensatz"] == dataset)
            & (df["Bilder"] == COMPARE_LARGE_IMAGES)
            & (df["Variante"] != "Baseline")
        ]

        plt.figure(figsize=(10, 6))

        for (laptop, variant), sub in group.groupby(
            ["Laptop", "Variante"]
        ):
            sub = sub.sort_values("Worker")
            plt.plot(
                sub["Worker"],
                sub["Laufzeit in s"],
                marker="o",
                label=f"{variant} — Laptop {laptop}",
            )

        plt.title(
            f"Laufzeit — {dataset} — "
            f"{COMPARE_LARGE_IMAGES} Bilder"
        )
        plt.xlabel("Worker")
        plt.ylabel("Laufzeit in s")
        plt.grid(True)
        plt.legend(fontsize=7)

        name = dataset.lower().replace(" ", "_")
        save_plot(f"runtime_by_worker_{name}.png")


def plot_amdahl(df):
    parallel_fraction = 0.95
    worker_range = np.linspace(1, COMPARE_WORKERS, 100)
    amdahl = 1 / (
        (1 - parallel_fraction) + parallel_fraction / worker_range
    )

    for dataset in sorted(df["Datensatz"].unique()):
        group = df[
            (df["Datensatz"] == dataset)
            & (df["Bilder"] == COMPARE_IMAGES)
            & (df["Variante"] != "Baseline")
        ]

        plt.figure(figsize=(10, 6))
        plt.plot(worker_range, amdahl, label="Amdahl (f=0.95)")
        plt.plot(
            range(1, COMPARE_WORKERS + 1),
            range(1, COMPARE_WORKERS + 1),
            label="Ideal",
        )

        for (laptop, variant), sub in group.groupby(
            ["Laptop", "Variante"]
        ):
            sub = sub.sort_values("Worker")
            plt.plot(
                sub["Worker"],
                sub["Speedup"],
                marker="o",
                label=f"{variant} — Laptop {laptop}",
            )

        plt.title(
            f"Amdahl vs. Messung — {dataset} — "
            f"{COMPARE_IMAGES} Bilder"
        )
        plt.xlabel("Worker")
        plt.ylabel("Speedup")
        plt.grid(True)
        plt.legend(fontsize=7)

        name = dataset.lower().replace(" ", "_")
        save_plot(f"amdahl_all_laptops_{name}.png")


def main():
    PLOT_DIR.mkdir(parents=True, exist_ok=True)

    results = load_results()
    results.to_csv(
        RESULTS_DIR / "results_all_laptops.csv",
        index=False,
    )

    plot_runtime_by_image_count(results)
    plot_runtime_by_worker(results)

    plot_metric_by_worker(
        results,
        "Speedup",
        "Speedup",
        "speedup_by_worker",
    )
    plot_metric_by_worker(
        results,
        "Efficiency",
        "Efficiency",
        "efficiency_by_worker",
    )
    plot_metric_by_worker(
        results,
        "Throughput",
        "Bilder pro Sekunde",
        "throughput_by_worker",
    )

    plot_amdahl(results)

    print(f"CSV:   {RESULTS_DIR / 'results_all_laptops.csv'}")
    print(f"Plots: {PLOT_DIR}")


if __name__ == "__main__":
    main()