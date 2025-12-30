#!/bin/bash
set -e

echo "🔥 Starting FastAPI server..."

exec gunicorn main:app \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --workers 1 \
  --timeout 120