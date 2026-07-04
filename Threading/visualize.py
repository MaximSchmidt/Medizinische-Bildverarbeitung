from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

LAPTOP_ID = 1
RUN_IDLE_ANALYSIS = False      # Für CSV-Plots auf False setzen
IDLE_IMAGE_COUNT = 200
IDLE_THREADS = 4
SHOW_PLOTS = False             # Bei vielen Plots auf False setzen


SCRIPT_DIR = Path(__file__).resolve().parent

POSSIBLE_RESULTS_DIRS = [
    SCRIPT_DIR / "pipeline_output" / "Laptop1_pipeline_output",
]

CSV_CONFIG = [
    {
        "file": "results_threads_test1_fixed.csv",
        "dataset": "NIH",
        "method": "Static Threading",
        "save_prefix": "static_nih",
    },
    {
        "file": "results_threads_test2_variable_static.csv",
        "dataset": "Kaggle Pneumonia",
        "method": "Static Threading",
        "save_prefix": "static_kaggle_pneumonia",
    },
    {
        "file": "results_threads_test2_variable_dynamic.csv",
        "dataset": "Kaggle Pneumonia",
        "method": "Dynamic Threading",
        "save_prefix": "dynamic_kaggle_pneumonia",
    },
]


def find_results_dir():
    for results_dir in POSSIBLE_RESULTS_DIRS:
        existing_files = [(results_dir / cfg["file"]).exists() for cfg in CSV_CONFIG]
        if any(existing_files):
            return results_dir

    raise FileNotFoundError(
        "Keine Ergebnis-CSV gefunden. Erst benchmark_threads.py ausführen."
    )


def load_results(results_dir):
    frames = []

    for cfg in CSV_CONFIG:
        csv_path = results_dir / cfg["file"]

        if not csv_path.exists():
            print(f"Überspringe fehlende Datei: {csv_path}")
            continue

        df = pd.read_csv(csv_path, sep=";")
        df["Datensatz"] = cfg["dataset"]
        df["Methode"] = cfg["method"]
        df["SavePrefix"] = cfg["save_prefix"]
        frames.append(df)

    if not frames:
        raise FileNotFoundError("Keine CSV-Dateien konnten geladen werden.")

    return pd.concat(frames, ignore_index=True)


def plot_benchmark_overview(df, results_dir):
    plot_dir = results_dir / "plots"
    plot_dir.mkdir(exist_ok=True)

    for save_prefix in df["SavePrefix"].unique():
        sub_ds = df[df["SavePrefix"] == save_prefix].copy()

        dataset_name = sub_ds["Datensatz"].iloc[0]
        method_name = sub_ds["Methode"].iloc[0]

        thread_counts = sorted(sub_ds["threads"].unique())
        image_counts = sorted(sub_ds["bilder"].unique())

        fig, axes = plt.subplots(1, 4, figsize=(20, 5))
        fig.suptitle(f"{method_name} — {dataset_name} — Laptop {LAPTOP_ID}")

        # 1) Laufzeit
        ax = axes[0]
        for n_threads in thread_counts:
            sub = sub_ds[sub_ds["threads"] == n_threads].sort_values("bilder")
            ax.plot(
                sub["bilder"],
                sub["laufzeit_s"],
                marker="o",
                label=f"{n_threads} Threads",
            )
        ax.set_xlabel("Bildanzahl")
        ax.set_ylabel("Laufzeit in s")
        ax.set_title("Laufzeit")
        ax.legend()
        ax.grid(True)

        # 2) Speedup
        ax = axes[1]
        for n_img in image_counts:
            sub = sub_ds[sub_ds["bilder"] == n_img].sort_values("threads")
            if not sub.empty:
                ax.plot(
                    sub["threads"],
                    sub["speedup"],
                    marker="o",
                    label=f"{n_img} Bilder",
                )

        ax.plot(thread_counts, thread_counts, "k--", alpha=0.4, label="Ideal")
        ax.set_xlabel("Threads")
        ax.set_ylabel("Speedup")
        ax.set_title("Speedup")
        ax.legend()
        ax.grid(True)

        # 3) Efficiency
        ax = axes[2]
        for n_img in image_counts:
            sub = sub_ds[sub_ds["bilder"] == n_img].sort_values("threads")
            if not sub.empty:
                ax.plot(
                    sub["threads"],
                    sub["efficiency"],
                    marker="o",
                    label=f"{n_img} Bilder",
                )

        ax.axhline(1.0, color="k", linestyle="--", alpha=0.4, label="Ideal")
        ax.set_xlabel("Threads")
        ax.set_ylabel("Efficiency")
        ax.set_title("Efficiency")
        ax.legend()
        ax.grid(True)

        # 4) Throughput
        ax = axes[3]
        for n_img in image_counts:
            sub = sub_ds[sub_ds["bilder"] == n_img].sort_values("threads")
            if not sub.empty:
                ax.plot(
                    sub["threads"],
                    sub["throughput"],
                    marker="o",
                    label=f"{n_img} Bilder",
                )

        ax.set_xlabel("Threads")
        ax.set_ylabel("Bilder pro Sekunde")
        ax.set_title("Throughput")
        ax.legend()
        ax.grid(True)

        plt.tight_layout()

        fname = plot_dir / f"{save_prefix}_laptop{LAPTOP_ID}.png"
        plt.savefig(fname, dpi=150)

        if SHOW_PLOTS:
            plt.show()
        else:
            plt.close()

        print(f"Gespeichert: {fname}")


def plot_static_vs_dynamic(df, results_dir):
    plot_dir = results_dir / "plots"
    plot_dir.mkdir(exist_ok=True)

    variable_df = df[df["Datensatz"] == "Kaggle Pneumonia"].copy()

    if variable_df.empty:
        return

    image_counts = sorted(variable_df["bilder"].unique())

    for n_img in image_counts:
        sub_img = variable_df[variable_df["bilder"] == n_img]

        fig, axes = plt.subplots(1, 4, figsize=(20, 5))
        fig.suptitle(f"Static vs. Dynamic Threading — Kaggle Pneumonia — {n_img} Bilder")

        metrics = [
            ("laufzeit_s", "Laufzeit in s", "Laufzeit"),
            ("speedup", "Speedup", "Speedup"),
            ("efficiency", "Efficiency", "Efficiency"),
            ("throughput", "Bilder pro Sekunde", "Throughput"),
        ]

        for ax, (metric, ylabel, title) in zip(axes, metrics):
            for method_name in sorted(sub_img["Methode"].unique()):
                sub = sub_img[sub_img["Methode"] == method_name].sort_values("threads")
                ax.plot(
                    sub["threads"],
                    sub[metric],
                    marker="o",
                    label=method_name.replace(" Threading", ""),
                )

            ax.set_xlabel("Threads")
            ax.set_ylabel(ylabel)
            ax.set_title(title)
            ax.legend()
            ax.grid(True)

        plt.tight_layout()

        fname = plot_dir / f"static_vs_dynamic_{n_img}_bilder_laptop{LAPTOP_ID}.png"
        plt.savefig(fname, dpi=150)

        if SHOW_PLOTS:
            plt.show()
        else:
            plt.close()

        print(f"Gespeichert: {fname}")


def plot_idle_analysis(results_dir):
    """
    Achtung:
    Die Einzelbild-Laufzeiten stehen NICHT in den CSV-Dateien.
    Deshalb wird hier ein kleiner Zusatzlauf mit 200 Bildern gemacht.
    """

    import benchmark_threads as bt

    plot_dir = results_dir / "plots"
    plot_dir.mkdir(exist_ok=True)

    datasets = [
        {
            "label": "NIH",
            "paths": bt.collect_image_paths(bt.CONFIG["same_size_dir"], {".png"}),
            "process_fn": bt.process_image_fixed_size,
        },
        {
            "label": "Kaggle Pneumonia",
            "paths": bt.collect_image_paths(bt.CONFIG["random_size_dir"], {".jpg", ".jpeg"}),
            "process_fn": bt.process_image_variable_size,
        },
    ]

    for ds in datasets:
        ds_label = ds["label"]
        paths = ds["paths"][:IDLE_IMAGE_COUNT]

        if len(paths) == 0:
            print(f"Keine Bilder gefunden für: {ds_label}")
            continue

        results, _ = bt.run_dynamic(
            image_path_list=paths,
            process_function=ds["process_fn"],
            output_directory=results_dir,
            number_of_threads=IDLE_THREADS,
        )

        durations = [
            r["elapsed_s"]
            for r in results
            if r.get("success")
        ]

        pixels = [
            r["orig_w"] * r["orig_h"]
            for r in results
            if r.get("success") and r.get("orig_w") and r.get("orig_h")
        ]

        if not durations:
            print(f"Keine gültigen Einzelbild-Laufzeiten für: {ds_label}")
            continue

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        fig.suptitle(f"Einzelbild-Laufzeiten: {ds_label} — Laptop {LAPTOP_ID}")

        axes[0].hist(durations, bins=30, color="steelblue", edgecolor="white")
        axes[0].set_xlabel("Laufzeit pro Bild in s")
        axes[0].set_ylabel("Anzahl Bilder")
        axes[0].set_title(f"Verteilung (Std: {np.std(durations) * 1000:.1f} ms)")
        axes[0].grid(True)

        if pixels:
            axes[1].scatter(pixels, durations, alpha=0.4, s=10)
            axes[1].set_xlabel("Originalgröße in Pixel")
            axes[1].set_ylabel("Laufzeit in s")
            axes[1].set_title("Laufzeit vs. Bildgröße")
            axes[1].grid(True)

        plt.tight_layout()

        fname = plot_dir / f"idle_{ds_label.lower().replace(' ', '_')}_laptop{LAPTOP_ID}.png"
        plt.savefig(fname, dpi=150)

        if SHOW_PLOTS:
            plt.show()
        else:
            plt.close()

        print(f"Gespeichert: {fname}")


def main():
    results_dir = find_results_dir()
    df = load_results(results_dir)

    combined_path = results_dir / "results_threads_combined.csv"
    df.to_csv(combined_path, index=False, sep=";")

    print(f"CSV geladen aus: {results_dir}")
    print(f"Kombinierte CSV: {combined_path}")

    plot_benchmark_overview(df, results_dir)
    plot_static_vs_dynamic(df, results_dir)

    if RUN_IDLE_ANALYSIS:
        plot_idle_analysis(results_dir)

    print("Fertig.")


if __name__ == "__main__":
    main()