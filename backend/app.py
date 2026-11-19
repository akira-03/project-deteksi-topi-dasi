import base64
import csv
import os
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import requests
import torch
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from config import (
    CONF_THRESHOLD,
    ESP32_CAPTURE_URL,
    GOOGLE_APPS_SCRIPT_URL,
    GOOGLE_LOG_INTERVAL_SECONDS,
    IMG_SIZE,
    MODEL_PATH,
    REQUIRED_CLASSES,
)
from google_sheets import GoogleSheetsLogger

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent
CAPTURE_DIR = BASE_DIR / "captures"
RESULT_DIR = BASE_DIR / "results"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "detection_log.csv"

CAPTURE_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

model = None
google_sheets = GoogleSheetsLogger(
    apps_script_url=GOOGLE_APPS_SCRIPT_URL,
    min_interval=GOOGLE_LOG_INTERVAL_SECONDS,
)


def load_model():
    """Load custom Ultralytics YOLO model."""
    global model
    if model is not None:
        return model

    model_path = BASE_DIR / MODEL_PATH
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model tidak ditemukan: {model_path}. Letakkan best.pt di backend/models/best.pt"
        )

    try:
        from ultralytics import YOLO
        model = YOLO(str(model_path))
        return model
    except Exception as exc:
        raise RuntimeError(
            "Gagal load model. Pastikan best.pt adalah model Ultralytics YOLO yang valid. "
            f"Detail error: {exc}"
        )


def fetch_frame_from_esp32():
    """Ambil gambar JPG dari endpoint /capture ESP32."""
    response = requests.get(ESP32_CAPTURE_URL, timeout=8)
    response.raise_for_status()
    image_bytes = response.content
    image_np = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Gagal decode gambar dari ESP32. Cek endpoint /capture.")
    return frame, image_bytes


def encode_image_to_base64(frame):
    ok, buffer = cv2.imencode(".jpg", frame)
    if not ok:
        return None
    return base64.b64encode(buffer).decode("utf-8")


def write_log(payload):
    file_exists = LOG_FILE.exists()
    with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "status",
                "topi_detected",
                "dasi_detected",
                "topi_confidence",
                "dasi_confidence",
                "total_objects",
            ],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": payload["timestamp"],
            "status": payload["status"],
            "topi_detected": payload["summary"]["topi"]["detected"],
            "dasi_detected": payload["summary"]["dasi"]["detected"],
            "topi_confidence": payload["summary"]["topi"]["confidence"],
            "dasi_confidence": payload["summary"]["dasi"]["confidence"],
            "total_objects": len(payload["detections"]),
        })


def save_detection(payload):
    """Simpan lokal dan antrekan pengiriman Google Sheets."""
    write_log(payload)
    payload["google_sheets_queued"] = google_sheets.queue(payload)


def parse_results(results):
    detections = []
    summary = {
        "topi": {"detected": False, "confidence": 0},
        "dasi": {"detected": False, "confidence": 0},
    }

    result = results[0]
    for box in result.boxes:
        class_id = int(box.cls[0].item())
        name = str(result.names[class_id])
        conf = float(box.conf[0].item())
        if conf < CONF_THRESHOLD:
            continue

        xmin, ymin, xmax, ymax = box.xyxy[0].tolist()

        item = {
            "class": name,
            "confidence": round(conf, 3),
            "xmin": int(xmin),
            "ymin": int(ymin),
            "xmax": int(xmax),
            "ymax": int(ymax),
        }
        detections.append(item)

        if name in summary and conf > summary[name]["confidence"]:
            summary[name] = {"detected": True, "confidence": round(conf, 3)}

    topi_ok = summary["topi"]["detected"]
    dasi_ok = summary["dasi"]["detected"]
    status = "Lengkap" if topi_ok and dasi_ok else "Tidak Lengkap"

    return detections, summary, status


@app.get("/")
def index():
    return jsonify({
        "app": "Backend Deteksi Topi dan Dasi",
        "esp32_capture_url": ESP32_CAPTURE_URL,
        "model_path": MODEL_PATH,
        "endpoints": ["/api/health", "/api/detect", "/api/log/download"],
    })


@app.get("/api/health")
def health():
    model_exists = (BASE_DIR / MODEL_PATH).exists()
    return jsonify({
        "ok": True,
        "model_exists": model_exists,
        "model_path": str(BASE_DIR / MODEL_PATH),
        "esp32_capture_url": ESP32_CAPTURE_URL,
        "required_classes": REQUIRED_CLASSES,
        "confidence_threshold": CONF_THRESHOLD,
        "google_sheets": {
            "status": google_sheets.configuration_status(),
            "log_interval_seconds": GOOGLE_LOG_INTERVAL_SECONDS,
        },
    })


@app.get("/api/detect")
def detect():
    started = time.time()
    try:
        frame, image_bytes = fetch_frame_from_esp32()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = datetime.now().strftime("capture_%Y%m%d_%H%M%S.jpg")
        capture_path = CAPTURE_DIR / filename
        capture_path.write_bytes(image_bytes)

        yolo = load_model()
        results = yolo.predict(frame, imgsz=IMG_SIZE, verbose=False)
        detections, summary, status = parse_results(results)

        annotated = results[0].plot()
        result_filename = f"result_{filename}"
        result_path = RESULT_DIR / result_filename
        cv2.imwrite(str(result_path), annotated)

        payload = {
            "success": True,
            "timestamp": timestamp,
            "status": status,
            "summary": summary,
            "detections": detections,
            "fps": round(1 / max(time.time() - started, 0.001), 2),
            "processing_time_seconds": round(time.time() - started, 3),
            "image_base64": encode_image_to_base64(annotated),
        }
        save_detection(payload)
        return jsonify(payload)
    except Exception as exc:
        return jsonify({
            "success": False,
            "error": str(exc),
            "hint": "Cek IP ESP32 di backend/config.py dan pastikan best.pt sudah ada di backend/models/.",
        }), 500


@app.post("/api/detect/upload")
def detect_uploaded_frame():
    """Run YOLO on a JPEG fetched by the browser from the ESP32.

    This is used when Windows allows the browser to reach the camera but blocks
    outgoing connections made by the Python backend process.
    """
    started = time.time()
    try:
        image_bytes = request.get_data()
        if not image_bytes:
            raise ValueError("Gambar dari kamera tidak diterima.")

        image_np = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Gambar dari kamera tidak dapat diproses.")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = datetime.now().strftime("capture_%Y%m%d_%H%M%S.jpg")
        (CAPTURE_DIR / filename).write_bytes(image_bytes)

        yolo = load_model()
        results = yolo.predict(frame, imgsz=IMG_SIZE, verbose=False)
        detections, summary, status = parse_results(results)

        annotated = results[0].plot()
        cv2.imwrite(str(RESULT_DIR / f"result_{filename}"), annotated)

        payload = {
            "success": True,
            "timestamp": timestamp,
            "status": status,
            "summary": summary,
            "detections": detections,
            "fps": round(1 / max(time.time() - started, 0.001), 2),
            "processing_time_seconds": round(time.time() - started, 3),
            "image_base64": encode_image_to_base64(annotated),
        }
        save_detection(payload)
        return jsonify(payload)
    except Exception as exc:
        return jsonify({
            "success": False,
            "error": str(exc),
            "hint": "Pastikan browser dapat membuka endpoint /capture ESP32.",
        }), 500


@app.get("/api/log/download")
def download_log():
    if not LOG_FILE.exists():
        return jsonify({"success": False, "error": "Belum ada log deteksi."}), 404
    return send_file(LOG_FILE, as_attachment=True, download_name="detection_log.csv")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
