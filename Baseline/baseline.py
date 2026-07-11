import sys
import time
import statistics
from pathlib import Path

import pandas as pd


#pipeline.py.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from pipeline import process_image, get_image_paths


# Konfiguration
LAPTOP_ID = 1
RUNS = 10

NIH_DIR = PROJECT_DIR / "data" / "nih_chest_xray"
KAGGLE_DIR = PROJECT_DIR / "data" / "kaggle_pneumonia"

RESULTS_DIR = SCRIPT_DIR / "results" / f"laptop{LAPTOP_ID}"
RESULTS_CSV = RESULTS_DIR / f"results_baseline_laptop{LAPTOP_ID}.csv"

IMAGE_COUNTS = [100, 500, 1000, 5000]


def run_baseline(image_paths):
    start = time.perf_counter()

    for path in image_paths:
        process_image(path)

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

            runtimes = [
                run_baseline(subset)
                for _ in range(RUNS)
            ]

            runtime = statistics.median(runtimes)

            rows.append({
                "Laptop": LAPTOP_ID,
                "Variante": "Baseline",
                "Datensatz": dataset_name,
                "Bilder": image_count,
                "Prozesse": 1,
                "Laufzeit in s": round(runtime, 3),
                "Speedup": 1.0,
                "Efficiency": 1.0,
                "Throughput": round(image_count / runtime, 2),
            })

            print(f"{image_count} Bilder | Median: {runtime:.3f}s")

    return pd.DataFrame(rows)

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results = benchmark()
    results.to_csv(RESULTS_CSV, index=False)

    print(f"\nGespeichert: {RESULTS_CSV}")


if __name__ == "__main__":
    main()
