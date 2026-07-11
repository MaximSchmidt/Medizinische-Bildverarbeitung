import sys
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from pipeline import process_image, get_image_paths


LAPTOP_ID = 1
RUNS = 10
IMAGE_COUNTS = [100, 500, 1000, 5000]
THREAD_COUNTS = [1, 2, 4, 8]

NIH_DIR = PROJECT_DIR / "data" / "nih_chest_xray"
KAGGLE_DIR = PROJECT_DIR / "data" / "kaggle_pneumonia"

RESULTS_DIR = SCRIPT_DIR / "results" / f"laptop{LAPTOP_ID}"
RESULTS_CSV = RESULTS_DIR / f"results_threading_laptop{LAPTOP_ID}.csv"


# Verarbeitet einen Chunk sequenziell
def process_chunk(chunk):
    for path in chunk:
        process_image(path)


# Statisch:
# Jeder Thread bekommt einmalig einen festen Chunk
def run_static(image_paths, n_threads):
    start = time.perf_counter()

    chunk_size = (len(image_paths) + n_threads - 1) // n_threads

    chunks = [
        image_paths[i:i + chunk_size]
        for i in range(0, len(image_paths), chunk_size)
    ]

    if n_threads == 1:
        process_chunk(chunks[0])
    else:
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            list(executor.map(process_chunk, chunks))

    return time.perf_counter() - start


# Dynamisch:
# Ein freier Thread übernimmt jeweils das nächste Bild.
def run_dynamic(image_paths, n_threads):
    start = time.perf_counter()

    if n_threads == 1:
        for path in image_paths:
            process_image(path)
    else:
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures = [
                executor.submit(process_image, path)
                for path in image_paths
            ]

            for future in as_completed(futures):
                future.result()

    return time.perf_counter() - start


def run_test(dataset_name, image_paths, variant, run_function):
    rows = []

    for image_count in IMAGE_COUNTS:
        subset = image_paths[:image_count]

        if len(subset) < image_count:
            continue

        baseline_time = None

        for n_threads in THREAD_COUNTS:
            runtimes = [
                run_function(subset, n_threads)
                for _ in range(RUNS)
            ]

            runtime = statistics.median(runtimes)

            if n_threads == 1:
                baseline_time = runtime

            speedup = baseline_time / runtime

            rows.append({
                "Laptop": LAPTOP_ID,
                "Variante": variant,
                "Datensatz": dataset_name,
                "Bilder": image_count,
                "Prozesse": n_threads,
                "Laufzeit in s": round(runtime, 3),
                "Speedup": round(speedup, 3),
                "Efficiency": round(speedup / n_threads, 3),
                "Throughput": round(image_count / runtime, 2),
            })

            print(
                f"{dataset_name} | {variant} | "
                f"{image_count} Bilder | {n_threads} Threads | "
                f"Median: {runtime:.3f}s"
            )

    return rows


def benchmark():
    nih_paths = get_image_paths(str(NIH_DIR))
    kaggle_paths = get_image_paths(str(KAGGLE_DIR))

    rows = []

    # NIH: statisch und dynamisch
    rows += run_test(
        "NIH",
        nih_paths,
        "Threading Static",
        run_static,
    )

    rows += run_test(
        "NIH",
        nih_paths,
        "Threading Dynamic",
        run_dynamic,
    )

    # Kaggle: statisch und dynamisch
    rows += run_test(
        "Kaggle Pneumonia",
        kaggle_paths,
        "Threading Static",
        run_static,
    )

    rows += run_test(
        "Kaggle Pneumonia",
        kaggle_paths,
        "Threading Dynamic",
        run_dynamic,
    )

    return pd.DataFrame(rows)


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results = benchmark()
    results.to_csv(RESULTS_CSV, index=False)

    print(f"\nGespeichert: {RESULTS_CSV}")


if __name__ == "__main__":
    main()