"""
utils/gate_controller.py
Handles gate open/close logic with edge-trigger prevention.
"""

import time
import threading


class GateController:
    """
    Issues OPEN / CLOSE serial commands to Arduino.
    Edge-trigger logic: the gate will only open once per continuous
    vehicle-presence event (rising edge detection).
    """

    OPEN_CMD  = b"O"
    CLOSE_CMD = b"C"

    def __init__(self, serial_conn, open_delay: int = 5):
        self._ser        = serial_conn
        self._open_delay = open_delay
        self._gate_open  = False
        self._triggered  = False   # edge-trigger flag
        self._lock       = threading.Lock()

    def evaluate(self, slots_available: bool, vehicle_present: bool):
        with self._lock:
            if slots_available and vehicle_present:
                if not self._triggered:
                    self._trigger_open()
                    self._triggered = True
            else:
                # Reset trigger when vehicle leaves
                if not vehicle_present:
                    self._triggered = False

                if slots_available is False and vehicle_present:
                    print("[ACTION] Parking Full. Gate remains CLOSED.")

    def _trigger_open(self):
        print("[DECISION] Slots Available: Yes | Vehicle Present: Yes")
        print("[ACTION] Sending OPEN command to Arduino...")
        self._ser.write(self.OPEN_CMD)
        print(f"[ARDUINO] Gate OPENED. Waiting {self._open_delay} seconds...")

        t = threading.Thread(target=self._close_after_delay, daemon=True)
        t.start()

    def _close_after_delay(self):
        time.sleep(self._open_delay)
        with self._lock:
            print("[ACTION] Sending CLOSE command to Arduino...")
            self._ser.write(self.CLOSE_CMD)
            print("[ARDUINO] Gate CLOSED.")
            self._gate_open = False
