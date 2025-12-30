#!/bin/bash
set -e

MODEL_PATH="weights/detect_trash.pt"
MODEL_URL="https://raw.githubusercontent.com/jeremy-rico/litter-detection/master/runs/detect/train/yolov8s_100epochs/weights/best.pt"

echo "🚀 Container starting..."

if [ ! -f "$MODEL_PATH" ]; then
  echo "⬇️ YOLO model not found. Downloading..."
  curl -L --progress-bar "$MODEL_URL" -o "$MODEL_PATH"
  echo "✅ Model downloaded"
else
  echo "✅ Model already exists"
fi

echo "🔥 Starting FastAPI server..."

exec gunicorn main:app \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --workers 1 \
  --timeout 120