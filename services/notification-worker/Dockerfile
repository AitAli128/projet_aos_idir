FROM python:3.11-slim
WORKDIR /app
COPY services/notification-worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/notification-worker/worker.py .
CMD ["python", "-u", "worker.py"]
