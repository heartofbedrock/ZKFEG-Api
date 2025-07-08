import os
import sys
import shutil
sys.path.insert(0, os.path.abspath("."))
from fastapi.testclient import TestClient
from app.main import app


def setup_module(module):
    os.environ['STORAGE_DIR'] = './test_storage'
    if os.path.isdir('./test_storage'):
        shutil.rmtree('./test_storage')
    os.makedirs('./test_storage')


def teardown_module(module):
    if os.path.isdir('./test_storage'):
        shutil.rmtree('./test_storage')


client = TestClient(app)

def test_session_lifecycle():
    # create session
    resp = client.post('/v1/sessions/', json={'filename': 'foo.txt', 'metadata': {}})
    assert resp.status_code == 200
    sid = resp.json()['session_id']

    # list sessions should contain new id
    resp = client.get('/v1/sessions/')
    assert resp.status_code == 200
    assert sid in resp.json()['sessions']

    # delete session
    resp = client.delete(f'/v1/sessions/{sid}')
    assert resp.status_code == 200

    # list sessions should not contain id
    resp = client.get('/v1/sessions/')
    assert sid not in resp.json()['sessions']

