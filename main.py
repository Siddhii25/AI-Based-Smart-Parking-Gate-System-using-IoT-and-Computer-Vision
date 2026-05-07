

import cv2
import serial
import time
import threading
from ultralytics import YOLO
from utils.sensor_reader import SensorReader
from utils.gate_controller import GateController
from utils.frame_smoother import FrameSmoother

# ─── Configuration ────────────────────────────────────────────────────────────
MODEL_PATH       = "model/parking_yolov8n.pt"
CAMERA_URL       = "http://192.168.1.5:8080/video"   # IP Webcam URL
SERIAL_PORT      = "COM4"                             # Arduino serial port
BAUD_RATE        = 9600
DISTANCE_THRESH  = 20    # cm — vehicle considered present below this value
GATE_OPEN_DELAY  = 5     # seconds gate stays open
SMOOTH_WINDOW    = 5     # frames for temporal smoothing of slot counts
# ──────────────────────────────────────────────────────────────────────────────


def main():
    print("[INFO] Loading YOLOv8 model...", end=" ")
    model = YOLO(MODEL_PATH)
    print("Done.")

    print(f"[INFO] Opening serial port {SERIAL_PORT}...")
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)   # allow Arduino to reset
    print(f"[INFO] Serial port {SERIAL_PORT} opened successfully.")

    print(f"[INFO] Connecting to camera: {CAMERA_URL}")
    cap = cv2.VideoCapture(CAMERA_URL)
    if not cap.isOpened():
        raise RuntimeError("Could not open camera stream. Check IP Webcam URL.")
    print(f"[INFO] Camera stream connected: {CAMERA_URL}")

    sensor   = SensorReader(ser)
    gate     = GateController(ser, open_delay=GATE_OPEN_DELAY)
    smoother = FrameSmoother(window=SMOOTH_WINDOW)

    sensor_thread = threading.Thread(target=sensor.read_loop, daemon=True)
    sensor_thread.start()

    frame_id = 0
    print("\n--- Live Parking Monitor Started (press Q to quit) ---\n")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[WARN] Frame grab failed, retrying...")
                continue

            frame_id += 1
            resized = cv2.resize(frame, (640, 640))
            results  = model(resized, verbose=False)[0]

            empty_count    = 0
            occupied_count = 0

            for box in results.boxes:
                cls  = int(box.cls[0])
                conf = float(box.conf[0])
                label = model.names[cls]
                color = (0, 255, 0) if label == "empty" else (0, 0, 255)

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(resized, (x1, y1), (x2, y2), color, 2)
                cv2.putText(resized, f"{label} {conf:.2f}",
                            (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX,
                            0.45, color, 1)

                if label == "empty":
                    empty_count += 1
                else:
                    occupied_count += 1

            # Temporal smoothing
            smoothed_empty = smoother.update(empty_count)

            # Sensor data
            distance        = sensor.latest_distance
            vehicle_present = distance is not None and distance < DISTANCE_THRESH

            print(f"[FRAME {frame_id:04d}] Empty Slots: {smoothed_empty} | "
                  f"Occupied Slots: {occupied_count}")
            print(f"[SENSOR] Distance = {distance} cm | "
                  f"Vehicle Detected: {'Yes' if vehicle_present else 'No'}")

            # Decision logic
            slots_available = smoothed_empty > 0
            gate.evaluate(slots_available, vehicle_present)

            # Overlay HUD
            hud = f"Empty: {smoothed_empty}  Occupied: {occupied_count}"
            cv2.putText(resized, hud, (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            cv2.imshow("Smart Parking System", resized)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        ser.close()
        print("\n[INFO] System shut down cleanly.")


if __name__ == "__main__":
    main()
