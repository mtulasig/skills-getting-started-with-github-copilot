from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of original participants to restore after each test
    original = {k: v["participants"][:] for k, v in activities.items()}
    yield
    for k, v in original.items():
        activities[k]["participants"] = v[:]


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_duplicate_blocked():
    client = TestClient(app)
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # signup should succeed
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # duplicate signup (different case / whitespace) should be rejected
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": "  NewStudent@mergington.edu "})
    assert resp2.status_code == 400


def test_remove_participant():
    client = TestClient(app)
    activity = "Tennis Team"
    # ensure there is a known participant
    participant = activities[activity]["participants"][0]

    resp = client.delete(f"/activities/{activity}/participants", params={"email": participant})
    assert resp.status_code == 200
    assert participant not in activities[activity]["participants"]

    # removing again should return 404
    resp2 = client.delete(f"/activities/{activity}/participants", params={"email": participant})
    assert resp2.status_code == 404
