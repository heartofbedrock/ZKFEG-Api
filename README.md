# Zero-Knowledge File Exchange Gateway (ZK-FEG)

A FastAPI service providing secure file exchange with zero-knowledge integrity proofs.

## Features
- Create file-exchange sessions
- Upload encrypted file chunks
- Submit Merkle-root + ZK proof
- Download metadata and encrypted chunks
- List and delete sessions
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

# Run locally
uvicorn app.main:app --reload
```
