from fastapi.testclient import TestClient
from packages.core.monkey_coder.app.main import app
import uuid

client = TestClient(app)


def create_user(email: str):
    payload = {
        "username": f"u_{uuid.uuid4().hex[:6]}",
        "name": "Verif User",
        "email": email,
        "password": "StrongPass12345",
        "plan": "free"
    }
    r = client.post("/api/v1/auth/signup", json=payload)
    assert r.status_code == 200
    return r


def test_email_verification_request_and_confirm():
    email = f"verify_{uuid.uuid4().hex[:6]}@example.com"
    create_user(email)
    # Request verification
    r = client.post("/api/v1/auth/verify/email/request", json={"email": email})
    assert r.status_code == 200
    data = r.json()
    token = data.get("debug_token")
    assert token
    # Confirm
    r2 = client.post("/api/v1/auth/verify/email/confirm", json={"token": token})
    assert r2.status_code == 200
    assert r2.json()["status"] == "email_verified"
    # Idempotent second confirm (should 400 invalid since token used)
    r3 = client.post("/api/v1/auth/verify/email/confirm", json={"token": token})
    assert r3.status_code == 400


def test_email_verification_invalid_token():
    r = client.post("/api/v1/auth/verify/email/confirm", json={"token": "notreal"})
    assert r.status_code == 400
