from fastapi.testclient import TestClient
from packages.core.monkey_coder.app.main import app
import uuid

client = TestClient(app)

def signup_and_get_tokens():
    email = f"rot_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "username": f"rotuser_{uuid.uuid4().hex[:4]}",
        "name": "Rot User",
        "email": email,
        "password": "StrongPass45678",
        "plan": "free"
    }
    r = client.post("/api/v1/auth/signup", json=payload)
    assert r.status_code == 200
    return r

def test_refresh_token_rotation_rejects_old():
    signup_and_get_tokens()
    # First refresh
    r1 = client.post("/api/v1/auth/refresh")
    assert r1.status_code == 200
    # Capture old refresh (sent with request cookies already updated afterwards). To simulate reuse, we need to store prior cookie before second refresh.
    # Extract refresh token cookie after first refresh for reuse attempt.
    refresh_cookie = None
    for c in client.cookies.items():
        if 'refresh' in c[0]:
            refresh_cookie = c[1]
    assert refresh_cookie
    # Second refresh (will revoke previous jti)
    r2 = client.post("/api/v1/auth/refresh")
    assert r2.status_code == 200
    # Attempt reuse of first refresh token by manually setting cookie
    client.cookies.set('refresh_token', refresh_cookie)
    r3 = client.post("/api/v1/auth/refresh")
    assert r3.status_code in (401, 400)
