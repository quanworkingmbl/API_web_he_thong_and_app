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

# Tạo user không phải root (best practice bảo mật)
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# Cấp quyền execute cho entrypoint
RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8080

# Dùng entrypoint.sh để start (alembic đã chạy trong Cloud Build Step 3)
CMD ["/app/entrypoint.sh"]
