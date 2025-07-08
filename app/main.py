import os
import io
import json
import secrets
import tempfile
import zipfile

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from app.api.sessions import router as sessions_router
from . import crud
from .local import LocalZKFileExchange
from .core.config import settings

app = FastAPI(title="Zero-Knowledge File Exchange Gateway")
templates = Jinja2Templates(directory="app/templates")
app.include_router(sessions_router)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = os.path.join(tmpdir, file.filename)
        with open(tmp_path, "wb") as f:
            f.write(await file.read())

        engine = LocalZKFileExchange(settings.STORAGE_DIR)
        encrypted, root, _ = engine.encrypt_and_chunk(tmp_path)
        proof = engine.generate_zk_proof(root, {})

    nonce = secrets.token_hex(8)
    sid = crud.create_session(file.filename, {"nonce": nonce})
    for c in encrypted:
        crud.upload_chunk(sid, c["index"], c["ciphertext"], c["nonce"], c["tag"])
    crud.upload_proof(sid, root.hex(), proof.hex())

    share_url = f"/share/{sid}"
    return templates.TemplateResponse(
        "success.html",
        {"request": request, "session_id": sid, "share_url": share_url, "nonce": nonce},
    )


@app.get("/share/{session_id}")
def share_page(request: Request, session_id: str):
    return templates.TemplateResponse(
        "share.html", {"request": request, "session_id": session_id, "error": False}
    )


@app.post("/share/{session_id}")
def submit_nonce(request: Request, session_id: str, nonce: str = Form(...)):
    meta_path = os.path.join(settings.STORAGE_DIR, session_id, "metadata.json")
    try:
        with open(meta_path) as f:
            meta = json.load(f)
    except FileNotFoundError:
        return templates.TemplateResponse(
            "share.html",
            {
                "request": request,
                "session_id": session_id,
                "error": True,
                "message": "Session not found",
            },
        )

    if meta.get("metadata", {}).get("nonce") != nonce:
        return templates.TemplateResponse(
            "share.html",
            {
                "request": request,
                "session_id": session_id,
                "error": True,
                "message": "Invalid nonce",
            },
        )

    proof = crud.get_metadata(session_id)
    chunk_count = proof["chunk_count"]
    return templates.TemplateResponse(
        "download.html",
        {
            "request": request,
            "session_id": session_id,
            "nonce": nonce,
            "chunks": list(range(chunk_count)),
        },
    )


@app.get("/download/{session_id}")
def download_zip(session_id: str, nonce: str):
    meta_path = os.path.join(settings.STORAGE_DIR, session_id, "metadata.json")
    with open(meta_path) as f:
        meta = json.load(f)
    if meta.get("metadata", {}).get("nonce") != nonce:
        return HTMLResponse("Invalid nonce", status_code=403)

    proof = crud.get_metadata(session_id)
    chunk_count = proof["chunk_count"]
    path = os.path.join(settings.STORAGE_DIR, session_id)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.write(os.path.join(path, "proof.json"), arcname="proof.json")
        zf.write(os.path.join(path, "metadata.json"), arcname="metadata.json")
        for i in range(chunk_count):
            fname = os.path.join(path, f"chunk_{i:05d}.bin")
            zf.write(fname, arcname=f"chunk_{i:05d}.bin")
    buf.seek(0)
    headers = {"Content-Disposition": f'attachment; filename="{meta["filename"]}.zip"'}
    return StreamingResponse(buf, media_type="application/zip", headers=headers)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
