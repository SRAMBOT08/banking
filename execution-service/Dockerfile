FROM python:3.12-slim
WORKDIR /app
COPY execution-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY execution-service/app ./app
COPY execution-service/README.md execution-service/SERVICE.md ./
COPY shared ./shared
EXPOSE 8700
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8700"]
