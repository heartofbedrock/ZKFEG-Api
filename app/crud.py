import os
import json
from .core.config import settings
from .local import LocalZKFileExchange

_engine = LocalZKFileExchange(settings.STORAGE_DIR)

def create_session(filename: str, metadata: dict) -> str:
    return _engine.create_session(filename, metadata)

def upload_chunk(session_id: str, index: int, ciphertext: bytes, nonce: bytes, tag: bytes):
    path = os.path.join(settings.STORAGE_DIR, session_id)
    fname = f"chunk_{index:05d}.bin"
    with open(os.path.join(path, fname), "wb") as f:
        f.write(nonce + tag + ciphertext)

def upload_proof(session_id: str, merkle_root: str, zk_proof: str):
    path = os.path.join(settings.STORAGE_DIR, session_id)
    count = len([n for n in os.listdir(path) if n.startswith("chunk_")])
    with open(os.path.join(path, "proof.json"), "w") as f:
        json.dump(
            {"merkle_root": merkle_root, "zk_proof": zk_proof, "chunk_count": count}, f
        )

def get_metadata(session_id: str) -> dict:
    path = os.path.join(settings.STORAGE_DIR, session_id, "proof.json")
    with open(path) as f:
        return json.load(f)

def get_chunk(session_id: str, index: int) -> bytes:
    path = os.path.join(settings.STORAGE_DIR, session_id, f"chunk_{index:05d}.bin")
    return open(path, "rb").read()
