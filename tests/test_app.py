import copy
import os
import sys
from urllib.parse import quote

from fastapi.testclient import TestClient
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import activities as app_activities, app


client = TestClient(app)
original_activities = copy.deepcopy(app_activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_activities.clear()
    app_activities.update(copy.deepcopy(original_activities))
    yield
    app_activities.clear()
    app_activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_activity_list():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    email = "test@example.com"
    response = client.post(f"/activities/{quote('Chess Club')}/signup?email={quote(email)}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in app_activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    email = "emma@mergington.edu"
    response = client.post(f"/activities/{quote('Programming Class')}/signup?email={quote(email)}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_email():
    email = "test@example.com"
    response = client.post(f"/activities/{quote('Chess Club')}/signup?email={quote(email)}")
    assert response.status_code == 200

    response = client.delete(f"/activities/{quote('Chess Club')}/signup?email={quote(email)}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in app_activities["Chess Club"]["participants"]


def test_unregister_unknown_participant_returns_404():
    response = client.delete(f"/activities/{quote('Chess Club')}/signup?email={quote('unknown@example.com')}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not registered for this activity"
