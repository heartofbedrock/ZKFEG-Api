import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
from app import crud, models
from app.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=models.SessionCreateResponse)
def create_session(
    req: models.SessionCreateRequest,
    user=Depends(get_current_user)
):
    session_id = crud.create_session(req.filename, req.metadata)
    return {'session_id': session_id}

@router.put("/{session_id}/chunks")
def upload_chunk(
    session_id: str,
    index: int = Form(...),
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    try:
        data = file.file.read()
        crud.save_chunk(session_id, index, data)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to save chunk")
    return JSONResponse({'status': 'ok'})

@router.post("/{session_id}/proof")
def upload_proof(
    session_id: str,
    proof: models.ProofPayload,
    user=Depends(get_current_user)
):
    # Count uploaded chunks
    path = crud.get_session_path(session_id)
    files = [f for f in os.listdir(path) if f.startswith("chunk_")]
    chunk_count = len(files)
    crud.save_proof(session_id, proof.merkle_root, proof.zk_proof, chunk_count)
    return JSONResponse({'status': 'ok'})

@router.get("/{session_id}/metadata", response_model=models.MetadataResponse)
def get_metadata(
    session_id: str,
    user=Depends(get_current_user)
):
    try:
        meta = crud.get_metadata(session_id)
        return meta
    except Exception:
        raise HTTPException(status_code=404, detail="Session not found")

@router.get("/{session_id}/chunks/{index}")
def get_chunk(
    session_id: str,
    index: int,
    user=Depends(get_current_user)
):
    try:
        data = crud.get_chunk(session_id, index)
        return StreamingResponse(iter([data]), media_type="application/octet-stream")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Chunk not found")