# Zero-Knowledge File Exchange Gateway (ZK-FEG)

A FastAPI service providing secure file exchange with zero-knowledge integrity proofs.

## Features
- Create file-exchange sessions
- Upload encrypted file chunks
- Submit Merkle-root + ZK proof
- Download metadata and encrypted chunks
- List and delete sessions
- Simple web interface for uploading and sharing files
- Health check endpoint

## Requirements
- Python 3.11+
- Dependencies in `requirements.txt`

## Setup
```bash
# Clone repo
git clone <repo_url>
cd zk_feg_api_repo

# Create virtual env & install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

## Usage
After starting the server you can interact with the API using any HTTP client.

### 1. Create a session
```bash
curl -X POST http://localhost:8000/v1/sessions/ \
  -H "Content-Type: application/json" \
  -d '{"filename": "example.txt", "metadata": {}}'
```
The response contains a `session_id` used for subsequent requests.

### 2. Upload encrypted file chunks
```bash
curl -X PUT http://localhost:8000/v1/sessions/<SESSION_ID>/chunks \
  -F index=0 \
  -F ciphertext=@chunk0.bin \
  -F nonce=@nonce0.bin \
  -F tag=@tag0.bin
```
Repeat for each chunk of your encrypted file.

### 3. Submit the Merkle proof
```bash
curl -X POST http://localhost:8000/v1/sessions/<SESSION_ID>/proof \
  -H "Content-Type: application/json" \
  -d '{"merkle_root": "<root>", "zk_proof": "<proof>"}'
```

### 4. Share and retrieve files
Share the `session_id` with another user. They can download the metadata
and encrypted chunks using:
```bash
curl http://localhost:8000/v1/sessions/<SESSION_ID>/metadata
curl http://localhost:8000/v1/sessions/<SESSION_ID>/chunks/0 > chunk0.bin
```
Combine all chunks to reconstruct the file using your decryption process.

### Web interface
The server also provides a simple UI at `http://localhost:8000/`.

1. Open the page and upload a file using the form.
2. After upload you will receive a unique sharing link and nonce.
3. Send the link and nonce to your recipient.
4. The recipient opens the link, enters the nonce and can download all
   encrypted chunks as a single zip archive.

The web pages are styled with basic CSS so they look pleasant without any
additional configuration.
