FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY docker/scripts/register_consul.py /scripts/register_consul.py
COPY services/web-ui/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/web-ui/ .
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
