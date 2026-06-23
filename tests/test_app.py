"""
AAA-style pytest tests for the Mergington High School API.
"""

import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities state after each test."""
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    return TestClient(app)


class TestRootEndpoint:
    def test_root_redirects_to_static_index_html(self, client):
        # Arrange
        expected_redirect = "/static/index.html"

        # Act
        response = client.get("/", allow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect


class TestGetActivitiesEndpoint:
    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_activity_names = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Swimming Club",
            "Art Studio",
            "Drama Club",
            "Robotics Team",
            "Debate Club",
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert isinstance(activities_data, dict)
        for name in expected_activity_names:
            assert name in activities_data

    def test_get_activities_includes_participants(self, client):
        # Arrange

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        for activity_data in activities_data.values():
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivityEndpoint:
    def test_signup_for_activity_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_registration_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is already signed up for this activity"


class TestUnregisterParticipantEndpoint:
    def test_unregister_participant_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"

    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_nonexistent_participant_returns_404(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
