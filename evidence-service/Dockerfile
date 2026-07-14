FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc librdkafka-dev git python3-setuptools && rm -rf /var/lib/apt/lists/*
COPY evidence-service/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip wheel --wheel-dir=/wheels -r /app/requirements.txt

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends librdkafka-dev python3-setuptools && rm -rf /var/lib/apt/lists/*
COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt /app/requirements.txt
RUN pip install --no-index --find-links=/wheels -r /app/requirements.txt

# Add shared code directly to image and expose on PYTHONPATH to avoid building wheels
COPY shared/ /app/shared
ENV PYTHONPATH=/app/shared:${PYTHONPATH}

COPY evidence-service/ /app
RUN chown -R app:app /app
USER app
EXPOSE 8200
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD python -c "import urllib.request, sys; \
resp=urllib.request.urlopen('http://127.0.0.1:8200/health'); \
sys.exit(0 if resp.status==200 else 1)" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8200"]
