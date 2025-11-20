import os
import sys
from fastapi.testclient import TestClient

# Ensure we can import the app module from src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from app import app  # noqa: E402


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic sanity checks
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "pytest_user@example.com"

    # Ensure clean state: if the test email exists, remove it first
    current = client.get("/activities").json()
    if email in current.get(activity, {}).get("participants", []):
        client.delete(f"/activities/{activity}/participants?email={email}")

    # Signup should succeed
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert f"Signed up {email}" in resp.json().get("message", "")

    # Signup again should fail with 400 (already signed up)
    resp_dup = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp_dup.status_code == 400

    # Verify participant present
    after = client.get("/activities").json()
    assert email in after.get(activity, {}).get("participants", [])

    # Unregister should succeed
    resp_del = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp_del.status_code == 200
    assert f"Unregistered {email}" in resp_del.json().get("message", "")

    # Verify removed
    final = client.get("/activities").json()
    assert email not in final.get(activity, {}).get("participants", [])
