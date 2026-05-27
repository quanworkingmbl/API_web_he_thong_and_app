#!/bin/bash
set -e

# NOTE: alembic upgrade head đã được chạy trong Cloud Build Step 3.
# KHÔNG chạy lại ở đây để tránh lỗi kết nối DB khi container cold start.

echo "=== Starting Gunicorn ==="
exec gunicorn app.main:app \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
