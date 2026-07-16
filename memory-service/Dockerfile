FROM python:3.13-slim
WORKDIR /app
COPY memory-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY memory-service/app ./app
COPY shared ./shared
RUN pip install --no-cache-dir ./shared
EXPOSE 8020
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8020"]
