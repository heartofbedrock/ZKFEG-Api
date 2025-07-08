from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from .. import crud, models

router = APIRouter(prefix="/v1/sessions", tags=["sessions"])

@router.get("/", response_model=models.SessionListResponse)
def list_sessions():
    sessions = crud.list_sessions()
    return {"sessions": sessions}

@router.post("/", response_model=models.SessionCreateResponse)
def create_session(req: models.SessionCreateRequest):
    sid = crud.create_session(req.filename, req.metadata)
    return {"session_id": sid}

@router.put("/{session_id}/chunks", response_model=models.ChunkUploadResponse)
async def upload_chunk(
    session_id: str,
    index: int = Form(...),
    ciphertext: UploadFile = File(...),
    nonce: UploadFile = File(...),
    tag: UploadFile = File(...)
):
    try:
        data_ct = await ciphertext.read()
        data_nonce = await nonce.read()
        data_tag = await tag.read()
        crud.upload_chunk(session_id, index, data_ct, data_nonce, data_tag)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}

@router.post("/{session_id}/proof", response_model=models.ProofUploadResponse)
def upload_proof(session_id: str, proof: models.ProofUploadRequest):
    try:
        crud.upload_proof(session_id, proof.merkle_root, proof.zk_proof)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}

@router.get("/{session_id}/metadata", response_model=models.MetadataResponse)
def get_metadata(session_id: str):
    try:
        return crud.get_metadata(session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")

@router.get("/{session_id}/chunks/{index}")
def get_chunk(session_id: str, index: int):
    try:
        chunk = crud.get_chunk(session_id, index)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return StreamingResponse(iter([chunk]), media_type="application/octet-stream")

@router.delete("/{session_id}", response_model=models.SessionDeleteResponse)
def delete_session(session_id: str):
    try:
        crud.delete_session(session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True}
