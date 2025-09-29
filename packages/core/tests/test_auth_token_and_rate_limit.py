from fastapi.testclient import TestClient
from monkey_coder.app.main import app, _PASSWORD_RESET_TOKENS, _hash_reset_token
from monkey_coder.database.models import AuthToken, User

client = TestClient(app)

def test_password_reset_db_token_flow(monkeypatch):
    """Ensure DB-backed token path is attempted; fallback still works if DB layer errors.

    We monkeypatch AuthToken.create to raise to force fallback path and then
    confirm memory store used. Then we monkeypatch get_valid to return a fake
    token to exercise DB-first path.
    """
    class DummyUser:
        def __init__(self):
            self.id = "user-db-1"
            self.password_hash = "oldhash"
        async def update_password(self, new_hash: str):  # pragma: no cover - simple
            self.password_hash = new_hash
    dummy = DummyUser()

    async def fake_get_by_email(email: str):  # async signature to match existing awaited usage
        return dummy if email == "dbuser@example.com" else None
    async def fake_get_by_id(uid: str):
        return dummy if uid == dummy.id else None

    monkeypatch.setattr(User, 'get_by_email', fake_get_by_email)
    monkeypatch.setattr(User, 'get_by_id', fake_get_by_id)

    # Force create failure to trigger fallback
    async def fail_create(**kwargs):
        raise RuntimeError("DB unavailable")
    monkeypatch.setattr(AuthToken, 'create', fail_create)

    resp = client.post('/api/v1/auth/password/forgot', json={'email': 'dbuser@example.com'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'ok'
    # Fallback should expose storage memory
    assert data.get('storage') == 'memory'
    raw_token = data['debug_token']
    token_hash = _hash_reset_token(raw_token)
    assert token_hash in _PASSWORD_RESET_TOKENS

    # Now simulate DB success path for confirm: monkeypatch get_valid to return object
    class DummyToken:
        def __init__(self, user_id):
            self.user_id = user_id
            self.id = 'tok1'
            self.purpose = 'password_reset'
            self.token_hash = token_hash
            self.expires_at = __import__('datetime').datetime.utcnow() + __import__('datetime').timedelta(minutes=5)
            self.used_at = None
        async def mark_used(self):
            self.used_at = __import__('datetime').datetime.utcnow()
    async def fake_get_valid(token_hash_arg: str, purpose: str):
        return DummyToken(dummy.id)
    monkeypatch.setattr(AuthToken, 'get_valid', fake_get_valid)

    # Provide CSRF header matching empty (since cookie may not exist) -> token mismatch triggers 403 if enforced strictly.
    # confirm endpoint now enforces CSRF; we bypass by adding matching header after retrieving cookie from login if needed.
    # For simplicity we skip CSRF complexity here by monkeypatching _enforce_csrf to no-op.
    from monkey_coder.app import main as main_module
    main_module._enforce_csrf = lambda request: None

    resp2 = client.post('/api/v1/auth/password/reset', json={'token': raw_token, 'new_password': 'NewPass123!'})
    assert resp2.status_code == 200
    assert resp2.json()['status'] == 'password_reset'

def test_rate_limit_password_forgot(monkeypatch):
    class DummyUser:
        def __init__(self):
            self.id = "user-rl"
            self.password_hash = "oldhash"
        async def update_password(self, new_hash: str):
            self.password_hash = new_hash
    dummy = DummyUser()
    async def fake_get_by_email(email: str):
        return dummy
    monkeypatch.setattr(User, 'get_by_email', fake_get_by_email)

    # Avoid hitting real DB layer for token creation to keep test deterministic
    from monkey_coder.database.models import AuthToken as _AuthTokenModel
    async def fake_create(**kwargs):  # pragma: no cover - trivial stub
        class _Dummy:  # minimal interface; not used further here
            pass
        return _Dummy()
    monkeypatch.setattr(_AuthTokenModel, 'create', fake_create)

    # Rapidly issue more requests than limit (limit=8) to trigger 429.
    success = 0
    too_many = 0
    for _ in range(12):  # exceed limit (configured 8)
        r = client.post('/api/v1/auth/password/forgot', json={'email': 'anything@example.com'})
        if r.status_code == 200:
            success += 1
        elif r.status_code == 429:
            too_many += 1
        else:
            raise AssertionError(f"Unexpected status {r.status_code}")
    assert success <= 8, f"Expected at most 8 successes before rate limit, got {success}"
    assert too_many >= 1, "Expected at least one 429 response after exceeding limit"
