FROM python:3.11-slim

WORKDIR /app

COPY apps/backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY apps/backend /app/backend
COPY apps/worker /app/worker

WORKDIR /app/worker

CMD ["python", "main.py"]
