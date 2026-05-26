# ============================================================
# Stage 1: Builder — cài dependencies
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Cài build tools cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy và cài requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# ============================================================
# Stage 2: Runtime — image nhỏ gọn để chạy thực tế
# ============================================================
FROM python:3.11-slim AS runtime

WORKDIR /app

# Cài libpq để psycopg2 chạy được
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies từ builder
COPY --from=builder /install /usr/local

# Copy toàn bộ source code
COPY . .

# Cloud Run yêu cầu lắng nghe trên cổng $PORT (mặc định 8080)
ENV PORT=8080

# Tạo user không phải root + cấp quyền
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Chạy Gunicorn trực tiếp (tránh vấn đề CRLF/BOM của shell script trên Windows)
CMD ["sh", "-c", "exec gunicorn app.main:app --bind 0.0.0.0:${PORT:-8080} --workers 1 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --graceful-timeout 30 --keepalive 5 --access-logfile - --error-logfile -"]
