from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


LAPTOP_ID = 1
COMPARE_IMAGES = 1000
MAX_WORKERS = 8
SHOW_PLOTS = False

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "results" / f"laptop{LAPTOP_ID}"
PLOT_DIR = OUTPUT_DIR / "plots"

COLUMNS = [
    "Laptop",
    "Variante",
    "Datensatz",
    "Bilder",
    "Worker",
    "Laufzeit in s",
    "Speedup",
    "Efficiency",
    "Throughput",
]


def load_csv(path, variant=None):
    if not path.exists():
        print(f"Fehlt: {path}")
        return None

    df = pd.read_csv(path)
    df = df.rename(columns={"Prozesse": "Worker"})

    if variant is not None:
        df["Variante"] = variant

    return df


def load_results():
    laptop = f"laptop{LAPTOP_ID}"

    frames = [
        load_csv(
            PROJECT_DIR
            / "Baseline"
            / "results"
            / laptop
            / f"results_baseline_laptop{LAPTOP_ID}.csv",
            "Baseline",
        ),
        load_csv(
            PROJECT_DIR
            / "Multiprocessing"
            / "results"
            / laptop
            / f"results_static_laptop{LAPTOP_ID}.csv",
            "Multiprocessing Static",
        ),
        load_csv(
            PROJECT_DIR
            / "Multiprocessing"
            / "results"
            / laptop
            / f"results_dynamic_laptop{LAPTOP_ID}.csv",
            "Multiprocessing Dynamic",
        ),
        load_csv(
            PROJECT_DIR
            / "Threading"
            / "results"
            / laptop
            / f"results_threading_laptop{LAPTOP_ID}.csv",
        ),
    ]

    frames = [df for df in frames if df is not None]

    if not frames:
        raise FileNotFoundError("Keine Ergebnisdateien gefunden.")

    results = pd.concat(frames, ignore_index=True)

    return results[COLUMNS]


def save_plot(filename):
    plt.tight_layout()
    plt.savefig(PLOT_DIR / filename, dpi=150)

    if SHOW_PLOTS:
        plt.show()
    else:
        plt.close()


def file_name(text):
    return text.lower().replace(" ", "_")


def plot_variant_overviews(df):
    for (variant, dataset), group in df.groupby(
        ["Variante", "Datensatz"]
    ):
        workers = sorted(group["Worker"].unique())
        image_counts = sorted(group["Bilder"].unique())

        fig, axes = plt.subplots(2, 2, figsize=(13, 9))
        fig.suptitle(
            f"{variant} — {dataset} — Laptop {LAPTOP_ID}"
        )

        for worker in workers:
            sub = group[
                group["Worker"] == worker
            ].sort_values("Bilder")

            axes[0, 0].plot(
                sub["Bilder"],
                sub["Laufzeit in s"],
                marker="o",
                label=f"{worker} Worker",
            )

        for image_count in image_counts:
            sub = group[
                group["Bilder"] == image_count
            ].sort_values("Worker")

            axes[0, 1].plot(
                sub["Worker"],
                sub["Speedup"],
                marker="o",
                label=f"{image_count} Bilder",
            )

            axes[1, 0].plot(
                sub["Worker"],
                sub["Efficiency"],
                marker="o",
                label=f"{image_count} Bilder",
            )

            axes[1, 1].plot(
                sub["Worker"],
                sub["Throughput"],
                marker="o",
                label=f"{image_count} Bilder",
            )

        axes[0, 0].set(
            title="Laufzeit",
            xlabel="Bildanzahl",
            ylabel="Laufzeit in s",
        )

        axes[0, 1].set(
            title="Speedup",
            xlabel="Worker",
            ylabel="Speedup",
        )

        axes[1, 0].set(
            title="Efficiency",
            xlabel="Worker",
            ylabel="Efficiency",
        )

        axes[1, 1].set(
            title="Throughput",
            xlabel="Worker",
            ylabel="Bilder pro Sekunde",
        )

        for ax in axes.flat:
            ax.grid(True)
            ax.legend(fontsize=8)

        save_plot(
            f"overview_{file_name(variant)}_"
            f"{file_name(dataset)}_laptop{LAPTOP_ID}.png"
        )


def plot_all_variants(df):
    for dataset in sorted(df["Datensatz"].unique()):
        group = df[df["Datensatz"] == dataset]

        fig, axes = plt.subplots(2, 2, figsize=(13, 9))
        fig.suptitle(
            f"Alle Varianten — {dataset} — Laptop {LAPTOP_ID}"
        )

        for variant, variant_df in group.groupby("Variante"):
            worker = 1 if variant == "Baseline" else MAX_WORKERS

            runtime_df = variant_df[
                variant_df["Worker"] == worker
            ].sort_values("Bilder")

            compare_df = variant_df[
                variant_df["Bilder"] == COMPARE_IMAGES
            ].sort_values("Worker")

            if not runtime_df.empty:
                axes[0, 0].plot(
                    runtime_df["Bilder"],
                    runtime_df["Laufzeit in s"],
                    marker="o",
                    label=variant,
                )

            if not compare_df.empty:
                axes[0, 1].plot(
                    compare_df["Worker"],
                    compare_df["Speedup"],
                    marker="o",
                    label=variant,
                )

                axes[1, 0].plot(
                    compare_df["Worker"],
                    compare_df["Efficiency"],
                    marker="o",
                    label=variant,
                )

                axes[1, 1].plot(
                    compare_df["Worker"],
                    compare_df["Throughput"],
                    marker="o",
                    label=variant,
                )

        axes[0, 0].set(
            title="Baseline vs. parallele Varianten",
            xlabel="Bildanzahl",
            ylabel="Laufzeit in s",
        )

        axes[0, 1].set(
            title=f"Speedup bei {COMPARE_IMAGES} Bildern",
            xlabel="Worker",
            ylabel="Speedup",
        )

        axes[1, 0].set(
            title=f"Efficiency bei {COMPARE_IMAGES} Bildern",
            xlabel="Worker",
            ylabel="Efficiency",
        )

        axes[1, 1].set(
            title=f"Throughput bei {COMPARE_IMAGES} Bildern",
            xlabel="Worker",
            ylabel="Bilder pro Sekunde",
        )

        for ax in axes.flat:
            ax.grid(True)
            ax.legend(fontsize=8)

        save_plot(
            f"all_variants_{file_name(dataset)}_"
            f"laptop{LAPTOP_ID}.png"
        )


def plot_static_vs_dynamic(df):
    variants = [
        "Multiprocessing Static",
        "Multiprocessing Dynamic",
        "Threading Static",
        "Threading Dynamic",
    ]

    for dataset in sorted(df["Datensatz"].unique()):
        dataset_df = df[
            (df["Datensatz"] == dataset)
            & (df["Variante"].isin(variants))
        ]

        for image_count in sorted(
            dataset_df["Bilder"].unique()
        ):
            group = dataset_df[
                dataset_df["Bilder"] == image_count
            ]

            fig, axes = plt.subplots(2, 2, figsize=(13, 9))
            fig.suptitle(
                f"Static vs. Dynamic — {dataset} — "
                f"{image_count} Bilder — Laptop {LAPTOP_ID}"
            )

            metrics = [
                ("Laufzeit in s", "Laufzeit"),
                ("Speedup", "Speedup"),
                ("Efficiency", "Efficiency"),
                ("Throughput", "Throughput"),
            ]

            for ax, (column, title) in zip(
                axes.flat,
                metrics,
            ):
                for variant, variant_df in group.groupby(
                    "Variante"
                ):
                    variant_df = variant_df.sort_values(
                        "Worker"
                    )

                    ax.plot(
                        variant_df["Worker"],
                        variant_df[column],
                        marker="o",
                        label=variant,
                    )

                ax.set(
                    title=title,
                    xlabel="Worker",
                    ylabel=column,
                )

                ax.grid(True)
                ax.legend(fontsize=8)

            save_plot(
                f"static_vs_dynamic_{file_name(dataset)}_"
                f"{image_count}_laptop{LAPTOP_ID}.png"
            )


def plot_amdahl(df):
    parallel_fraction = 0.95

    worker_range = np.linspace(
        1,
        MAX_WORKERS,
        100,
    )

    amdahl = 1 / (
        (1 - parallel_fraction)
        + parallel_fraction / worker_range
    )

    for dataset in sorted(df["Datensatz"].unique()):
        group = df[
            (df["Datensatz"] == dataset)
            & (df["Bilder"] == COMPARE_IMAGES)
            & (df["Variante"] != "Baseline")
        ]

        plt.figure(figsize=(9, 6))

        plt.plot(
            worker_range,
            amdahl,
            label="Amdahl (f=0.95)",
        )

        plt.plot(
            range(1, MAX_WORKERS + 1),
            range(1, MAX_WORKERS + 1),
            label="Ideal",
        )

        for variant, variant_df in group.groupby(
            "Variante"
        ):
            variant_df = variant_df.sort_values("Worker")

            plt.plot(
                variant_df["Worker"],
                variant_df["Speedup"],
                marker="o",
                label=variant,
            )

        plt.title(
            f"Amdahl vs. Messung — {dataset} — "
            f"Laptop {LAPTOP_ID}"
        )

        plt.xlabel("Worker")
        plt.ylabel("Speedup")
        plt.grid(True)
        plt.legend(fontsize=8)

        save_plot(
            f"amdahl_{file_name(dataset)}_"
            f"laptop{LAPTOP_ID}.png"
        )


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOT_DIR.mkdir(parents=True, exist_ok=True)

    results = load_results()

    csv_path = (
        OUTPUT_DIR
        / f"results_all_laptop{LAPTOP_ID}.csv"
    )

    results.to_csv(csv_path, index=False)

    plot_variant_overviews(results)
    plot_all_variants(results)
    plot_static_vs_dynamic(results)
    plot_amdahl(results)

    print(f"CSV:   {csv_path}")
    print(f"Plots: {PLOT_DIR}")


if __name__ == "__main__":
    main()