from fastapi import FastAPI
from app.core.logger import get_logger

logger = get_logger("main")
app = FastAPI(title="evidence-service")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "evidence-service"}
