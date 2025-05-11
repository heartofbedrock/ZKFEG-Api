import os
import uvicorn
from fastapi import FastAPI
from app.api.sessions import router as sessions_router

app = FastAPI(title="Zero-Knowledge File Exchange Gateway")
app.include_router(sessions_router)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
