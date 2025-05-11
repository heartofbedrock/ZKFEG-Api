from pydantic import BaseModel
from typing import Any, Dict

class SessionCreateRequest(BaseModel):
    filename: str
    metadata: Dict[str, Any] = {}

class SessionCreateResponse(BaseModel):
    session_id: str

class ChunkUploadResponse(BaseModel):
    success: bool

class ProofUploadRequest(BaseModel):
    merkle_root: str
    zk_proof: str

class ProofUploadResponse(BaseModel):
    success: bool

class MetadataResponse(BaseModel):
    merkle_root: str
    zk_proof: str
    chunk_count: int
