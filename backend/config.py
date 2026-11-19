import os

# Konfigurasi backend deteksi topi dan dasi
# GANTI IP ESP32 sesuai IP yang muncul di Serial Monitor Arduino IDE.

ESP32_CAPTURE_URL = "http://10.169.220.134:8080/capture"

# Lokasi model hasil training YOLO Anda.
# Letakkan file best.pt di folder backend/models/best.pt
MODEL_PATH = "models/best.pt"

# Confidence minimal. Naikkan jika terlalu sering salah deteksi.
CONF_THRESHOLD = 0.35

# Ukuran input YOLO.
IMG_SIZE = 640

# Nama class wajib sama dengan class saat labeling/training.
REQUIRED_CLASSES = ["topi", "dasi"]

# URL deployment Google Apps Script Web App yang berakhiran /exec.
GOOGLE_APPS_SCRIPT_URL = os.getenv("GOOGLE_APPS_SCRIPT_URL", "")
GOOGLE_LOG_INTERVAL_SECONDS = float(os.getenv("GOOGLE_LOG_INTERVAL_SECONDS", "10"))
