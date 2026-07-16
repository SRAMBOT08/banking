FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends librdkafka-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY event-simulator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY event-simulator/ .
RUN addgroup --system app && adduser --system --ingroup app app && chown -R app:app /app
USER app
EXPOSE 8900
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8900/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8900"]
