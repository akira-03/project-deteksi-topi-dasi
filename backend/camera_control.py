import requests
from flask import Blueprint, jsonify, request

from config import DEFAULT_CAMERA_RESOLUTION, ESP32_BASE_URL

camera_bp = Blueprint("camera", __name__)

CAMERA_RESOLUTIONS = [
    {"name": "QQVGA", "label": "QQVGA 160x120", "width": 160, "height": 120, "value": 0},
    {"name": "QVGA", "label": "QVGA 320x240", "width": 320, "height": 240, "value": 5},
    {"name": "VGA", "label": "VGA 640x480", "width": 640, "height": 480, "value": 8},
    {"name": "SVGA", "label": "SVGA 800x600", "width": 800, "height": 600, "value": 9},
    {"name": "XGA", "label": "XGA 1024x768", "width": 1024, "height": 768, "value": 10},
    {"name": "SXGA", "label": "SXGA 1280x1024", "width": 1280, "height": 1024, "value": 12},
    {"name": "UXGA", "label": "UXGA 1600x1200", "width": 1600, "height": 1200, "value": 13},
]


def find_resolution(name):
    normalized = str(name or "").strip().upper()
    return next((item for item in CAMERA_RESOLUTIONS if item["name"] == normalized), None)


@camera_bp.get("/api/camera/resolutions")
def get_camera_resolutions():
    return jsonify({
        "success": True,
        "default": DEFAULT_CAMERA_RESOLUTION,
        "resolutions": CAMERA_RESOLUTIONS,
    })


@camera_bp.post("/api/camera/resolution")
def set_camera_resolution():
    payload = request.get_json(silent=True) or {}
    resolution = find_resolution(payload.get("resolution"))

    if resolution is None:
        return jsonify({
            "success": False,
            "error": "Resolusi tidak tersedia. Pilih salah satu: QQVGA, QVGA, VGA, SVGA, XGA, SXGA, UXGA.",
        }), 400

    control_url = f"{ESP32_BASE_URL}/control"
    try:
        response = requests.get(
            control_url,
            params={"var": "framesize", "val": resolution["value"]},
            timeout=8,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return jsonify({
            "success": False,
            "error": f"ESP32 tidak bisa dihubungi atau menolak perubahan resolusi di {response.url if 'response' in locals() else control_url}: {exc}",
        }), 500

    return jsonify({
        "success": True,
        "resolution": resolution["name"],
        "value": resolution["value"],
        "message": f"Resolusi kamera berhasil diubah ke {resolution['name']}",
    })
