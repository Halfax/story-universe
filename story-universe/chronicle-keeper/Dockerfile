# Multi-stage Dockerfile for Chronicle Keeper (smaller runtime image)
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt ./
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .

# initialize DB
RUN python src/db/init_db.py || true

COPY start_with_clock.sh /app/start_with_clock.sh
RUN chmod +x /app/start_with_clock.sh

EXPOSE 8001 5555

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
	CMD curl -f http://localhost:8001/ping || exit 1

ENTRYPOINT ["/app/start_with_clock.sh"]
