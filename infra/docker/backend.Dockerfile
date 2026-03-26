FROM python:3.11-slim

WORKDIR /app

COPY apps/backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY apps/backend /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
