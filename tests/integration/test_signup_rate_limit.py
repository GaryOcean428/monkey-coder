from fastapi.testclient import TestClient
from packages.core.monkey_coder.app.main import app
import uuid

client = TestClient(app)


def test_signup_rate_limit():
    # Perform up to limit successful-ish attempts (unique emails) then expect 429
    successes = 0
    last_status = None
    for i in range(12):
        email = f"user{i}-{uuid.uuid4().hex[:6]}@example.com"
        payload = {
            "username": f"user{i}{uuid.uuid4().hex[:4]}",
            "name": "Test User",
            "email": email,
            "password": "ComplexPass123!",  # meets policy
            "plan": "free"
        }
        r = client.post("/api/v1/auth/signup", json=payload)
        last_status = r.status_code
        if r.status_code == 200:
            successes += 1
        if r.status_code == 429:
            break
    # Ensure we eventually hit rate limit
    assert last_status == 429, f"Expected 429 after exceeding limit, got {last_status}"  # noqa
    assert successes <= 8  # given limiter threshold
