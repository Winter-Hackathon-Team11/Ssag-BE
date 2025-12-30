from pathlib import Path
from ultralytics import YOLO
from PIL import Image

from threading import Lock

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "weights" / "detect_trash.pt"

_model = None
_lock = Lock()

def get_model():
    global _model
    if _model is None:
        with _lock:  # 동시 요청 방지
            if _model is None:
                print("🧠 YOLO model loading...")
                _model = YOLO("weights/detect_trash.pt")
                print("✅ YOLO model loaded")
    return _model


def run_yolo(image_path: str, conf: float = 0.25):
    model = get_model()
    results = model.predict(
        source=image_path,
        conf=conf,
        imgsz=640,
        verbose=False,
    )[0]

    names = results.names  # {class_id: class_name}

    detections = []
    for box in results.boxes:
        cls_id = int(box.cls[0])
        detections.append({
            "class_id": cls_id,
            "class_name": names[cls_id],
            "confidence": float(box.conf[0]),
            "bbox": list(map(float, box.xyxy[0])),
        })

    return detections


def summarize_detections(detections):
    summary = {}
    for d in detections:
        name = d["class_name"]
        summary[name] = summary.get(name, 0) + 1
    return summary


def save_annotated_image(
    image_path: str,
    output_path: str,
    conf: float = 0.25,
):
    model = get_model()
    results = model.predict(
        source=image_path,
        conf=conf,
        imgsz=640,
        verbose=False,
        save=False,
    )[0]

    annotated = results.plot()  # numpy array with boxes
    Image.fromarray(annotated).save(output_path)