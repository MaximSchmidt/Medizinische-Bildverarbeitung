"""
Bildverarbeitungs-Pipeline

Stabile API für alle Varianten:
    process_image(input_path, output_path) -> dict

"""

import cv2
import numpy as np
import time
from pathlib import Path


def process_image(input_path: str, output_path: str) -> dict:
    """
    Verarbeitet ein einzelnes Bild durch die volle Pipeline und speichert das Ergebnis auf der Festplatte.

    Gibt eine Zusammenfassung als dict mit Metadaten zurück:
        {
            "input_path":    str,
            "output_path":   str,
            "duration_s":    float,   # Laufzeit in Sekunden
            "input_shape":   tuple,   # (H, W, C) des Originals (Height, Width, Channels also 1 für Graustufen).
                               Damit Vergleich vor dem Resize um zu schauen ob größere Bilder tatsächlich länger dauern
            "histogram":     list,    # 256 Einträge, Grauwert-Häufigkeiten
            "success":       bool
        }
    """
    meta = {"input_path": input_path, "output_path": output_path, "success": False}
    t_start = time.perf_counter()

    #Schritt 1: Bild laden
    img = cv2.imread(input_path)
    if img is None:
        meta["error"] = f"Bild konnte nicht geladen werden: {input_path}"
        return meta
    meta["input_shape"] = img.shape

    #Schritt 2: Resize auf 512 × 512 px
    img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_AREA)

    #Schritt 3: Graustufen
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #Schritt 4: Median-Filter (Kernel 5 × 5)
    # Entfernt impulsartiges Rauschen (Salt-and-Pepper) vor CLAHE,
    # damit CLAHE das Rauschen nicht mitverstärkt.
    img = cv2.medianBlur(img, 5)

    #Schritt 5: CLAHE
    # clipLimit:    Schwellenwert für Kontrastverstärkung (verhindert Rauschverstärkung)
    # tileGridSize: Kachelgröße für lokale Histogramm-Ausgleichung
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img = clahe.apply(img)

    #Schritt 6: Gauß-Filter (Kernel 3 × 3)
    # Glättet leichte Artefakte, die durch die kachelbasierte
    # Histogrammausgleichung entstehen können.
    img = cv2.GaussianBlur(img, (3, 3), sigmaX=0)

    #Schritt 7: Histogramm berechnen
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    meta["histogram"] = hist.flatten().tolist()

    #Schritt 8: Ergebnis speichern
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_path, img)

    meta["duration_s"] = time.perf_counter() - t_start
    meta["success"] = True
    return meta


    # parallel-imaging/
    # ├── requirements.txt
    # ├── pipeline.py
    # ├── benchmark.py
    # ├── variants/
    # │   ├── sequential.py
    # │   ├── static_mp.py
    # │   └── dynamic_mp.py
    # ├── data/                # nicht im Git (.gitignore)
    # ├── output/              # nicht im Git (.gitignore)
    # ├── results/
    # │   ├── laptop1.csv
    # │   ├── laptop2.csv
    # │   └── laptop3.csv
    # └── analysis.ipynb