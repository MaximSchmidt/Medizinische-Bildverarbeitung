"""
dataset_info.py
----------------
Alles rund um die zwei Bild-Datensätze:
  - Bildpfade aus einem Ordner einsammeln
  - Statistiken zu einem Ordner ausgeben (Anzahl, Dateigröße, Auflösung)

Wird von benchmark_threads.py importiert.
"""

from pathlib import Path
import cv2


def collect_image_paths(folder: Path, extensions: set) -> list:
    """
    Gibt eine sortierte Liste aller Bildpfade in 'folder' zurück,
    deren Dateiendung in 'extensions' enthalten ist (z.B. {".png"}).
    """
    return sorted(
        path for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in extensions
    )


def print_dataset_info(image_paths: list, label: str):
    """
    Gibt Statistiken zu einem Bildordner auf der Konsole aus:
    Anzahl Bilder, Dateigröße (min/max/durchschnitt), Auflösung (min/max/durchschnitt).
    """
    print(f"\nDatensatz: {label} {'─' * max(0, 45 - len(label))}")
    print(f"  │  Bilder insgesamt : {len(image_paths):>6,}")

    if not image_paths:
        print("  │  (leer)")
        return

    # Dateigröße jedes Bildes in Bytes (nur Metadaten, kein Laden des Bildinhalts)
    file_sizes = [path.stat().st_size for path in image_paths]

    print(f"  │")
    print(f"  │  Dateigröße (Bytes)")
    print(f"  │  Minimum          : {min(file_sizes):>10,} B  ({min(file_sizes) / 1024:,.1f} KB)")
    print(f"  │  Maximum          : {max(file_sizes):>10,} B  ({max(file_sizes) / 1024:,.1f} KB)")
    print(f"  │  Durchschnitt     : {sum(file_sizes) / len(file_sizes):>10,.0f} B "
          f" ({sum(file_sizes) / len(file_sizes) / 1024:,.1f} KB)")

    # Auflösung jedes Bildes ermitteln
    widths, heights = [], []
    failed_reads = 0

    for path in image_paths:
        image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if image is None:
            failed_reads += 1
            continue
        height, width = image.shape[:2]
        widths.append(width)
        heights.append(height)

    if widths:
        areas = [w * h for w, h in zip(widths, heights)]

        print(f"  │")
        print(f"  │  Bildauflösung (Pixel)")
        print(f"  │     Breite  min / max  : {min(widths):>6} px  /  {max(widths):>6} px")
        print(f"  │     Höhe    min / max  : {min(heights):>6} px  /  {max(heights):>6} px")
        print(f"  │     Ø Breite × Ø Höhe : {sum(widths) / len(widths):>6.0f} px  ×  {sum(heights) / len(heights):>6.0f} px")
        print(f"  │")
        print(f"  │  Bildfläche (Breite × Höhe)")
        print(f"  │     Durchschnitt       : {sum(areas) / len(areas):>12,.0f} px²")

    if failed_reads:
        print(f"  │  Nicht lesbar      : {failed_reads} Bild(er)")

    print(f" {'─' * 50}")
