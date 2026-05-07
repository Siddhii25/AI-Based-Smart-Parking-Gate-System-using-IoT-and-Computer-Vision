"""
utils/sensor_reader.py
Reads ultrasonic distance values from Arduino over serial in a background thread.
"""

import threading
import re


class SensorReader:
    """Continuously reads distance values sent by Arduino over serial."""

    def __init__(self, serial_conn):
        self._ser   = serial_conn
        self._lock  = threading.Lock()
        self._dist  = None

    @property
    def latest_distance(self):
        with self._lock:
            return self._dist

    def read_loop(self):
        """Blocking loop — run in a daemon thread."""
        while True:
            try:
                raw = self._ser.readline().decode("utf-8", errors="ignore").strip()
                # Arduino sends lines like "DIST:14" or just "14"
                match = re.search(r"(\d+(?:\.\d+)?)", raw)
                if match:
                    with self._lock:
                        self._dist = float(match.group(1))
            except Exception:
                pass  # Serial errors are non-fatal; keep reading
