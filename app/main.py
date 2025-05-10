from fastapi import FastAPI
from app.api.sessions import router as sessions_router

app = FastAPI(title="ZK File Exchange Gateway", version="0.1.0")

app.include_router(sessions_router, prefix="/v1/sessions", tags=["sessions"])

@app.get("/health")
def health():
    return {"status": "ok"}