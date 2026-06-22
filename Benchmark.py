"""
Hauptskript für alle Benchmark-Läufe

Ausführung:
    python benchmark.py --input ./data --output ./output --results ./results/laptop2.csv

Optionen:
    --input      Verzeichnis mit Eingabebildern
    --output     Verzeichnis für verarbeitete Bilder
    --results    CSV-Datei für Messergebnisse
    --processes  Komma-getrennte Liste der Prozessanzahlen  (default: 1,2,4,8)
    --variants   Komma-getrennte Liste der Varianten        (default: all)
                 Mögliche Werte: sequential, static, dynamic
"""

import argparse
import cv2

# OpenCV internes Multithreading deaktivieren
# Parallelisierung soll ausschließlich auf Prozessebene stattfinden.
cv2.setNumThreads(1)

from variants.sequential import run as run_sequential
from variants.static_mp  import run as run_static
from variants.dynamic_mp import run as run_dynamic


def main():
    parser = argparse.ArgumentParser(description="Benchmark-Runner")
    parser.add_argument("--input",     required=True)
    parser.add_argument("--output",    required=True)
    parser.add_argument("--results",   required=True)
    parser.add_argument("--processes", default="1,2,4,8")
    parser.add_argument("--variants",  default="all")
    args = parser.parse_args()

    process_counts = [int(n) for n in args.processes.split(",")]
    run_all = args.variants == "all"
    selected = args.variants.split(",") if not run_all else []

    #Variante 1: Sequenziell (immer, dient als Baseline)
    if run_all or "sequential" in selected:
        print("\n" + "="*50)
        print("VARIANTE 1: Sequenziell")
        print("="*50)
        run_sequential(args.input, args.output, args.results)

    #Variante 2: Static Multiprocessing
    if run_all or "static" in selected:
        for n in process_counts:
            if n == 1:
                continue  # 1 Prozess = sequenziell, bereits oben gemessen
            print("\n" + "="*50)
            print(f"VARIANTE 2: Static Multiprocessing ({n} Prozesse)")
            print("="*50)
            run_static(args.input, args.output, args.results, n_processes=n)

    #Variante 3: Dynamic Multiprocessing
    if run_all or "dynamic" in selected:
        for n in process_counts:
            if n == 1:
                continue
            print("\n" + "="*50)
            print(f"VARIANTE 3: Dynamic Multiprocessing ({n} Prozesse)")
            print("="*50)
            run_dynamic(args.input, args.output, args.results, n_processes=n,
                        chunksize=1)

    print("\nAlle Läufe abgeschlossen. Ergebnisse in:", args.results)


if __name__ == "__main__":
    main()