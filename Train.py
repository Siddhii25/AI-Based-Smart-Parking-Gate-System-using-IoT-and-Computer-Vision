"""
model/train.py
Trains a YOLOv8n model on the custom parking dataset.
Run this script on Kaggle or any machine with a GPU.

Usage:
    python model/train.py --data data.yaml --epochs 80

dataset/
├── images/
│   ├── train/
│   └── val/
└── labels/
    ├── train/
    └── val/
"""

import argparse
from ultralytics import YOLO


def parse_args():
    p = argparse.ArgumentParser(description="Train YOLOv8 parking model")
    p.add_argument("--data",   default="model/data.yaml", help="Path to data.yaml")
    p.add_argument("--epochs", type=int, default=80)
    p.add_argument("--imgsz",  type=int, default=640)
    p.add_argument("--batch",  type=int, default=16)
    p.add_argument("--name",   default="parking_run")
    return p.parse_args()


def main():
    args = parse_args()

    model = YOLO("yolov8n.pt")   # start from pretrained nano weights

    results = model.train(
        data    = args.data,
        epochs  = args.epochs,
        imgsz   = args.imgsz,
        batch   = args.batch,
        name    = args.name,
        optimizer = "AdamW",
        augment   = True,
        mosaic    = 1.0,
        fliplr    = 0.5,
        flipud    = 0.1,
        scale     = 0.5,
        hsv_h     = 0.015,
        hsv_s     = 0.7,
        hsv_v     = 0.4,
        project   = "runs/train",
        exist_ok  = True,
    )

    print("\n[TRAIN] Final metrics:")
    print(f"  mAP50    : {results.results_dict.get('metrics/mAP50(B)', 'N/A'):.4f}")
    print(f"  mAP50-95 : {results.results_dict.get('metrics/mAP50-95(B)', 'N/A'):.4f}")
    print(f"  Precision: {results.results_dict.get('metrics/precision(B)', 'N/A'):.4f}")
    print(f"  Recall   : {results.results_dict.get('metrics/recall(B)', 'N/A'):.4f}")


if __name__ == "__main__":
    main()
