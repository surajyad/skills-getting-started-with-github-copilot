import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# Helper to reset activities for each test (since in-memory)
@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the participants for each activity
    for activity in app.extra['activities'] if hasattr(app, 'extra') and 'activities' in app.extra else []:
        app.extra['activities'][activity]['participants'] = []
    yield


def test_get_activities():
    # Arrange
    # (No setup needed for this test)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_duplicate():
    # Arrange
    email = "testuser@mergington.edu"
    activity = "Chess Club"

    # Act
    response_first = client.post(f"/activities/{activity}/signup?email={email}")
    response_duplicate = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response_first.status_code == 200
    assert response_duplicate.status_code == 400
    assert "already signed up" in response_duplicate.json()["detail"]


def test_signup_activity_not_found():
    # Arrange
    activity = "Nonexistent"
    email = "someone@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_participant():
    # Arrange
    email = "removeuser@mergington.edu"
    activity = "Chess Club"
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response_remove = client.delete(f"/activities/{activity}/unregister?email={email}")
    response_remove_again = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response_remove.status_code == 200
    assert response_remove_again.status_code == 404
    assert "Participant not found" in response_remove_again.json()["detail"]


def test_unregister_activity_not_found():
    # Arrange
    activity = "Nonexistent"
    email = "someone@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
