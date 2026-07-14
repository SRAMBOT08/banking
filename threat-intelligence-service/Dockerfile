FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN apt-get update && apt-get install -y gcc librdkafka-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt
# install shared package for models
RUN pip install --no-cache-dir ../shared
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8400"]
