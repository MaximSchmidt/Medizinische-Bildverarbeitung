"""
Das Skript liest Bilder aus folgenden zwei lokalen Ordnern ein:
  - same_size/ : 1000+ PNG-Bilder, alle 1024x1024 px (Aus dem Datensatz https://www.kaggle.com/datasets/nih-chest-xrays/data/data?select=images_002 aus images_002)
  - random_size/ : 5000+ JPEG-Bilder mit unterschiedlichen Auflösungen (Aus dem Datensatz https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia/data aus train)

Ausgabe (im Ordner pipeline_output/):
    results_test1_fixed.csv – Test 1: gleiche Auflösung (same_size/)
    results_test2_variable_static.csv – Test 2a: variable Auflösung, statisch
    results_test2_variable_dynamic.csv – Test 2b: variable Auflösung, dynamisch

Pipeline (pro Bild)
  1. Bild laden
  2. Resize auf 1024x1024 (nur Test 1)
  3. Graustufen
  4. Median-Filter 5x5 (entfernt Salt-and-Pepper vor CLAHE)
  5. CLAHE (Kontrastverstärkung, clipLimit=2.0, tileGrid=8x8)
  6. Gauß-Filter 3x3 (glättet Kachelartefakte von CLAHE)
  7. Histogramm berechnen
  8. Ergebnis speichern

Tests
  Test 1: Steigende Bildanzahl, Gleiche Auflösung
  Test 2a: Steigende Bildanzahl, Variable Auflösung, Statisches Scheduling
  Test 2b: Steigende Bildanzahl, Variable Auflösung, Dynamisches Scheduling
"""


# Bibliotheken ####################################################################

import random
import sys
import time
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import cv2
import numpy as np
import pandas as pd

# KONFIGURATION ####################################################################

CONFIG = {
    "same_size_dir":  Path("same_size"),
    "random_size_dir": Path("random_size"),
    "output_dir":     Path("pipeline_output"),
    "sample_sizes":   [100, 500, 1000, 5000],
    "thread_counts":  [1, 2, 4, 8, 16],
    "random_seed":    123,
}

# Maxims config
# SCRIPT_DIR = Path(__file__).resolve().parent
# PROJECT_DIR = SCRIPT_DIR.parent
# DATA_DIR = PROJECT_DIR / "data"

# CONFIG = {
#     "same_size_dir": DATA_DIR / "nih_chest_xray",
#     "random_size_dir": DATA_DIR / "kaggle_pneumonia",
#     "output_dir": SCRIPT_DIR / "pipeline_output" / "Laptop1_pipeline_output",
#     "sample_sizes": [100, 500, 1000, 5000],
#     "thread_counts": [1, 2, 4, 8],
#     "random_seed": 123,
# }

# WORKER-FUNKTIONEN ############################################################

"""
Bildverarbeitungs-Pipeline für TEST 1 -> feste Zielauflösung 1024x1024
Gibt ein Dictionary mit Metadaten zurück (oder eine Fehlermeldung)
"""
def process_image_fixed_size(arguments_as_tuple: tuple):

    # OpenCV auf Single-Thread setzen, damit OpenCV nicht selbst weitere Threads startet
    cv2.setNumThreads(1)

    image_path_as_string, output_directory_as_string = arguments_as_tuple # Tupel in zwei Variablen gespeichert

    start_time = time.perf_counter() # Startzeit merken

    image_path = Path(image_path_as_string) # Pfad-String in Path-Objekt umwandeln (path.stem oder path.name möglich)

    try:
        # Schritt 1: Bild laden #################################################
        # cv2.imread lädt Bild als NumPy-Array (Höhe x Breite x Farbkanäle)
        # cv2.IMREAD_COLOR -> immer als Farbbild laden (3 Kanäle: BGR, auch wenn grau)
        loaded_image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)

        # Wenn das Bild nicht geladen werden konnte, gibt cv2.imread None zurück -> abbrechen und Fehler zurückgeben
        if loaded_image is None:
            return {"file": image_path.name, "success": False, "error": "imread returned None"}

        # img.shape gibt (Höhe, Breite, Kanäle) zurück
        # [:2] -> nur ersten zwei Werte (Höhe und Breite)
        original_height, original_width = loaded_image.shape[:2]


        # Schritt 2: Resize auf 1024x1024 ###########################################
        # Das Bild wird auf 1024x1024 Pixel skaliert
        resized_image = cv2.resize(loaded_image, (1024, 1024), interpolation=cv2.INTER_LINEAR) # cv2.INTER_LINEAR -> bilineare Interpolation

        # Schritt 3: Graustufen ###################################################
        grayscale_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY) if resized_image.ndim == 3 else resized_image   # Farbbild (3 Känale) in Grausstufenbild (1 Kanal) umwandeln (nur wenn .ndim == 3, also 3 Känale existieren)

        # Schritt 4: Median-Filter (5x5) ########################################
        median_filtered_image = cv2.medianBlur(grayscale_image, 5)  # Entfernt Bildrauschen, Filter ersetzt jeden Pixel durch Median seiner 5x5 Nachbarn

        # Schritt 5: CLAHE (Contrast Limited Adaptive Histogram Equalization) ###
        # Verstärkt den lokalen Kontrast
        clahe_processor = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))     # clipLimit=2.0 begrenzt die maximale Kontrastverstärkung pro Kachel um Überlichtung zu vermeiden
        clahe_enhanced_image = clahe_processor.apply(median_filtered_image)

        # Schritt 6: Gauß-Filter (3x3) #########################################
        gauss_smoothed_image = cv2.GaussianBlur(clahe_enhanced_image, (3, 3), 0)

        # Schritt 7: Histogramm berechnen ######################################
        # Zählt Grauwerte (0–255) von jedem Pixel -> 256 Bins
        grayscale_histogram = cv2.calcHist([gauss_smoothed_image], [0], None, [256], [0, 256]).flatten()  # .flatten() wandelt 2D-Ergebnis von calcHist in 1D-Liste um

        # Ergebnis-Dictionary zurückgeben
        return {
            "file": image_path.name,       # Dateiname, z.B. "bild_001.png"
            "success": True,                   # Verarbeitung erfolgreich
            "orig_w": original_width,         # Originalbreite in Pixeln
            "orig_h": original_height,        # Originalhöhe in Pixeln
            "proc_w": 1024,                   # Breite nach Resize
            "proc_h": 1024,                   # Höhe nach Resize
            "hist_mean": float(np.mean(grayscale_histogram)),  # Mittlerer Grauwert
            "hist_std": float(np.std(grayscale_histogram)),   # Streuung der Grauwerte
            "elapsed_s": time.perf_counter() - start_time,     # Laufzeit in Sekunden
        }

    except Exception as error_exception:
        # Fehler wird hier abgefangen und als Dictionary zurückgegeben
        return {"file": image_path.name, "success": False, "error": str(error_exception)}  # Das Programm läuft weiter


"""
Bildverarbeitungs-Pipeline für TEST 2 -> variable Originalauflösung, kein Resize
Für statisches/ dynamisches Scheduling (executor.map vs. executor.submit)
"""
def process_image_variable_size(arguments_as_tuple: tuple):
    cv2.setNumThreads(1)

    image_path_string, output_directory_string = arguments_as_tuple
    start_time = time.perf_counter()
    image_path = Path(image_path_string)

    try:
        # Schritt 1: Bild laden ###############################################
        loaded_image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if loaded_image is None:
            return {"file": image_path.name, "success": False, "error": "imread returned None"}

        original_height, original_width = loaded_image.shape[:2]

        # Schritt 2: KEIN Resize ##############################################
        # Die Originalauflösung bleibt erhalten, das ist der Unterschied zu Test 1

        # Schritt 3: Graustufen ###############################################
        grayscale_image = cv2.cvtColor(loaded_image, cv2.COLOR_BGR2GRAY) if loaded_image.ndim == 3 else loaded_image

        # Schritt 4: Median-Filter (5x5) ######################################
        median_filtered_image = cv2.medianBlur(grayscale_image, 5)

        # Schritt 5: CLAHE ####################################################
        clahe_processor = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_enhanced_image = clahe_processor.apply(median_filtered_image)

        # Schritt 6: Gauß-Filter (3x3) ########################################
        gauss_smoothed_image = cv2.GaussianBlur(clahe_enhanced_image, (3, 3), 0)

        # Schritt 7: Histogramm ###############################################
        grayscale_histogram = cv2.calcHist([gauss_smoothed_image], [0], None, [256], [0, 256]).flatten()

        return {
            "file": image_path.name,
            "success": True,
            "orig_w": original_width,
            "orig_h": original_height,
            "proc_w": original_width,   # kein Resize → gleich wie Original
            "proc_h": original_height,
            "pixel_count": original_width * original_height,   # Gesamtpixelzahl (für Laufzeit-Analyse)
            "hist_mean": float(np.mean(grayscale_histogram)),
            "hist_std": float(np.std(grayscale_histogram)),
            "elapsed_s": time.perf_counter() - start_time,
        }

    except Exception as error_exception:
        return {"file": image_path.name, "success": False, "error": str(error_exception)}


# DATENSATZ-HILFSFUNKTIONEN ##################################################

def collect_image_paths(folder: Path, extensions: set):
    return sorted(p for p in folder.iterdir()    # Alphabetisch sortiert
                  if p.is_file() and p.suffix.lower() in extensions)   # extension (Endung wie .png oder .jpeg) in Kleinbuschstaben p.suffix.lower() (".PNG" -> ".png")


"""
Gibt Statistiken zu einem Bildordner aus:
Anzahl Bilder, Dateigröße, Auflösungen, Bildfläche
"""
def print_dataset_info(image_paths: list, label: str):
    print(f"\nDatensatz: {label} {'─' * max(0, 45 - len(label))}")
    print(f"  │  Bilder insgesamt : {len(image_paths):>6,}")

    if not image_paths:
        print("(leer)")
        return

    # Dateigröße jedes Bildes in Bytes auslesen (nur Metadaten, kein Laden des Bildinhalts)
    file_sizes_in_bytes = [single_path.stat().st_size for single_path in image_paths]
    minimum_file_size = min(file_sizes_in_bytes)
    maximum_file_size = max(file_sizes_in_bytes)
    average_file_size = sum(file_sizes_in_bytes) / len(file_sizes_in_bytes)

    print(f"  │")
    print(f"  │  Dateigröße (Bytes)")
    print(f"  │  Minimum          : {minimum_file_size:>10,} B  ({minimum_file_size / 1024:,.1f} KB)")
    print(f"  │  Maximum          : {maximum_file_size:>10,} B  ({maximum_file_size / 1024:,.1f} KB)")
    print(f"  │  Durchschnitt     : {average_file_size:>10,.0f} B  ({average_file_size / 1024:,.1f} KB)")

    all_widths = []
    all_heights = []
    number_of_failed_reads = 0

    for single_path in image_paths:
        # cv2.IMREAD_UNCHANGED -> Bild so laden wie es ist (inkl. Alphakanal falls vorhanden)
        loaded_image = cv2.imread(str(single_path), cv2.IMREAD_UNCHANGED)
        if loaded_image is not None:
            image_height, image_width = loaded_image.shape[:2]
            all_widths.append(image_width)
            all_heights.append(image_height)
        else:
            number_of_failed_reads += 1

    if all_widths:
        minimum_width = min(all_widths)
        maximum_width = max(all_widths)
        minimum_height = min(all_heights)
        maximum_height = max(all_heights)
        average_width = sum(all_widths)  / len(all_widths)
        average_height = sum(all_heights) / len(all_heights)

        # Pixel-Fläche = Breite × Höhe jedes Bildes
        pixel_areas = [width * height for width, height in zip(all_widths, all_heights)]
        average_area = sum(pixel_areas) / len(pixel_areas)

        print(f"  │")
        print(f"  │  Bildauflösung (Pixel)")
        print(f"  │     Breite  min / max  : {minimum_width:>6} px  /  {maximum_width:>6} px")
        print(f"  │     Höhe    min / max  : {minimum_height:>6} px  /  {maximum_height:>6} px")
        print(f"  │     Ø Breite × Ø Höhe : {average_width:>6.0f} px  ×  {average_height:>6.0f} px")
        print(f"  │")
        print(f"  │  Bildfläche (Breite × Höhe)")
        print(f"  │     Durchschnitt       : {average_area:>12,.0f} px²")

    if number_of_failed_reads:
        print(f"  │  Nicht lesbar      : {number_of_failed_reads} Bild(er)")

    print(f" {'─' * 50}")


# BENCHMARK-ENGINE #################################################

"""
Statisches Scheduling -> ThreadPoolExecutor.map
executor.map verteilt die Aufgaben gleichmäßig auf alle Threads
Die Ergebnisse kommen in der gleichen Reihenfolge zurück wie die Eingabe (Vergleich mit pool.map aus Multiprocessing)
Gibt (Ergebnisliste, Gesamtlaufzeit_in_Sekunden) zurück
"""
def run_static(image_path_list: list, process_function, output_directory: Path, number_of_threads: int):
    # Jede Bildpfad in ein Tupel (pfad_string, ausgabeordner_string) verpacken,
    # weil die Worker-Funktion genau dieses Format erwartet
    task_arguments = [(str(single_path), str(output_directory)) for single_path in image_path_list]

    benchmark_start_time = time.perf_counter()

    if number_of_threads == 1:
        # Bei nur 1 Thread: direkt sequenziell ausführen, kein Thread-Overhead
        cv2.setNumThreads(1)
        results = [process_function(single_argument) for single_argument in task_arguments]
    else:
        # ThreadPoolExecutor startet einen Pool mit number_of_threads Threads
        # executor.map ruft process_function für jedes Element in task_arguments auf
        # und wartet bis alle fertig sind. list() erzwingt die vollständige Ausführung
        with ThreadPoolExecutor(max_workers=number_of_threads) as thread_pool_executor:
            results = list(thread_pool_executor.map(process_function, task_arguments))

    total_elapsed_time = time.perf_counter() - benchmark_start_time
    return results, total_elapsed_time


"""
Dynamisches Scheduling -> executor.submit + as_completed
Jeder Thread holt sich eine neue Aufgabe sobald er fertig ist
as_completed() gibt jedes Ergebnis zurück sobald es fertig ist (in Fertigstellungsreihenfolge) (Gleich wie pool.imap_unordered(chunksize=1))
Gibt (Ergebnisliste, Gesamtlaufzeit_in_Sekunden) zurück
"""
def run_dynamic(image_path_list: list, process_function, output_directory: Path, number_of_threads: int):

    task_arguments = [(str(single_path), str(output_directory)) for single_path in image_path_list]

    benchmark_start_time = time.perf_counter()

    if number_of_threads == 1:
        cv2.setNumThreads(1)
        results = [process_function(single_argument) for single_argument in task_arguments]
    else:
        results = []
        with ThreadPoolExecutor(max_workers=number_of_threads) as thread_pool_executor:
            # executor.submit schickt EINE Aufgabe an den Pool und gibt sofort
            # ein "Future"-Objekt zurück, ein Platzhalter für das spätere Ergebnis
            # Hier werden alle Aufgaben auf einmal eingereicht
            all_submitted_futures = [
                thread_pool_executor.submit(process_function, single_argument)
                for single_argument in task_arguments
            ]
            # as_completed wartet und gibt jedes Future zurück, sobald es fertig ist
            # future.result() gibt das eigentliche Ergebnis (das Dictionary) zurück
            for completed_future in as_completed(all_submitted_futures):
                results.append(completed_future.result())

    total_elapsed_time = time.perf_counter() - benchmark_start_time
    return results, total_elapsed_time



"""
Berechnet die Parallelisierungs-Metriken für einen Benchmark-Lauf

Speedup S_p = T_1 / T_p -> wie viel schneller als 1 Thread?
Efficiency E_p = S_p / p -> wie gut wird jeder Thread ausgelastet? (1.0 = ideal)
Throughput R = N / T_p -> wie viele Bilder pro Sekunde?
"""
def compute_metrics(number_of_images: int, number_of_threads: int, elapsed_time: float,
                    baseline_time_with_one_thread: float, test_name: str,
                    scheduling: str = ""):

    speedup_factor = baseline_time_with_one_thread / elapsed_time if elapsed_time > 0 else 0.0
    efficiency_per_thread = speedup_factor / number_of_threads if number_of_threads > 0 else 0.0
    images_per_second = number_of_images / elapsed_time if elapsed_time > 0 else 0.0

    return {
        "test": test_name,
        "scheduling": scheduling,
        "bilder": number_of_images,
        "threads": number_of_threads,
        "laufzeit_s": round(elapsed_time, 4),
        "speedup": round(speedup_factor, 4),
        "efficiency": round(efficiency_per_thread, 4),
        "throughput": round(images_per_second, 2),
    }


# TEST-RUNNER #####################################################################


"""
Diese Funktion gibt am Ende eine Tabelle zurück, die dann als CSV
gespeichert und in visualize.py für Plots verwendet wird
"""
def run_test(
    all_paths: list,
    process_fn,
    test_label: str,
    sample_sizes: list,
    thread_counts: list,
    output_dir: Path,
    scheduling: str = "static",
) -> pd.DataFrame:    # Tabelle aus der Pandas Bilbiothek
    all_result_rows = [] # Liste der Ergebnisse als Dic mit pd.DataFrame(rows)

    scheduling_function = run_static if scheduling == "static" else run_dynamic # Static oder dynamic case für Auswahl der richtigen Funktion

    for number_of_images_in_sample in sample_sizes:
        actual_sample_size = min(number_of_images_in_sample, len(all_paths)) # Nicht mehr Bilder ziehen als vorhanden

        sampled_image_paths = random.sample(all_paths, actual_sample_size) # Zufällige Stichprobe

        baseline_time_single_thread = None  # 1 Thread Laufzeit als Referenz für den Vergleich der anderen Laufzeiten

        print(f"\n{'='*60}")
        print(f"  {test_label} | {scheduling.upper()} | {actual_sample_size} Bilder")
        print(f"{'='*60}")

        for number_of_threads in thread_counts:
            print(f" ->  {number_of_threads:2d} Thread(s) [{scheduling:7s}] ... ", end="", flush=True)

            # Test ausführen und Laufzeit messen
            _, elapsed_time_seconds = scheduling_function(
                sampled_image_paths, process_fn, output_dir, number_of_threads
            )
            print(f"{elapsed_time_seconds:.3f} s")

            # Ersten Lauf (1 Thread) als Baseline speichern
            if baseline_time_single_thread is None:
                baseline_time_single_thread = elapsed_time_seconds

            # Metriken berechnen und als neue Zeile speichern
            all_result_rows.append(compute_metrics(
                actual_sample_size, number_of_threads,
                elapsed_time_seconds, baseline_time_single_thread,
                test_label, scheduling
            ))

    # Liste von Dictionaries in pandas-Tabelle umwandeln und zurückgeben
    return pd.DataFrame(all_result_rows)


# AUSGABE-HILFSFUNKTIONEN #####################################################

"""
Gibt die Benchmark-Ergebnisse formatiert auf der Konsole aus
"""
def print_results_table(results_dataframe: pd.DataFrame):   # "-> None" Funktion gibt nichts zurück
    column_widths = [30, 9, 7, 9, 12, 9, 11, 14]
    header_names = ["Test", "Scheduling", "Bilder", "Threads",
                     "Laufzeit(s)", "Speedup", "Efficiency", "Throughput"]

    separator_line = "  ".join("-" * width for width in column_widths)   # Trennlinie

    header_line = "  ".join(f"{name:<{width}}" for name, width in zip(header_names, column_widths)) # Kopfzeile mit Spaltentitel

    print(f"\n  {header_line}")
    print(f"  {separator_line}")


    for _, single_row in results_dataframe.iterrows():  # iterrows() geht durch jede Zeile der Tabelle
        print(
            f"{single_row['test']:<30}     "
            f"{single_row['scheduling']:<9} "
            f"{int(single_row['bilder']):>7}  "
            f"{int(single_row['threads']):>9} "
            f"{single_row['laufzeit_s']:>11.3f}    "
            f"{single_row['speedup']:>9.3f}    "
            f"{single_row['efficiency']:>11.3f}    "
            f"{single_row['throughput']:>14.2f}    "
        )


# HAUPTPROGRAMM ###################################################################

def main():
    random.seed(CONFIG["random_seed"])
    output_directory = CONFIG["output_dir"]


    output_directory.mkdir(parents=True, exist_ok=True)    # Ausgabeordner erstellen falls er noch nicht existiert

    print("-" * 60)
    print("  Parallele Bildverarbeitungs-Pipeline (THREADING) - Parallel Systems 2026")
    print("-" * 60)
    print(f" CPU-Kerne: {mp.cpu_count()}")
    print(f" OpenCV: {cv2.__version__}")
    print(sys.version)
    print(f" same_size/: {CONFIG['same_size_dir'].resolve()}")
    print(f" random_size/: {CONFIG['random_size_dir'].resolve()}")
    print(f" Ausgabe: {output_directory.resolve()}")

    print("\n Datensätze einlesen ")

    same_size_directory = CONFIG["same_size_dir"]
    random_size_directory = CONFIG["random_size_dir"]

    for folder in (same_size_directory, random_size_directory):
        if not folder.exists():
            print(f"\n  FEHLER: Ordner '{folder.resolve()}' nicht gefunden.")
            print("-> Pfade in CONFIG oben anpassen.")
            sys.exit(1)

    same_size_image_paths = collect_image_paths(same_size_directory, extensions={".png"})
    random_size_image_paths = collect_image_paths(random_size_directory, extensions={".jpg", ".jpeg"})

    if not same_size_image_paths:
        print(f"\n  FEHLER: Keine PNG-Bilder in '{same_size_directory.resolve()}'")
        sys.exit(1)
    if not random_size_image_paths:
        print(f"\n  FEHLER: Keine JPEG-Bilder in '{random_size_directory.resolve()}'")
        sys.exit(1)

    print(f"  DONE  {len(same_size_image_paths):,} Bilder in same_size/")
    print(f"  DONE  {len(random_size_image_paths):,} Bilder in random_size/")

    print("\n\n ## Datensatz-Statistiken ##")
    print("  (wird einmalig vor den Tests berechnet)")
    print_dataset_info(same_size_image_paths, label="same_size   (PNG, 1024×1024)")
    print_dataset_info(random_size_image_paths, label="random_size (JPEG, variable Auflösung)")

    # Tests #####################################################################

    print("\n\n TEST 1: Gleiche Auflösung (same_size/ → Resize 1024×1024) ")
    results_test1 = run_test(
        all_paths = same_size_image_paths,
        process_fn = process_image_fixed_size,
        test_label = "Gleiche Aufloesung (1024x1024)",
        sample_sizes = CONFIG["sample_sizes"],
        thread_counts = CONFIG["thread_counts"],
        output_dir = output_directory,
        scheduling = "static",
    )

    print("\n\n TEST 2a: Variable Auflösung (random_size/) | Statisches Scheduling ")
    results_test2_static = run_test(
        all_paths = random_size_image_paths,
        process_fn = process_image_variable_size,
        test_label = "Variable Aufloesung",
        sample_sizes = CONFIG["sample_sizes"],
        thread_counts = CONFIG["thread_counts"],
        output_dir = output_directory,
        scheduling = "static",
    )

    print("\n\n TEST 2b: Variable Auflösung (random_size/) | Dynamisches Scheduling ")
    results_test2_dynamic = run_test(
        all_paths = random_size_image_paths,
        process_fn = process_image_variable_size,
        test_label = "Variable Aufloesung",
        sample_sizes = CONFIG["sample_sizes"],
        thread_counts = CONFIG["thread_counts"],
        output_dir = output_directory,
        scheduling = "dynamic",
    )

    # Ergebnisse ausgeben #######################################################
    print("\n\n GESAMTERGEBNISSE ")

    # pd.concat fügt mehrere DataFrames zusammen.
    # ignore_index=True setzt den Zeilenindex neu (0, 1, 2, ...) statt aus einzelnen Tabellen zu übernehmen
    all_results_combined = pd.concat(
        [results_test1, results_test2_static, results_test2_dynamic],
        ignore_index=True
    )
    print_results_table(all_results_combined)

    # CSV-Dateien schreiben #####################################################
    csv_output_files = {
        "results_threads_test1_fixed.csv": results_test1,
        "results_threads_test2_variable_static.csv": results_test2_static,
        "results_threads_test2_variable_dynamic.csv": results_test2_dynamic,
    }
    print("\n CSV-Dateien schreiben ")
    for csv_filename, dataframe_to_save in csv_output_files.items():
        csv_output_path = output_directory / csv_filename
        dataframe_to_save.to_csv(csv_output_path, index=False, sep=";") # ; als CSV-Trennzeichen setzen
        print(f"DONE {csv_output_path}")

    print(f"\n Fertig! visualize.py -> für die Plots")


# EINSTIEGSPUNKT #############################################################
# Bei Threads ist der __main__-Guard nicht zwingend nötig (kein spawn) -> Best Practice

if __name__ == "__main__":
    main()
