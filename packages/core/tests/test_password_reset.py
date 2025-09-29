from fastapi.testclient import TestClient
from monkey_coder.app.main import app, _PASSWORD_RESET_TOKENS
from monkey_coder.database.models import User
import pytest

# For test speed we assume an in-memory or test DB is configured elsewhere.
# These tests focus only on the HTTP contract and in-memory token store logic.

client = TestClient(app)

@pytest.mark.asyncio
async def test_password_reset_flow(monkeypatch):
    from unittest.mock import AsyncMock
    async def mock_check_rate_limit(*args, **kwargs):
        return True  # Always allow requests
    
    from monkey_coder.middleware.rate_limiter import get_rate_limiter
    limiter = get_rate_limiter()
    if hasattr(limiter, '_fallback_store'):
        limiter._fallback_store.clear()
    
    monkeypatch.setattr('monkey_coder.middleware.rate_limiter.check_rate_limit', mock_check_rate_limit)
    
    # Create a fake user in DB via monkeypatching User.get_by_email and get_by_id
    class DummyUser:
        def __init__(self):
            self.id = "user-123"
            self.password_hash = "oldhash"
        async def update_password(self, new_hash: str):
            self.password_hash = new_hash
    dummy = DummyUser()

    async def fake_get_by_email(email: str):
        return dummy if email == "test@example.com" else None
    async def fake_get_by_id(uid: str):
        return dummy if uid == dummy.id else None

    monkeypatch.setattr(User, 'get_by_email', fake_get_by_email)
    monkeypatch.setattr(User, 'get_by_id', fake_get_by_id)
    
    from monkey_coder.app import main as main_module
    main_module._enforce_csrf = lambda request: None

    # Step 1: request reset
    resp = client.post('/api/v1/auth/password/forgot', json={'email': 'test@example.com'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'ok'
    assert 'debug_token' in data  # since ENV != production
    raw_token = data['debug_token']

    # Step 2: confirm reset
    resp2 = client.post('/api/v1/auth/password/reset', json={'token': raw_token, 'new_password': 'NewSecurePass123!'})
    assert resp2.status_code == 200
    assert resp2.json()['status'] == 'password_reset'

    # Ensure token invalidated
    from monkey_coder.app.main import _hash_reset_token
    token_hash = _hash_reset_token(raw_token)
    assert token_hash not in _PASSWORD_RESET_TOKENS

@pytest.mark.asyncio
async def test_password_reset_invalid_token():
    resp = client.post('/api/v1/auth/password/reset', json={'token': 'badtoken', 'new_password': 'Whatever123!'})
    assert resp.status_code == 400
