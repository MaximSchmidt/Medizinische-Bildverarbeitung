# Parallel Systems: Benchmarking einer parallelen medizinischen Bildverarbeitung

Dieses Repository enthält den Code und die Ergebnisse für das Projekt **„Entwicklung und Benchmarking einer parallelen Anwendung“** im Kurs Parallel Systems an der HTW Berlin, Sommersemester 2026.

Ziel des Projekts ist der Vergleich von Multiprocessing Ansätzen für die medizinische Bildverarbeitung. Als Anwendungsfall werden Röntgenbilder verarbeitet.

Der Fokus liegt nicht auf medizinischer Diagnose, sondern auf der technischen Untersuchung der Parallelisierung.


## Aufgaben des Projekts

Ein einzelnes Bild wird dieser Pipeline verarbeitet:

1. Bild laden
2. Bildgröße ändern (Resize auf 512 x 512 px)
3. Bild in Graustufen umwandeln (falls zuvor als RGB gespeichert, um Ressourcen zu sparen)
4. Median-Filter (entfernt Salt-and-Pepper Rauschen, damit CLAHE dieses Rauschen nicht mitverstärkt; Kernel 5 x 5)
5. CLAHE = Contrast Limited Adaptive Histogram Equalization (Kontrastverstärkung) (In Literatur z.B.: Altan, G., & Narlı, S. S. (2022). CLAHE based Enhancement to Transfer Learning in COVID-19 Detection. Gazi Journal of Engineering Sciences, 8(2), 406-416. https://izlik.org/JA75HG54CH)
6. Gauß-Filter (Weichzeichunung von Artefakten, die durch kachelbasierte Histogrammausgleichung entstehen können; Kernel 3 x 3)
7. Histogramm der Grauwerte berechnen
8. Ergebnis speichern


Die Bildverarbeitung erfolgt mit OpenCV. Die Parallelisierung erfolgt mit Python Multiprocessing,
aber ohne internes Multithreading, cv2.setNumThreads(1)


## Testumgebung


| Laptop   | Prozessor                                |                  Kerne / Threads |    RAM | Betriebssystem |
| -------- | ---------------------------------------- | -------------------------------: | -----: | -------------- |
|  1 | Intel(R) Core(TM) Ultra 7 258V, 2200 MHz | 8 Kerne / 8 logische Prozessoren | 32 GB | Windows        |
|  2 | AMD Ryzen 7 PRO 7840U   | 8 Kerne / 16 logische Prozessoren | 32 GB | Linux Mint 22.2             |
|  3 | xxx                                      |                              xxx | xxx GB | XXX      |



## Varianten

Die Bildverarbeitung bleibt in allen Varianten identisch. Der Unterschied in der Verteilung der Bilder auf Prozesse.

| Variante | Name | Technologie | Beschreibung |
| -------: | ---- | ----------- | ------------ |
| 1 | Sequenziell | Python + OpenCV | Ein Prozess verarbeitet alle Bilder nacheinander |
| 2 | Multiprocessing static | Python `multiprocessing.Process` + OpenCV | Die Bilder werden auf mehrere Prozesse aufgeteilt |
| 3 | Multiprocessing dynamic | Python `multiprocessing.Pool` / `Queue` + OpenCV | Prozesse holen sich dynamisch neue Bilder, sobald sie fertig bearbeitet sind |
| 4 | Multithreading | Python `ThreadPoolExecutor` / `threading` + OpenCV | Mehrere Threads verarbeiten Bilder parallel|



# Benchmark

## Testdaten

Es werden zwei Testarten betrachtet:

1. Steigende Bildanzahl bei gleicher Auflösung

2. Steigende Bildanzahl bei unterschiedlicher Auflösung

Datensatz:

- Kaggle Pneumonia Dataset (~5.000 Bilder, 14 Klassen, variable Auflösung) Link: https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia


## Ergebnisse - Platzhalter

### Bildverarbeitung

<table width="100%">
  <tr>
    <td width="30%"><img src="images_input/example_original.png" width="100%"></td>
    <td align="center" width="5%">></td>
    <td width="30%"><img src="images_output/example_gray.png" width="100%"></td>
    <td align="center" width="5%">></td>
    <td width="30%"><img src="images_output/example_processed.png" width="100%"></td>
  </tr>
  <tr>
    <td align="center">Originalbild</td>
    <td></td>
    <td align="center">Graustufenbild</td>
    <td></td>
    <td align="center">Kontrast / Helligkeit / Filter</td>
  </tr>
</table>


### Histogramm

<table width="100%">
  <tr>
    <td width="100%"><img src="images_output/histogram.png" width="100%"></td>
  </tr>
  <tr>
    <td align="center">Histogramm der Grauwerte</td>
  </tr>
</table>


### Diagramme

<table width="100%">
  <tr>
    <td width="100%"><img src="plots/runtime_by_image_count_all_laptops.png" width="100%"></td>
  </tr>
  <tr>
    <td align="center">Laufzeit bei steigender Bildanzahl auf allen drei Laptops.</td>
  </tr>

  <tr>
    <td width="100%"><img src="plots/speedup_by_processes_all_laptops.png" width="100%"></td>
  </tr>
  <tr>
    <td align="center">Speedup bei 2, 4 und 8 Prozessen auf allen drei Laptops.</td>
  </tr>

  <tr>
    <td width="100%"><img src="plots/efficiency_by_processes_all_laptops.png" width="100%"></td>
  </tr>
  <tr>
    <td align="center">Efficiency bei 2, 4 und 8 Prozessen auf allen drei Laptops.</td>
  </tr>

  <tr>
    <td width="100%"><img src="plots/static_vs_dynamic_all_laptops.png" width="100%"></td>
  </tr>
  <tr>
    <td align="center">Vergleich von Baselinem, Static, Dynamic Multiprocessing auf allen drei Laptops.</td>
  </tr>
</table>


## Messung


Pro Kombination aus Bildanzahl, Variante und Prozessanzahl werden 10 Runs durchgeführt. Als Laufzeit wird der Median verwendet.

| Laptop | Variante | Bilder | Prozesse | Laufzeit in s | Speedup | Efficiency | Throughput |
| -----: | -------- | -----: | -------: | ------------: | ------: | ---------: | ---------: |
| 1 | Sequenziell | 100 | 1 | xxx | 1.00 | 1.00 | xxx |
| 1 | Static | 100 | 2 | xxx | xxx | xxx | xxx |
| 1 | Static | 100 | 4 | xxx | xxx | xxx | xxx |
| 1 | Static | 100 | 8 | xxx | xxx | xxx | xxx |
| 1 | Dynamic | 100 | 2 | xxx | xxx | xxx | xxx |
| 1 | Dynamic | 100 | 4 | xxx | xxx | xxx | xxx |
| 1 | Dynamic | 100 | 8 | xxx | xxx | xxx | xxx |
| 1 | Sequenziell | 500 | 1 | xxx | 1.00 | 1.00 | xxx |
| 1 | Static | 500 | 2 | xxx | xxx | xxx | xxx |
| 1 | Static | 500 | 4 | xxx | xxx | xxx | xxx |
| 1 | Static | 500 | 8 | xxx | xxx | xxx | xxx |
| 1 | Dynamic | 500 | 2 | xxx | xxx | xxx | xxx |
| 1 | Dynamic | 500 | 4 | xxx | xxx | xxx | xxx |
| 1 | Dynamic | 500 | 8 | xxx | xxx | xxx | xxx |
| 1 | Sequenziell | 1000 | 1 | xxx | 1.00 | 1.00 | xxx |
| 1 | Static | 1000 | 2 | xxx | xxx | xxx | xxx |
| 1 | Static | 1000 | 4 | xxx | xxx | xxx | xxx |
| 1 | Static | 1000 | 8 | xxx | xxx | xxx | xxx |
| 1 | Dynamic | 1000 | 2 | xxx | xxx | xxx | xxx |
| 1 | Dynamic | 1000 | 4 | xxx | xxx | xxx | xxx |
| 1 | Dynamic | 1000 | 8 | xxx | xxx | xxx | xxx |
| 1 | Sequenziell | 5000 | 1 | xxx | 1.00 | 1.00 | xxx |
| 1 | Static | 5000 | 2 | xxx | xxx | xxx | xxx |
| 1 | Static | 5000 | 4 | xxx | xxx | xxx | xxx |
| 1 | Static | 5000 | 8 | xxx | xxx | xxx | xxx |
| 1 | Dynamic | 5000 | 2 | xxx | xxx | xxx | xxx |
| 1 | Dynamic | 5000 | 4 | xxx | xxx | xxx | xxx |
| 1 | Dynamic | 5000 | 8 | xxx | xxx | xxx | xxx |
| 2 | Sequenziell | 100 | 1 | xxx | 1.00 | 1.00 | xxx |
| 2 | Static | 100 | 2 | xxx | xxx | xxx | xxx |
| 2 | Static | 100 | 4 | xxx | xxx | xxx | xxx |
| 2 | Static | 100 | 8 | xxx | xxx | xxx | xxx |
| 2 | Dynamic | 100 | 2 | xxx | xxx | xxx | xxx |
| 2 | Dynamic | 100 | 4 | xxx | xxx | xxx | xxx |
| 2 | Dynamic | 100 | 8 | xxx | xxx | xxx | xxx |
| 2 | Sequenziell | 500 | 1 | xxx | 1.00 | 1.00 | xxx |
| 2 | Static | 500 | 2 | xxx | xxx | xxx | xxx |
| 2 | Static | 500 | 4 | xxx | xxx | xxx | xxx |
| 2 | Static | 500 | 8 | xxx | xxx | xxx | xxx |
| 2 | Dynamic | 500 | 2 | xxx | xxx | xxx | xxx |
| 2 | Dynamic | 500 | 4 | xxx | xxx | xxx | xxx |
| 2 | Dynamic | 500 | 8 | xxx | xxx | xxx | xxx |
| 2 | Sequenziell | 1000 | 1 | xxx | 1.00 | 1.00 | xxx |
| 2 | Static | 1000 | 2 | xxx | xxx | xxx | xxx |
| 2 | Static | 1000 | 4 | xxx | xxx | xxx | xxx |
| 2 | Static | 1000 | 8 | xxx | xxx | xxx | xxx |
| 2 | Dynamic | 1000 | 2 | xxx | xxx | xxx | xxx |
| 2 | Dynamic | 1000 | 4 | xxx | xxx | xxx | xxx |
| 2 | Dynamic | 1000 | 8 | xxx | xxx | xxx | xxx |
| 2 | Sequenziell | 5000 | 1 | xxx | 1.00 | 1.00 | xxx |
| 2 | Static | 5000 | 2 | xxx | xxx | xxx | xxx |
| 2 | Static | 5000 | 4 | xxx | xxx | xxx | xxx |
| 2 | Static | 5000 | 8 | xxx | xxx | xxx | xxx |
| 2 | Dynamic | 5000 | 2 | xxx | xxx | xxx | xxx |
| 2 | Dynamic | 5000 | 4 | xxx | xxx | xxx | xxx |
| 2 | Dynamic | 5000 | 8 | xxx | xxx | xxx | xxx |
| 3 | Sequenziell | 100 | 1 | xxx | 1.00 | 1.00 | xxx |
| 3 | Static | 100 | 2 | xxx | xxx | xxx | xxx |
| 3 | Static | 100 | 4 | xxx | xxx | xxx | xxx |
| 3 | Static | 100 | 8 | xxx | xxx | xxx | xxx |
| 3 | Dynamic | 100 | 2 | xxx | xxx | xxx | xxx |
| 3 | Dynamic | 100 | 4 | xxx | xxx | xxx | xxx |
| 3 | Dynamic | 100 | 8 | xxx | xxx | xxx | xxx |
| 3 | Sequenziell | 500 | 1 | xxx | 1.00 | 1.00 | xxx |
| 3 | Static | 500 | 2 | xxx | xxx | xxx | xxx |
| 3 | Static | 500 | 4 | xxx | xxx | xxx | xxx |
| 3 | Static | 500 | 8 | xxx | xxx | xxx | xxx |
| 3 | Dynamic | 500 | 2 | xxx | xxx | xxx | xxx |
| 3 | Dynamic | 500 | 4 | xxx | xxx | xxx | xxx |
| 3 | Dynamic | 500 | 8 | xxx | xxx | xxx | xxx |
| 3 | Sequenziell | 1000 | 1 | xxx | 1.00 | 1.00 | xxx |
| 3 | Static | 1000 | 2 | xxx | xxx | xxx | xxx |
| 3 | Static | 1000 | 4 | xxx | xxx | xxx | xxx |
| 3 | Static | 1000 | 8 | xxx | xxx | xxx | xxx |
| 3 | Dynamic | 1000 | 2 | xxx | xxx | xxx | xxx |
| 3 | Dynamic | 1000 | 4 | xxx | xxx | xxx | xxx |
| 3 | Dynamic | 1000 | 8 | xxx | xxx | xxx | xxx |
| 3 | Sequenziell | 5000 | 1 | xxx | 1.00 | 1.00 | xxx |
| 3 | Static | 5000 | 2 | xxx | xxx | xxx | xxx |
| 3 | Static | 5000 | 4 | xxx | xxx | xxx | xxx |
| 3 | Static | 5000 | 8 | xxx | xxx | xxx | xxx |
| 3 | Dynamic | 5000 | 2 | xxx | xxx | xxx | xxx |
| 3 | Dynamic | 5000 | 4 | xxx | xxx | xxx | xxx |
| 3 | Dynamic | 5000 | 8 | xxx | xxx | xxx | xxx |



## Interpretation


## Getting Started

### Dependencies

* Python 3.10+
* NumPy
* pandas
* matplotlib
* Pillow
* OpenCV


## Installation


## Authors


## License

This project is licensed under the MIT License.

## Acknowledgments


## Notizen, Vorschlag: Aufteilung zwischen den Personen

### Variante A: Aufteilung nach Pipeline-Komponenten

Klare technische Trennung, jede Person hat einen abgeschlossenen Codebereich.

| Person | Bereich | Aufgaben |
|--------|---------|----------|
| **Person 1** | Preprocessing-Pipeline | Bild laden, Resize, Graustufen, Median-Filter, CLAHE, Gauß-Filter, Speichern · sequentielle Baseline-Implementierung · Histogramm-Vergleich vorher/nachher als visuelle Validierung |
| **Person 2** | Parallelisierung & Messung | `multiprocessing.Process` (static), `multiprocessing.Pool` (dynamic), Skalierung über 1 / 2 / 4 / 8 Prozesse, Laufzeitmessung via `time.perf_counter()`, CPU-Auslastung via `psutil`, Cross-Platform-Ausführung auf allen drei Testmaschinen |
| **Person 3** | Theorie & Auswertung | Amdahls Gesetz, Literaturrecherche (CLAHE-Paper, Multiprocessing-Grundlagen), Speedup-Kurven, Effizienz-Plots, Histogramm-Vergleiche, Visualisierung der Ergebnisse (matplotlib) |

**Vorteil:** klare Verantwortlichkeiten, minimale Merge-Konflikte.  
**Nachteil:** Person 2 ist von Person 1 blockiert; Pipeline muss als stabile API (`process_image(path) -> result`) definiert sein, bevor parallelisiert werden kann.

---

### Variante B: Aufteilung nach Experimentier-Strängen

Alle drei implementieren zunächst gemeinsam eine Basisversion (Pipeline + Parallelisierung), danach läuft jede Person einen eigenen Experimentierstrang.

**Gemeinsame Basis (alle drei):**
- Pipeline-Funktionen als Modul (`pipeline.py`)
- Sequentielle Baseline + erste Pool-Parallelisierung
- Einheitliches Logging- und Messformat (CSV-Export)

**Eigenständige Stränge:**

| Person | Strang | Inhalt |
|--------|--------|--------|
| **Person 1** | Dataset A | Kaggle Pneumonia Dataset · einheitliche Auflösung · alle Varianten (seq / static / dynamic) · Speedup-Kurven |
| **Person 2** | Dataset B | NIH Chest X-Ray · variable Auflösung · Untersuchung, ob Lastungleichgewicht bei unterschiedlichen Bildgrößen das dynamische Scheduling bevorzugt |
| **Person 3** | Scheduling-Vergleich | `multiprocessing.Pool` mit `chunksize=1` vs. größeren Chunks · `concurrent.futures.ProcessPoolExecutor` als Alternative · Vergleich der Overhead-Kosten |

**Vorteil:** alle verstehen den ganzen Stack, können gleichzeitig arbeiten, drei unabhängige Ergebnis-Dimensionen.  
**Nachteil:** höherer Koordinationsaufwand am Anfang (gemeinsame API, gemeinsames Datenformat).

