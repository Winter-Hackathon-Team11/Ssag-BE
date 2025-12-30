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

# app source
COPY . .

RUN mkdir -p /app/.cache /app/weights && chmod -R 777 /app

EXPOSE 8000

CMD ["bash", "entrypoint.sh"]