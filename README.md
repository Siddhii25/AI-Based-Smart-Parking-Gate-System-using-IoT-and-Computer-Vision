# AI-Based-Smart-Parking-Gate-System-using-IoT-and-Computer-Vision

> **Project-Based Learning Report**  
> Subject: IOT FOR AI LAB [BCS-DS-684] · Academic Year 2025–2026  
> Manav Rachna International Institute of Research and Studies  
> Under the guidance of **Mrs. Nidhi**, Dept. of Computer Science & Engineering

---

## 👥 Team Members

| Name | Enrollment No. |
|------|---------------|
| Mohit Jain | 1/23/SET/BCS/485 |
| Siddhi Vats | 1/23/SET/BCS/471 |
| Raunak Pratap Singh | 1/23/SET/BCS/467 |

---

## 📌 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Hardware Components](#-hardware-components)
- [Model Training](#-model-training)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Running the System](#-running-the-system)
- [Results](#-results)
- [Limitations & Future Work](#-limitations--future-work)
- [References](#-references)

---

## 🧠 Overview

Urban parking congestion is a growing challenge in smart cities. This project presents an **AI-powered, IoT-integrated Smart Parking Gate System** that automates gate control based on real-time parking slot availability.

**How it works:**
1. A **camera** streams live footage of the parking area.
2. A custom-trained **YOLOv8n model** detects and classifies each slot as `empty` or `occupied`.
3. An **ultrasonic sensor (HC-SR04)** detects whether a vehicle is waiting at the gate.
4. A **Python decision engine** combines both inputs to send `OPEN` or `CLOSE` commands.
5. An **Arduino UNO** receives serial commands and drives a **servo motor** to physically operate the gate.

```
Camera ──► YOLOv8 Inference ──► Python Decision Logic ──► Arduino UNO ──► Servo (Gate)
                                          ▲
                              HC-SR04 Ultrasonic Sensor
```

---

## 🏗 System Architecture

The system is divided into three layers:

| Layer | Components | Role |
|-------|-----------|------|
| **Sensing** | IP Webcam, HC-SR04 | Raw data acquisition |
| **Processing** | Python + YOLOv8 + OpenCV | Inference & decision logic |
| **Actuation** | Arduino UNO + Servo Motor | Physical gate control |

### Data Flow

```
1. IP Webcam → live frames → Python (OpenCV)
2. Each frame resized to 640×640 → YOLOv8n inference
3. Bounding boxes → count empty / occupied slots
4. Arduino → serial → distance reading (cm)
5. If (empty > 0) AND (distance < 20 cm) → send 'O' to Arduino
6. Arduino rotates servo to 90° (OPEN)
7. After 5 seconds → send 'C' → servo returns to 0° (CLOSED)
8. Edge-trigger flag prevents repeated activation for same vehicle
```

---

## 🛠 Technology Stack

| Component | Technology |
|-----------|-----------|
| Object Detection Model | YOLOv8n (custom-trained) |
| Training Framework | Ultralytics YOLOv8 |
| Training Platform | Kaggle Notebook (Tesla P100 GPU) |
| Programming Language | Python 3 |
| Computer Vision | OpenCV |
| Microcontroller | Arduino UNO |
| Gate Mechanism | Servo Motor |
| Distance Sensing | HC-SR04 Ultrasonic Sensor |
| Camera Input | IP Webcam (mobile phone) |
| Serial Communication | PySerial |

---

## 🔌 Hardware Components

| Component | Quantity | Notes |
|-----------|----------|-------|
| Arduino UNO | 1 | Microcontroller |
| HC-SR04 Ultrasonic Sensor | 1 | Trig → Pin 9, Echo → Pin 10 |
| Servo Motor | 1 | Signal → Pin 6 |
| Mobile Phone | 1 | Running **IP Webcam** app |
| USB Cable | 1 | Arduino ↔ PC (serial + power) |
| Jumper Wires | Several | Connections |
| Breadboard | 1 | Prototyping |

### Wiring Diagram

```
Arduino UNO
├── Pin 9  ──► HC-SR04 TRIG
├── Pin 10 ──► HC-SR04 ECHO
├── Pin 6  ──► Servo Signal
├── 5V     ──► HC-SR04 VCC, Servo VCC
└── GND    ──► HC-SR04 GND, Servo GND
```

---

## 🤖 Model Training

### Base Model
**YOLOv8n (Nano)** was selected for its balance of speed and accuracy, making it suitable for real-time CPU/GPU inference.

### Dataset
- Custom parking lot images captured under **varying lighting and angles**
- Two classes: `empty` (green bbox) and `occupied` (red bbox)
- **80% train / 20% validation** split
- Augmentations: mosaic, horizontal/vertical flip, random scale, HSV shifts

### Training Configuration

| Parameter | Value |
|-----------|-------|
| Base Model | YOLOv8n (pretrained) |
| Classes | 2 (empty, occupied) |
| Epochs | 80 |
| Image Size | 640 × 640 |
| Batch Size | 16 |
| Optimizer | AdamW (auto) |
| GPU | Tesla P100 (Kaggle) |

### Results

| Metric | Epoch 1 | Epoch 80 |
|--------|---------|---------|
| mAP50 | ~0.02 | **~0.85** |
| mAP50-95 | ~0.01 | **~0.70** |
| Precision | Low | **>0.80** |
| Recall | Low | **>0.85** |

> The model improved **~42×** from initial to final mAP50 — a clear indicator of successful training and convergence.

---

## 📁 Project Structure

```
smart-parking-system/
│
├── main.py                      # Main application entry point
│
├── arduino/
│   └── smart_parking_gate.ino   # Arduino firmware (sensor + servo control)
│
├── model/
│   ├── train.py                 # YOLOv8 training script
│   ├── data.yaml                # Dataset configuration
│   └── parking_yolov8n.pt       # Trained weights (add your own — see below)
│
├── utils/
│   ├── __init__.py
│   ├── sensor_reader.py         # Threaded serial distance reader
│   ├── gate_controller.py       # Gate open/close + edge-trigger logic
│   └── frame_smoother.py        # Temporal smoothing of slot counts
│
├── docs/
│   └── project_report.pdf       # Full PBL report
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.8+
- Arduino IDE
- IP Webcam app (Android/iOS) or a webcam
- Arduino UNO + components (see [Hardware](#-hardware-components))

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/smart-parking-system.git
cd smart-parking-system
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Flash Arduino firmware

1. Open `arduino/smart_parking_gate.ino` in **Arduino IDE**
2. Select **Board: Arduino UNO** and the correct **COM port**
3. Click **Upload**

### 4. Add model weights

Download or copy your trained weights to:
```
model/parking_yolov8n.pt
```

To train from scratch:
```bash
# Prepare your dataset following YOLO format, then:
python model/train.py --data model/data.yaml --epochs 80
```

### 5. Configure `main.py`

Edit the constants at the top of `main.py`:

```python
MODEL_PATH  = "model/parking_yolov8n.pt"
CAMERA_URL  = "http://<your-phone-ip>:8080/video"   # IP Webcam URL
SERIAL_PORT = "COM4"      # Windows: COM4, Linux/Mac: /dev/ttyUSB0
```

---

## ▶️ Running the System

```bash
python main.py
```

**Expected console output:**

```
[INFO] Loading YOLOv8 model... Done.
[INFO] Serial port COM4 opened successfully.
[INFO] Camera stream connected: http://192.168.1.5:8080/video

--- Live Parking Monitor Started (press Q to quit) ---

[FRAME 001] Empty Slots: 4 | Occupied Slots: 2
[SENSOR] Distance = 85 cm | Vehicle Detected: No

[FRAME 047] Empty Slots: 3 | Occupied Slots: 3
[SENSOR] Distance = 14 cm | Vehicle Detected: Yes
[DECISION] Slots Available: Yes | Vehicle Present: Yes
[ACTION] Sending OPEN command to Arduino...
[ARDUINO] Gate OPENED. Waiting 5 seconds...
[ACTION] Sending CLOSE command to Arduino...
[ARDUINO] Gate CLOSED.

[FRAME 089] Empty Slots: 0 | Occupied Slots: 6
[SENSOR] Distance = 11 cm | Vehicle Detected: Yes
[ACTION] Parking Full. Gate remains CLOSED.
```

Press **Q** in the OpenCV window to quit.

---

## 📊 Results

| Scenario | System Behaviour |
|----------|-----------------|
| Vehicle present + slots available | ✅ Gate opens for 5 seconds, then closes |
| Vehicle present + parking full | ❌ Gate stays closed |
| No vehicle detected | ⏸ Gate stays closed regardless of slots |
| Vehicle stays stationary | 🔒 Edge-trigger prevents repeated opening |

### Challenges & Solutions

| Challenge | Solution Applied |
|-----------|-----------------|
| IP Webcam lag | Buffered frames + reduced stream resolution |
| Ultrasonic sensor noise | Moving average filter on distance readings |
| YOLO frame-to-frame jitter | Temporal smoothing over 5-frame window |
| Repeated gate triggering | Boolean edge-trigger state variable |

---

## 🔮 Limitations & Future Work

### Current Limitations
- Single parking zone (one camera view)
- Outdoor glare and night conditions degrade camera performance
- No vehicle identification or number plate recognition
- Ultrasonic sensor has a narrow detection cone (~15°)

### Planned Enhancements
- [ ] **ANPR (Number Plate Recognition)** — OCR-based vehicle authorisation
- [ ] **Mobile App** — Real-time slot availability for approaching drivers
- [ ] **Multi-Zone Support** — Multiple cameras + centralised backend
- [ ] **Night Vision** — Infrared/low-light camera support
- [ ] **Cloud Dashboard** — MQTT + AWS IoT / Firebase for remote monitoring
- [ ] **Automated Billing** — Entry/exit timestamping and fare calculation
- [ ] **Larger Dataset** — Improved generalisation across diverse environments

---



<p align="center">Made with ❤️ by Mohit, Siddhi & Raunak · MRIIRS · 2025–2026</p>
