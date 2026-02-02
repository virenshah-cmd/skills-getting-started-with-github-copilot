import pytest
from src.app import activities


class TestActivitiesAPI:
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static index"""
        response = client.get("/")
        assert response.status_code == 200  # FastAPI TestClient follows redirects by default
        assert "text/html" in response.headers.get("content-type", "")

    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        # Check that each activity has required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_signup_success(self, client):
        """Test successful signup"""
        # Use an activity that exists
        activity_name = "Chess Club"
        email = "test@example.com"

        # Ensure the email is not already signed up
        initial_participants = activities[activity_name]["participants"].copy()
        if email in initial_participants:
            activities[activity_name]["participants"].remove(email)

        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify the participant was added
        assert email in activities[activity_name]["participants"]

        # Clean up
        activities[activity_name]["participants"].remove(email)

    def test_signup_activity_not_found(self, client):
        """Test signup with non-existent activity"""
        response = client.post("/activities/NonExistentActivity/signup?email=test@example.com")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_already_signed_up(self, client):
        """Test signup when already signed up"""
        activity_name = "Chess Club"
        email = activities[activity_name]["participants"][0]  # Use existing participant

        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_unregister_success(self, client):
        """Test successful unregister"""
        activity_name = "Programming Class"
        email = "test_unregister@example.com"

        # First sign up
        activities[activity_name]["participants"].append(email)

        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

        # Verify the participant was removed
        assert email not in activities[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Test unregister with non-existent activity"""
        response = client.delete("/activities/NonExistentActivity/unregister?email=test@example.com")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_not_signed_up(self, client):
        """Test unregister when not signed up"""
        activity_name = "Chess Club"
        email = "not_signed_up@example.com"

        # Ensure not signed up
        if email in activities[activity_name]["participants"]:
            activities[activity_name]["participants"].remove(email)

        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]