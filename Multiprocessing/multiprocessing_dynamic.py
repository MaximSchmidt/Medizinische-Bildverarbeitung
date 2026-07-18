#!/usr/bin/env python
# coding: utf-8

# Variante 3: Multiprocessing Dynamic
#
# Worker holen sich dynamisch neue Bilder aus einer internen Queue, sobald sie frei sind.
#
# Hypothese: Dynamic ist bei variabler Auflösung (Kaggle Pneumonia) im Vorteil, weil kein Prozess idle wartet
# während ein anderer noch ein großes Bild verarbeitet. Bei gleicher Auflösung (NIH) bringt Dynamic keinen Vorteil.
#
# Technologie: multiprocessing.Pool mit imap_unordered (chunksize=1)

# Imports

import sys
from scipy import stats

import multiprocessing
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import statistics
from pathlib import Path
from functools import partial

from pipeline import process_image, get_image_paths

# Konfiguration
# Hinweis: Bitte an eigenes lokales Set-Up anpassen
# (Laptop 1 = Maxim, Laptop 2 = Ella, Laptop 3 = Jordan)

LAPTOP_ID = 2

IMG_SIZE = (512, 512)
RUNS = 10

NIH_DIR    = "../data/nih_chest_xray"
KAGGLE_DIR = "../data/kaggle_pneumonia"

RESULTS_DIR = f"results/laptop{LAPTOP_ID}"
RESULTS_CSV = f"{RESULTS_DIR}/results_dynamic_laptop{LAPTOP_ID}.csv"

IMAGE_COUNTS   = [100, 500, 1000]
PROCESS_COUNTS = [1, 2, 4, 8]
CHUNKSIZE      = 1  # Chunksize 1 damit jeder Worker ein Bild verarbeitet


Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)


# 1. Get Images

nih_paths    = get_image_paths(NIH_DIR)
kaggle_paths = get_image_paths(KAGGLE_DIR)


# 2. Process Image
# process_image gibt ein Dictionary zurück und Pool leitet es direkt ans Hauptprogramm weiter.
# Hier brauchen wir kein manager.list() shared memory wie bei static.
# with multiprocessing.Pool() as pool: Am Ende des with-Blocks wird der Pool automatisch
# geschlossen und alle Worker-Prozesse beendet.

def run_dynamic(image_paths, n_processes, chunksize=1):
    t_start = time.perf_counter()
    with multiprocessing.Pool(processes=n_processes) as pool:
        results = list(pool.imap_unordered(process_image, image_paths, chunksize=chunksize))
    total_time = time.perf_counter() - t_start
    return total_time, results


# 2b. "True" Dynamic (explizite Queue)
# Echtes dynamisches Scheduling mit multiprocessing.Queue.
# Jeder Worker holt sich aktiv die nächste Aufgabe (kein Pool-internes Management).

def worker_dynamic_true(task_queue, result_queue):
    while True:
        path = task_queue.get()  # holt nächste Aufgabe aus Queue
        if path is None:         # Sentinel — keine Arbeit mehr
            break
        result = process_image(path)
        result_queue.put(result)


def run_dynamic_true(image_paths, n_processes):
    task_queue   = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    for path in image_paths:
        task_queue.put(path)

    for _ in range(n_processes):
        task_queue.put(None)

    processes = [
        multiprocessing.Process(
            target=worker_dynamic_true,
            args=(task_queue, result_queue)
        )
        for _ in range(n_processes)
    ]

    t_start = time.perf_counter()
    for p in processes: p.start()

    # Ergebnisse WÄHREND die Prozesse laufen einlesen
    results = []
    for _ in range(len(image_paths)):
        results.append(result_queue.get())

    for p in processes: p.join()
    total_time = time.perf_counter() - t_start

    return total_time, results


# 3. Run

def benchmark():
    rows = []

    datasets = [
        ("NIH",              nih_paths),
        ("Kaggle Pneumonia", kaggle_paths),
    ]

    for dataset_name, all_paths in datasets:
        print(f"\n=== {dataset_name} ===")

        for n_img in IMAGE_COUNTS:
            subset = all_paths[:n_img]
            if len(subset) < n_img:
                print(f"  Nur {len(subset)} Bilder verfügbar (angefragt: {n_img})")
                continue

            for n_proc in PROCESS_COUNTS:
                # Dynamic (Pool)
                runtimes = []
                for run in range(RUNS):
                    runtime, _ = run_dynamic(subset, n_proc, chunksize=CHUNKSIZE)
                    runtimes.append(runtime)

                median_runtime    = statistics.median(runtimes)
                median_throughput = n_img / median_runtime
                std_runtime       = statistics.stdev(runtimes)
                ci                = stats.t.interval(0.95, df=len(runtimes)-1, loc=median_runtime, scale=stats.sem(runtimes))

                rows.append({
                    "Laptop":        LAPTOP_ID,
                    "Variante":      "Dynamic",
                    "Datensatz":     dataset_name,
                    "Bilder":        n_img,
                    "Prozesse":      n_proc,
                    "Laufzeit in s": round(median_runtime, 3),
                    "Std":           round(std_runtime, 4),
                    "CI_low":        round(ci[0], 4),
                    "CI_high":       round(ci[1], 4),
                    "Speedup":       None,
                    "Efficiency":    None,
                    "Throughput":    round(median_throughput, 2),
                    "all_times":     str(runtimes),
                })
                print(f"  {n_img} Bilder | {n_proc} Prozesse | Dynamic | Median: {median_runtime:.3f}s ± {std_runtime:.4f}s")

                # Dynamic True (explizite Queue)
                runtimes = []
                for run in range(RUNS):
                    runtime, _ = run_dynamic_true(subset, n_proc)
                    runtimes.append(runtime)

                median_runtime    = statistics.median(runtimes)
                median_throughput = n_img / median_runtime
                std_runtime       = statistics.stdev(runtimes)
                ci                = stats.t.interval(0.95, df=len(runtimes)-1, loc=median_runtime, scale=stats.sem(runtimes))

                rows.append({
                    "Laptop":        LAPTOP_ID,
                    "Variante":      "Dynamic True",
                    "Datensatz":     dataset_name,
                    "Bilder":        n_img,
                    "Prozesse":      n_proc,
                    "Laufzeit in s": round(median_runtime, 3),
                    "Std":           round(std_runtime, 4),
                    "CI_low":        round(ci[0], 4),
                    "CI_high":       round(ci[1], 4),
                    "Speedup":       None,
                    "Efficiency":    None,
                    "Throughput":    round(median_throughput, 2),
                    "all_times":     str(runtimes),
                })
                print(f"  {n_img} Bilder | {n_proc} Prozesse | Dynamic True | Median: {median_runtime:.3f}s ± {std_runtime:.4f}s")

    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(f"CPU-Kerne verfügbar: {multiprocessing.cpu_count()}")

    nih_paths    = get_image_paths(NIH_DIR)
    kaggle_paths = get_image_paths(KAGGLE_DIR)

    print(f"NIH Bilder gefunden:              {len(nih_paths)}")
    print(f"Kaggle Pneumonia Bilder gefunden: {len(kaggle_paths)}")

    df = benchmark()

    # 4. Speedup und Efficiency
    df["Speedup"]    = None
    df["Efficiency"] = None

    for variante in ["Dynamic", "Dynamic True"]:
        mask = df["Variante"] == variante
        baseline = (
            df[mask & (df["Prozesse"] == 1)]
            .set_index(["Datensatz", "Bilder"])["Laufzeit in s"]
        )
        df.loc[mask, "Speedup"] = df[mask].apply(
            lambda r: round(baseline.get((r["Datensatz"], r["Bilder"]), float("nan")) / r["Laufzeit in s"], 3), axis=1
        )
        df.loc[mask, "Efficiency"] = df[mask].apply(
            lambda r: round(r["Speedup"] / r["Prozesse"], 3), axis=1
        )

    df.to_csv(RESULTS_CSV, index=False)
    print(f"Gespeichert: {RESULTS_CSV}")

    # 5. Plots
    Path("plots").mkdir(exist_ok=True)

    for dataset_name in ["NIH", "Kaggle Pneumonia"]:
        sub_ds = df[(df["Datensatz"] == dataset_name) & (df["Variante"] == "Dynamic")]

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle(f"Dynamic Multiprocessing — {dataset_name} — Laptop {LAPTOP_ID}")

        ax = axes[0]
        for n_proc in PROCESS_COUNTS:
            sub = sub_ds[sub_ds["Prozesse"] == n_proc]
            ax.errorbar(sub["Bilder"], sub["Laufzeit in s"],
                        yerr=sub["Std"], marker="o", capsize=4, label=f"{n_proc} Prozesse")
        ax.set_xlabel("Bildanzahl")
        ax.set_ylabel("Laufzeit in s")
        ax.set_title("Laufzeit")
        ax.legend()
        ax.grid(True)

        ax = axes[1]
        for n_img in IMAGE_COUNTS:
            sub = sub_ds[sub_ds["Bilder"] == n_img]
            if not sub.empty:
                ax.errorbar(sub["Prozesse"], sub["Speedup"],
                            yerr=sub["Std"], marker="o", capsize=4, label=f"{n_img} Bilder")
        ax.plot(PROCESS_COUNTS, PROCESS_COUNTS, "k--", alpha=0.4, label="Ideal")
        ax.set_xlabel("Prozesse")
        ax.set_ylabel("Speedup")
        ax.set_title("Speedup")
        ax.legend()
        ax.grid(True)

        ax = axes[2]
        for n_img in IMAGE_COUNTS:
            sub = sub_ds[sub_ds["Bilder"] == n_img]
            if not sub.empty:
                ax.errorbar(sub["Prozesse"], sub["Efficiency"],
                            yerr=sub["Std"], marker="o", capsize=4, label=f"{n_img} Bilder")
        ax.axhline(1.0, color="k", linestyle="--", alpha=0.4, label="Ideal")
        ax.set_xlabel("Prozesse")
        ax.set_ylabel("Efficiency")
        ax.set_title("Efficiency")
        ax.legend()
        ax.grid(True)

        plt.tight_layout()
        fname = f"{RESULTS_DIR}/dynamic_{dataset_name.lower().replace(' ', '_')}_laptop{LAPTOP_ID}.png"
        plt.savefig(fname, dpi=150)

    # Dynamic vs. Dynamic True
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f"Dynamic vs. Dynamic True — Laptop {LAPTOP_ID}")

    for ax, dataset_name in zip(axes, ["NIH", "Kaggle Pneumonia"]):
        for variant, color, marker in [
            ("Dynamic",      "darkorange", "o"),
            ("Dynamic True", "purple",     "s"),
        ]:
            sub = df[
                (df["Variante"]  == variant) &
                (df["Datensatz"] == dataset_name) &
                (df["Bilder"]    == 1000)
            ]
            if not sub.empty:
                ax.errorbar(sub["Prozesse"], sub["Laufzeit in s"],
                            yerr=sub["Std"], color=color, marker=marker,
                            capsize=4, label=variant)
        ax.set_title(dataset_name)
        ax.set_xlabel("Prozesse")
        ax.set_ylabel("Laufzeit in s")
        ax.legend()
        ax.grid(True)

    plt.tight_layout()
    fname = f"{RESULTS_DIR}/dynamic_vs_true_laptop{LAPTOP_ID}.png"
    plt.savefig(fname, dpi=150)

    # 6. Idle-Time Analyse
    # Veranschaulichung der Variation der Laufzeit zwischen den einzelnen Bildern

    for ds_label, paths in [("NIH", nih_paths[:200]), ("Kaggle Pneumonia", kaggle_paths[:200])]:
        if len(paths) == 0:
            continue

        _, results = run_dynamic(paths, n_processes=4)
        durations  = [r["duration_s"]    for r in results if r["success"]]
        sizes      = [r["original_size"] for r in results if r["success"] and r["original_size"]]
        pixels     = [w * h for w, h in sizes]

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        fig.suptitle(f"Einzelbild-Laufzeiten: {ds_label}")

        axes[0].hist(durations, bins=30, color="steelblue", edgecolor="white")
        axes[0].set_xlabel("Laufzeit pro Bild (s)")
        axes[0].set_ylabel("Anzahl Bilder")
        axes[0].set_title(f"Verteilung (Std: {np.std(durations)*1000:.1f} ms)")

        if pixels:
            axes[1].scatter(pixels, durations, alpha=0.4, s=10)
            axes[1].set_xlabel("Originalgröße (Pixel)")
            axes[1].set_ylabel("Laufzeit (s)")
            axes[1].set_title("Laufzeit vs. Bildgröße")

        plt.tight_layout()
        fname = f"{RESULTS_DIR}/idle_{ds_label.lower().replace(' ', '_')}_laptop{LAPTOP_ID}.png"
        plt.savefig(fname, dpi=150)

    print("Fertig.")