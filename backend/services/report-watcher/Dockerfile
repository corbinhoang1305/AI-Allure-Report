FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/services/report-watcher/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code
COPY backend/shared /app/shared

# Copy service code
COPY backend/services/report-watcher /app/report-watcher

WORKDIR /app/report-watcher

EXPOSE 8005

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]

