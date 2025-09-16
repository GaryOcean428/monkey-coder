from fastapi.testclient import TestClient
from packages.core.monkey_coder.app.main import app

client = TestClient(app)


def test_oauth_initiate_google_degraded():
    r = client.get("/api/v1/auth/oauth/google/initiate")
    assert r.status_code == 200
    data = r.json()
    assert data["provider"] == "google"
    assert "authorization_url" in data
    assert data["state"]
    assert data["degraded"] is True  # likely true because env vars not set in tests


def test_oauth_state_mismatch_rejected():
    # Get a valid initiate first
    init = client.get("/api/v1/auth/oauth/github/initiate").json()
    good_state = init["state"]
    # Tamper state (remove last char)
    bad_state = good_state[:-1] + ("A" if good_state[-1] != "A" else "B")
    r = client.get(f"/api/v1/auth/oauth/github/callback?code=dummy&state={bad_state}")
    assert r.status_code == 400


def test_oauth_callback_degraded_success_creates_session():
    init = client.get("/api/v1/auth/oauth/github/initiate").json()
    state = init["state"]
    # Simulate provider redirect with dummy code (degraded mode bypasses exchange)
    r = client.get(f"/api/v1/auth/oauth/github/callback?code=dummycode&state={state}")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["provider"] == "github"
    assert "access_token" in data
    assert data["user"]["email"].endswith("@example.local") or data["user"]["email"].endswith("@users.noreply.github.com")
