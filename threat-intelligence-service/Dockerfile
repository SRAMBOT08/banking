FROM python:3.12-slim
WORKDIR /app
COPY threat-intelligence-service/requirements.txt ./requirements.txt
RUN apt-get update && apt-get install -y gcc librdkafka-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt
COPY threat-intelligence-service/app ./app
COPY threat-intelligence-service/knowledge_registry ./knowledge_registry
COPY threat-intelligence-service/patterns ./patterns
COPY shared ./shared
RUN pip install --no-cache-dir ./shared
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8400"]
