# Parallel Systems: Benchmarking einer parallelen medizinischen Bildverarbeitung

Dieses Repository enthält den Code und die Ergebnisse für das Projekt **„Entwicklung und Benchmarking einer parallelen Anwendung“** im Kurs Parallel Systems an der HTW Berlin, Sommersemester 2026.

Ziel des Projekts ist der Vergleich einer sequenziellen und einer parallelen Bildverarbeitungspipeline mit Python Multiprocessing. Als Anwendungsfall werden Röntgen, also medizinische Bilder verarbeitet.

Der Fokus liegt nicht auf medizinischer Diagnose, sondern auf der technischen Untersuchung der Parallelisierung.


## Aufgaben des Projekts

Ein einzelnes Bild wird dieser Pipeline verarbeitet:

1. Bild laden
2. Bildgröße zu 512×512 
3. Bild in Graustufen umwandeln
4. Helligkeit und Kontrast anpassen
5. Rauschen reduzieren, Blur-Filter
6. Histogramm der Grauwerte berechnen
7. Ergebnis speichern


## Testumgebung


| Laptop   | Prozessor                                |                  Kerne / Threads |    RAM | Betriebssystem |
| -------- | ---------------------------------------- | -------------------------------: | -----: | -------------- |
|  1 | Intel(R) Core(TM) Ultra 7 258V, 2200 MHz | 8 Kerne / 8 logische Prozessoren | 32 GB | Windows        |
|  2 | xxx                                      |                              xxx | xxx GB | xxx            |
|  3 | xxx                                      |                              xxx | xxx GB | xxx            |



## Varianten

Die Bildverarbeitung bleibt beiden Varianten identisch. Der Unterschied liegt  in der Ausführung:

| Variante | Name                       | Beschreibung                                                          |
| -------: | -------------------------- | --------------------------------------------------------------------- |
|        1 | Sequenziell     | Ein Prozess verarbeitet alle Bilder nacheinander         |
|        2 | Multiprocessing | Mehrere Prozesse verarbeiten mehrere Bilder parallel |


## Benchmark



## Ergebnisse - Platzhalter

### Beispiel: Bildverarbeitung

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

---

### Beispiel: Histogramm

<table width="100%">
  <tr>
    <td width="50%"><img src="images_output/histogram_original.png" width="100%"></td>
    <td width="50%"><img src="images_output/histogram_processed.png" width="100%"></td>
  </tr>
  <tr>
    <td align="center">Histogramm Originalbild</td>
    <td align="center">Histogramm nach Verarbeitung</td>
  </tr>
</table>

---

### Benchmark-Diagramme

<table width="100%">
  <tr>
    <td width="50%"><img src="plots/runtime_by_laptop.png" width="100%"></td>
    <td width="50%"><img src="plots/speedup_by_laptop.png" width="100%"></td>
  </tr>
  <tr>
    <td align="center">Laufzeitvergleich auf drei Laptops</td>
    <td align="center">Speedup-Vergleich auf drei Laptops</td>
  </tr>
  <tr>
    <td width="50%"><img src="plots/efficiency_by_processes.png" width="100%"></td>
    <td width="50%"><img src="plots/runtime_by_image_count.png" width="100%"></td>
  </tr>
  <tr>
    <td align="center">Efficiency bei unterschiedlicher Prozessanzahl</td>
    <td align="center">Laufzeit bei steigender Bildanzahl</td>
  </tr>
</table>

---

## Benchmark

| Laptop   | Bilder | Prozesse | Laufzeit in s | Speedup | Efficiency |
| -------- | -----: | -------: | ------------: | ------: | ---------: |
|  1 |     10 |        1 |           xxx |    1.00 |       1.00 |
|  1 |     10 |        2 |           xxx |     xxx |        xxx |
|  1 |     10 |        4 |           xxx |     xxx |        xxx |
|  1 |     10 |        8 |           xxx |     xxx |        xxx |
|  1 |     50 |        1 |           xxx |    1.00 |       1.00 |
|  1 |     50 |        2 |           xxx |     xxx |        xxx |
|  1 |     50 |        4 |           xxx |     xxx |        xxx |
|  1 |     50 |        8 |           xxx |     xxx |        xxx |
|  2 |     10 |        1 |           xxx |    1.00 |       1.00 |
|  2 |     10 |        2 |           xxx |     xxx |        xxx |
|  2 |     10 |        4 |           xxx |     xxx |        xxx |
|  2 |     10 |        8 |           xxx |     xxx |        xxx |
|  3 |     10 |        1 |           xxx |    1.00 |       1.00 |
|  3 |     10 |        2 |           xxx |     xxx |        xxx |
|  3 |     10 |        4 |           xxx |     xxx |        xxx |
|  3 |     10 |        8 |           xxx |     xxx |        xxx |

---

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
