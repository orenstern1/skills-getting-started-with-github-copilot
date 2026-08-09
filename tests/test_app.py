import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app


client = TestClient(app)


def test_unregister_participant_removes_email():
    response = client.post("/activities/Chess Club/signup?email=test@example.com")
    assert response.status_code == 200

    response = client.delete("/activities/Chess Club/signup?email=test@example.com")
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]

    activities = client.get("/activities").json()
    assert "test@example.com" not in activities["Chess Club"]["participants"]
