from fastapi import FastAPI

app = FastAPI(title="SentinelIQ Gateway")

@app.get("/health")
async def health():
    return {"status": "ok"}
