import os
import uuid
import json
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

CHUNK_SIZE = 1 << 20  # 1 MiB per chunk

def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def compute_merkle_root(hashes: list[bytes]) -> bytes:
    if not hashes:
        return b'\x00' * 32
    layer = hashes[:]
    while len(layer) > 1:
        if len(layer) % 2:
            layer.append(layer[-1])
        layer = [sha256(layer[i] + layer[i+1]) for i in range(0, len(layer), 2)]
    return layer[0]

class LocalZKFileExchange:
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def create_session(self, filename: str, metadata: dict = None) -> str:
        session_id = str(uuid.uuid4())
        path = os.path.join(self.storage_dir, session_id)
        os.makedirs(path)
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump({"filename": filename, "metadata": metadata or {}}, f)
        return session_id

    def encrypt_and_chunk(self, filepath: str):
        key = AESGCM.generate_key(bit_length=256)
        aesgcm = AESGCM(key)
        chunk_hashes, encrypted = [], []

        with open(filepath, "rb") as f:
            idx = 0
            while (data := f.read(CHUNK_SIZE)):
                nonce = os.urandom(12)
                ct = aesgcm.encrypt(nonce, data, None)
                ciphertext, tag = ct[:-16], ct[-16:]
                encrypted.append(
                    {"index": idx, "ciphertext": ciphertext, "nonce": nonce, "tag": tag}
                )
                chunk_hashes.append(sha256(ciphertext))
                idx += 1

        root = compute_merkle_root(chunk_hashes)
        return encrypted, root, aesgcm

    def generate_zk_proof(self, merkle_root: bytes, metadata: dict) -> bytes:
        # Stub: integrate your ZK toolchain here
        return b"PROOF_PLACEHOLDER"

    def upload(self, session_id: str, encrypted_chunks, merkle_root: bytes, zk_proof: bytes):
        path = os.path.join(self.storage_dir, session_id)
        for c in encrypted_chunks:
            fname = f"chunk_{c['index']:05d}.bin"
            with open(os.path.join(path, fname), "wb") as f:
                f.write(c["nonce"] + c["tag"] + c["ciphertext"])
        with open(os.path.join(path, "proof.json"), "w") as f:
            json.dump(
                {
                    "merkle_root": merkle_root.hex(),
                    "zk_proof": zk_proof.hex(),
                    "chunk_count": len(encrypted_chunks),
                },
                f,
            )

    def download_and_decrypt(self, session_id: str, aesgcm: AESGCM, out_path: str):
        path = os.path.join(self.storage_dir, session_id)
        with open(os.path.join(path, "proof.json")) as f:
            proof = json.load(f)
        expected_root = bytes.fromhex(proof["merkle_root"])
        count = proof["chunk_count"]

        hashes = []
        with open(out_path, "wb") as out:
            for i in range(count):
                fname = os.path.join(path, f"chunk_{i:05d}.bin")
                raw = open(fname, "rb").read()
                nonce, tag, ct = raw[:12], raw[12:28], raw[28:]
                hashes.append(sha256(ct))
                pt = aesgcm.decrypt(nonce, ct + tag, None)
                out.write(pt)

        actual_root = compute_merkle_root(hashes)
        if actual_root != expected_root:
            raise ValueError("Merkle root mismatch")
