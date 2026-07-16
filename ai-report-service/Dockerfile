FROM python:3.12-slim
WORKDIR /app
COPY ai-report-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ai-report-service/app ./app
COPY shared ./shared
RUN useradd --create-home app && chown -R app:app /app
USER app
EXPOSE 8960
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8960/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8960"]
