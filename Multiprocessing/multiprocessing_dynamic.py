import sys
import time
import statistics
import multiprocessing as mp
from pathlib import Path

import pandas as pd

#pipeline.py.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from pipeline import process_image, get_image_paths

#Konfiguration
LAPTOP_ID = 1
RUNS = 10
CHUNKSIZE = 1
IMAGE_COUNTS = [100, 500, 1000, 5000]
PROCESS_COUNTS = [1, 2, 4, 8]

NIH_DIR = PROJECT_DIR / "data" / "nih_chest_xray"
KAGGLE_DIR = PROJECT_DIR / "data" / "kaggle_pneumonia"

RESULTS_DIR = SCRIPT_DIR / "results" / f"laptop{LAPTOP_ID}"
RESULTS_CSV = RESULTS_DIR / f"results_dynamic_laptop{LAPTOP_ID}.csv"


def process_path(path):
    process_image(path)


def run_dynamic(image_paths, n_processes):
    start = time.perf_counter()

    if n_processes == 1:
        for path in image_paths:
            process_path(path)
    else:
        ctx = mp.get_context("spawn")

        with ctx.Pool(n_processes) as pool:
            for _ in pool.imap_unordered(
                process_path,
                image_paths,
                chunksize=CHUNKSIZE,
            ):
                pass

    return time.perf_counter() - start


def benchmark():
    rows = []

    datasets = [
        ("NIH", get_image_paths(str(NIH_DIR))),
        ("Kaggle Pneumonia", get_image_paths(str(KAGGLE_DIR))),
    ]

    for dataset_name, image_paths in datasets:
        print(f"\n=== {dataset_name} ===")

        for image_count in IMAGE_COUNTS:
            subset = image_paths[:image_count]

            if len(subset) < image_count:
                continue

            baseline_time = None

            for n_processes in PROCESS_COUNTS:
                runtimes = [
                    run_dynamic(subset, n_processes)
                    for _ in range(RUNS)
                ]

                runtime = statistics.median(runtimes)

                if n_processes == 1:
                    baseline_time = runtime

                speedup = baseline_time / runtime

                rows.append({
                    "Laptop": LAPTOP_ID,
                    "Variante": "Dynamic",
                    "Datensatz": dataset_name,
                    "Bilder": image_count,
                    "Prozesse": n_processes,
                    "Laufzeit in s": round(runtime, 3),
                    "Speedup": round(speedup, 3),
                    "Efficiency": round(speedup / n_processes, 3),
                    "Throughput": round(image_count / runtime, 2),
                })

                print(
                    f"{image_count} Bilder | "
                    f"{n_processes} Prozesse | "
                    f"Median: {runtime:.3f}s"
                )

    return pd.DataFrame(rows)


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results = benchmark()
    results.to_csv(RESULTS_CSV, index=False)

    print(f"\nGespeichert: {RESULTS_CSV}")


if __name__ == "__main__":
    mp.freeze_support()
    main()
