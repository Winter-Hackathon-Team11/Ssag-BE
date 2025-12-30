# utils/model_loader.py
from pathlib import Path
import urllib.request

MODEL_URL = "https://github.com/jeremy-rico/litter-detection/raw/master/runs/detect/train/yolov8s_100epochs/weights/best.pt"
MODEL_PATH = Path("weights/detect_trash.pt")

def ensure_model_exists():
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not MODEL_PATH.exists():
        print("📥 Downloading YOLO model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("✅ Model downloaded")