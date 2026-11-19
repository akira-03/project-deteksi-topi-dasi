import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests


LOGGER = logging.getLogger(__name__)


class GoogleSheetsLogger:
    """Kirim hasil deteksi ke URL Google Apps Script tanpa menghambat kamera."""

    def __init__(self, apps_script_url, min_interval=10):
        self.apps_script_url = apps_script_url.strip()
        self.min_interval = max(float(min_interval), 0)
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="sheets")
        self._lock = threading.Lock()
        self._last_queued_at = 0.0

    @property
    def enabled(self):
        return self.apps_script_url.startswith("https://script.google.com/macros/s/")

    def configuration_status(self):
        if not self.apps_script_url:
            return "belum_dikonfigurasi"
        if not self.enabled:
            return "url_apps_script_tidak_valid"
        return "aktif"

    def queue(self, payload):
        if not self.enabled:
            return False

        now = time.monotonic()
        with self._lock:
            if now - self._last_queued_at < self.min_interval:
                return False
            self._last_queued_at = now

        data = {
            "timestamp": payload["timestamp"],
            "status": payload["status"],
            "topi_detected": payload["summary"]["topi"]["detected"],
            "dasi_detected": payload["summary"]["dasi"]["detected"],
            "topi_confidence": payload["summary"]["topi"]["confidence"],
            "dasi_confidence": payload["summary"]["dasi"]["confidence"],
            "total_objects": len(payload["detections"]),
        }
        self._executor.submit(self._send, data)
        return True

    def _send(self, data):
        try:
            response = requests.post(self.apps_script_url, json=data, timeout=10)
            response.raise_for_status()
        except Exception:
            LOGGER.exception("Gagal mengirim hasil deteksi ke Google Apps Script")
