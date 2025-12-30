RUN mkdir -p /weights && \
    curl -L \
      -o /weights/detect_trash.pt \
      https://raw.githubusercontent.com/jeremy-rico/litter-detection/master/runs/detect/train/yolov8s_100epochs/weights/best.pt

RUN pip install --no-cache-dir -r requirements.txt