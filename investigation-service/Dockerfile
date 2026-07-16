FROM python:3.12-slim
WORKDIR /app
COPY investigation-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY investigation-service/app ./app
COPY investigation-service/README.md investigation-service/SERVICE.md ./
COPY shared ./shared
RUN pip install --no-cache-dir ./shared
EXPOSE 8500
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8500"]
