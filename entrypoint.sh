#!/bin/bash
set -e

# NOTE: alembic upgrade head Ä‘Ã£ Ä‘Æ°á»£c cháº¡y trong Cloud Build Step 3.
# KHÃ”NG cháº¡y láº¡i á»Ÿ Ä‘Ã¢y Ä‘á»ƒ trÃ¡nh lá»—i káº¿t ná»‘i DB khi container cold start.

echo "=== Starting Gunicorn ==="
exec gunicorn app.main:app \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --graceful-timeout 30 \
    --keepalive 5 \
    --access-logfile - \
    --error-logfile -
