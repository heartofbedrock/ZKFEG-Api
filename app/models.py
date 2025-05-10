from pydantic import BaseModel
from typing import Optional

class SessionCreateRequest(BaseModel):
    filename: str
    metadata: Optional[dict] = {}

class SessionCreateResponse(BaseModel):
    session_id: str

class ProofPayload(BaseModel):
    merkle_root: str
    zk_proof: str

class MetadataResponse(BaseModel):
    filename: str
    metadata: dict
    merkle_root: str
    chunk_count: int