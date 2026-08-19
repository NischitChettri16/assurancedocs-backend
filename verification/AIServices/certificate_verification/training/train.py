
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="dataset.yaml",
    epochs=150,
    imgsz=640,
    batch=4,
    workers=0,
    device="cpu",
    patience=30,
    project="runs/detect",
    name="certificate_detector_v2"
)

print("Training Complete!")