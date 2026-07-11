# Parallel Systems: Benchmarking einer parallelen medizinischen Bildverarbeitung

Dieses Repository enthält den Code und die Ergebnisse für das Projekt **„Entwicklung und Benchmarking einer parallelen Anwendung“** im Kurs Parallel Systems an der HTW Berlin, Sommersemester 2026.

Ziel des Projekts ist der Vergleich von Multiprocessing Ansätzen für die medizinische Bildverarbeitung. Als Anwendungsfall werden Röntgenbilder verarbeitet.

Der Fokus liegt nicht auf medizinischer Diagnose, sondern auf der technischen Untersuchung der Parallelisierung.


## Aufgaben des Projekts

Ein einzelnes Bild wird dieser Pipeline verarbeitet:

2. Bild laden und in Graustufen umwandeln
4. Median-Filter (entfernt Salt-and-Pepper Rauschen, damit CLAHE dieses Rauschen nicht mitverstärkt; Kernel 5 x 5)
5. Kontrastverstärkung mit CLAHE = Contrast Limited Adaptive Histogram Equalization (Kontrastverstärkung) (In Literatur z.B.: Altan, G., & Narlı, S. S. (2022). CLAHE based Enhancement to Transfer Learning in COVID-19 Detection. Gazi Journal of Engineering Sciences, 8(2), 406-416. https://izlik.org/JA75HG54CH)
6. Gauß-Filter (Weichzeichunung von Artefakten, die durch kachelbasierte Histogrammausgleichung entstehen können; Kernel 3 x 3)
7. Histogramm der Grauwerte berechnen


Die Bildverarbeitung erfolgt mit OpenCV. Die Parallelisierung erfolgt mit Python Multiprocessing,
aber ohne internes Multithreading, cv2.setNumThreads(1)


## Testumgebung


| Laptop   | Prozessor                                |                  Kerne / Threads |    RAM | Betriebssystem |
| -------- | ---------------------------------------- | -------------------------------: | -----: | -------------- |
|  1 | Intel(R) Core(TM) Ultra 7 258V, 2200 MHz | 8 Kerne / 8 logische Prozessoren | 32 GB | Windows        |
|  2 | AMD Ryzen 7 PRO 7840U   | 8 Kerne / 16 logische Prozessoren | 32 GB | Linux Mint 22.2             |
|  3 | xxx                                      |                              xxx | xxx GB | XXX      |



## Varianten

Die Bildverarbeitungspipeline mit OpenCV  bleibt in allen Varianten identisch. Nur die Verteilung der Bilder auf Prozesse oder Threads unterscheidet sich.

| Variante | Technologie | Beschreibung |
|---|---|---|
| Baseline | Python | Alle Bilder werden sequenziell verarbeitet |
| Multiprocessing Static | `multiprocessing.Process` | Die Bilder werden vor dem Start in Chunks aufgeteilt |
| Multiprocessing Dynamic | `multiprocessing.Pool.imap_unordered` |  Prozesse übernehmen dynamisch das jeweils nächste Bild |
| Threading Static | `ThreadPoolExecutor` | Jeder Thread erhält einen  Chunk von Bildern |
| Threading Dynamic | `ThreadPoolExecutor` | Jedes Bild wird einzeln als Aufgabe an den nächsten freien Thread vergeben |



# Benchmark

## Testdaten

Es werden zwei Testarten betrachtet:

| Nr. | Testart | Datensatz |
|---:|---|---|
| 1 | Steigende Bildanzahl bei gleicher Auflösung | [NIH Chest X-rays `images_002`](https://www.kaggle.com/datasets/nih-chest-xrays/data?resource=download-directory&select=images_002) |
| 2 | Steigende Bildanzahl bei unterschiedlicher Auflösung | [Chest X-Ray Images (Pneumonia)](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia/data) |



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


</table>


## Messung


Pro Kombination aus Bildanzahl, Variante und Prozessanzahl werden 10 Runs durchgeführt. Als Laufzeit wird der Median verwendet.

| Laptop | Variante | Bilder | Prozesse | Laufzeit in s | Speedup | Efficiency | Throughput |



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


