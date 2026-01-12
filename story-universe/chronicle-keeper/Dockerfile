# Dockerfile for Chronicle Keeper (Raspberry Pi 5)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python src/db/init_db.py
COPY start_with_clock.sh /app/start_with_clock.sh
RUN chmod +x /app/start_with_clock.sh
ENTRYPOINT ["/app/start_with_clock.sh"]
