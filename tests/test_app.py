import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_returns_200(self):
        """Test that getting all activities returns success status"""
        # Arrange
        expected_status = 200

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == expected_status

    def test_get_activities_returns_dict(self):
        """Test that activities endpoint returns a dictionary"""
        # Arrange
        expected_type = dict

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert isinstance(data, expected_type)

    def test_get_activities_contains_default_activities(self):
        """Test that endpoint returns expected default activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity in expected_activities:
            assert activity in data

    def test_activity_has_required_fields(self):
        """Test that each activity contains all required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]

        # Assert
        for field in required_fields:
            assert field in activity

    def test_participants_field_is_list(self):
        """Test that participants field is a list"""
        # Arrange
        expected_type = list

        # Act
        response = client.get("/activities")
        data = response.json()
        participants = data["Chess Club"]["participants"]

        # Assert
        assert isinstance(participants, expected_type)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_with_valid_activity_and_email(self):
        """Test successful signup with valid activity and email"""
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"
        expected_status = 200

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_status
        assert "Signed up" in response.json()["message"]

    def test_signup_adds_participant_to_list(self):
        """Test that signup actually adds the participant"""
        # Arrange
        activity = "Programming Class"
        email = "verify@mergington.edu"

        # Act
        client.post(f"/activities/{activity}/signup", params={"email": email})
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]

        # Assert
        assert email in participants

    def test_signup_duplicate_email_returns_400(self):
        """Test that duplicate signup is rejected"""
        # Arrange
        activity = "Gym Class"
        email = "duplicate@mergington.edu"
        expected_status = 400

        # Act
        client.post(f"/activities/{activity}/signup", params={"email": email})
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_status
        assert "Already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self):
        """Test that signup to non-existent activity returns 404"""
        # Arrange
        activity = "Nonexistent Club"
        email = "test@mergington.edu"
        expected_status = 404

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_status
        assert "not found" in response.json()["detail"].lower()


class TestDeleteEndpoint:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""

    def test_delete_existing_participant_returns_200(self):
        """Test successful removal of existing participant"""
        # Arrange
        activity = "Chess Club"
        email = "removal@mergington.edu"
        client.post(f"/activities/{activity}/signup", params={"email": email})
        expected_status = 200

        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_status
        assert "Removed" in response.json()["message"]

    def test_delete_removes_participant_from_list(self):
        """Test that delete actually removes the participant"""
        # Arrange
        activity = "Programming Class"
        email = "removeme@mergington.edu"
        client.post(f"/activities/{activity}/signup", params={"email": email})

        # Act
        client.delete(f"/activities/{activity}/signup", params={"email": email})
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]

        # Assert
        assert email not in participants

    def test_delete_nonexistent_participant_returns_404(self):
        """Test that deleting non-existent participant returns 404"""
        # Arrange
        activity = "Gym Class"
        email = "notexist@mergington.edu"
        expected_status = 404

        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_status

    def test_delete_from_nonexistent_activity_returns_404(self):
        """Test that deleting from non-existent activity returns 404"""
        # Arrange
        activity = "Fake Club"
        email = "test@mergington.edu"
        expected_status = 404

        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_status


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_returns_redirect(self):
        """Test that root endpoint redirects"""
        # Arrange
        expected_status = 307

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == expected_status

    def test_root_redirects_to_static_index(self):
        """Test that root redirects to correct location"""
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)
        location = response.headers.get("location")

        # Assert
        assert location == expected_location
