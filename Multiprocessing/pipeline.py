import cv2
import glob
import time
from pathlib import Path


cv2.setNumThreads(1)


def process_image(input_path: str) -> dict:

    t_start = time.perf_counter()

    result = {
        "input_path":   input_path,
        "original_size": None,
        "duration_s":   None,
        "histogram":    None,
        "success":      False,
        "error":        None,
    }

    try:
        # 1. Laden
        img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"Bild konnte nicht geladen werden: {input_path}")

        # Originalgröße speichern (für Lastanalyse bei variablen Auflösungen)
        h, w = img.shape[:2]
        result["original_size"] = (w, h)

        # 2. Resize auf 512x512
        img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_AREA)

        # 3. Graustufen - passiert direkt beim Laden via IMREAD_GRAYSCALE


        # 4. Median-Filter (5x5)
        img = cv2.medianBlur(img, 5)

        # 5. CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img = clahe.apply(img)

        # 6. Gauß-Filter (3x3)
        img = cv2.GaussianBlur(img, (3, 3), 0)

        # 7. Histogramm
        hist = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten().tolist()

        result["histogram"] = hist
        result["success"] = True
        # Schritt 8 Speichern gelöscht, zu viel Speicherplatz

    except Exception as e:
        result["error"] = str(e)

    result["duration_s"] = time.perf_counter() - t_start
    return result


def get_image_paths(input_dir: str, limit: int = None) -> list:
    patterns = ["*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"]
    all_files = set()
    for pattern in patterns:
        all_files.update(glob.glob(str(Path(input_dir) / pattern)))

    sorted_files = sorted(all_files, key=lambda p: Path(p).name)

    if limit is not None:
        sorted_files = sorted_files[:limit]

    return sorted_files