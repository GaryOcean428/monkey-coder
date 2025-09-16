"""Tests for /frontend-status diagnostic endpoint."""

import json
from fastapi.testclient import TestClient

from monkey_coder.app.main import app

def test_frontend_status_shape():
    client = TestClient(app)
    resp = client.get('/frontend-status')
    assert resp.status_code == 200
    data = resp.json()
    assert 'served' in data
    # If served true, expect basic keys
    if data['served']:
        for key in ['static_dir', 'index_hash', 'has_next', 'files']:
            assert key in data, f"Missing key {key} in served frontend status"
    else:
        assert 'reason' in data

def test_frontend_status_json_serializable():
    client = TestClient(app)
    resp = client.get('/frontend-status')
    # Ensure response body is valid JSON (already parsed above). Re-dump for safety.
    json.dumps(resp.json())
