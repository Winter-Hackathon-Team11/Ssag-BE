RUN mkdir -p /app/weights && \
    curl -L \
      -o /weights/detect_trash.pt \
      https://raw.githubusercontent.com/jeremy-rico/litter-detection/master/runs/detect/train/yolov8s_100epochs/weights/best.pt