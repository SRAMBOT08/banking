FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY case-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY case-service/ .
COPY shared/ ./shared/
RUN addgroup --system app && adduser --system --ingroup app app && chown -R app:app /app
USER app
EXPOSE 8950
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8950/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8950"]
