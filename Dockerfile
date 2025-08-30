# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Kalau ada lib yang butuh build tools, aktifkan baris berikut:
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# App kamu kelihatannya Flask + Procfile, jadi kita expose 5000
ENV PORT=5000
EXPOSE 5000

# Jalankan langsung app.py biar aman (kalau nanti mau, ganti ke gunicorn app:app)
CMD ["python", "app.py"]
