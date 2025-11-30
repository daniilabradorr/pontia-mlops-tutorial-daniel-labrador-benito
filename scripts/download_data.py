import os
from pathlib import Path
import urllib.request

#directorio raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

#URLs del dataset Adult (UCI)
TRAIN_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
TEST_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.test"

TRAIN_PATH = DATA_DIR / "adult.data"
TEST_PATH = DATA_DIR / "adult.test"

print(f"📥 Descargando train a {TRAIN_PATH}...")
urllib.request.urlretrieve(TRAIN_URL, TRAIN_PATH)

print(f"📥 Descargando test a {TEST_PATH}...")
urllib.request.urlretrieve(TEST_URL, TEST_PATH)

print("✅ Descarga completada.")
