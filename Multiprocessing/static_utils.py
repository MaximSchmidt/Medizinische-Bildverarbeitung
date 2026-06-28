import multiprocessing as mp
import time
from queue import Empty

import numpy as np

from pipeline import process_image


def worker_static(chunk, result_queue):
    success_count = 0
    error_count = 0

    for path in chunk:
        result = process_image(path)

        if result["success"]:
            success_count += 1
        else:
            error_count += 1

    result_queue.put({
        "success": success_count,
        "errors": error_count
    })


def run_static(image_paths, n_processes):
    t_start = time.perf_counter()

    if n_processes == 1:
        success_count = 0
        error_count = 0

        for path in image_paths:
            result = process_image(path)

            if result["success"]:
                success_count += 1
            else:
                error_count += 1

        total_time = time.perf_counter() - t_start

        return total_time, [{
            "success": success_count,
            "errors": error_count
        }]

    chunks = [
        list(c)
        for c in np.array_split(image_paths, n_processes)
        if len(c) > 0
    ]

    ctx = mp.get_context("spawn")
    result_queue = ctx.Queue()

    processes = [
        ctx.Process(target=worker_static, args=(chunk, result_queue))
        for chunk in chunks
    ]

    for p in processes:
        p.start()

    results = []

    try:
        for _ in processes:
            results.append(result_queue.get(timeout=300))
    except Empty:
        for p in processes:
            p.terminate()
        raise RuntimeError("Worker hängt oder gibt kein Ergebnis zurück.")

    for p in processes:
        p.join()

    total_time = time.perf_counter() - t_start

    return total_time, results