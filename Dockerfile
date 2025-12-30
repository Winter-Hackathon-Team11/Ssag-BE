FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TORCH_HOME=/app/.cache/torch
ENV YOLO_CONFIG_DIR=/app/.cache/ultralytics

# system deps (opencv용)
RUN apt-get update && apt-get install -y \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# python deps
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# weights 디렉토리 생성
RUN mkdir -p weights

# YOLO 모델 다운로드 (빌드 타임)
RUN curl -L \
  https://raw.githubusercontent.com/jeremy-rico/litter-detection/master/runs/detect/train/yolov8s_100epochs/weights/best.pt \
  -o weights/detect_trash.pt

# app source
COPY . .

RUN mkdir -p /app/.cache /app/weights && chmod -R 777 /app

EXPOSE 8000

CMD ["bash", "entrypoint.sh"]