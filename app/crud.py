import os
import uuid
import json
from app.core.config import settings


def init_storage():
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)


def get_session_path(session_id: str) -> str:
    return os.path.join(settings.STORAGE_DIR, session_id)


def create_session(filename: str, metadata: dict) -> str:
    init_storage()
    session_id = str(uuid.uuid4())
    path = get_session_path(session_id)
    os.makedirs(path)
    with open(os.path.join(path, 'metadata.json'), 'w') as f:
        json.dump({'filename': filename, 'metadata': metadata}, f)
    return session_id


def save_chunk(session_id: str, index: int, data: bytes) -> None:
    path = get_session_path(session_id)
    os.makedirs(path, exist_ok=True)
    chunk_path = os.path.join(path, f"chunk_{index:05d}.bin")
    with open(chunk_path, 'wb') as f:
        f.write(data)


def save_proof(session_id: str, merkle_root: str, zk_proof: str, chunk_count: int) -> None:
    path = get_session_path(session_id)
    with open(os.path.join(path, 'proof.json'), 'w') as f:
        json.dump({
            'merkle_root': merkle_root,
            'zk_proof': zk_proof,
            'chunk_count': chunk_count
        }, f)


def get_metadata(session_id: str) -> dict:
    path = get_session_path(session_id)
    meta = json.load(open(os.path.join(path, 'metadata.json')))
    proof = json.load(open(os.path.join(path, 'proof.json')))
    return {
        'filename': meta['filename'],
        'metadata': meta['metadata'],
        'merkle_root': proof['merkle_root'],
        'chunk_count': proof['chunk_count']
    }


def get_chunk(session_id: str, index: int) -> bytes:
    path = get_session_path(session_id)
    chunk_path = os.path.join(path, f"chunk_{index:05d}.bin")
    with open(chunk_path, 'rb') as f:
        return f.read()