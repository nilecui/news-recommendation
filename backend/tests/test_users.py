"""
Tests for user endpoints
"""
import pytest
from fastapi import status


class TestUsers:
    """Test user management endpoints"""
    
    def test_get_current_user(self, authenticated_client, test_user):
        """Test getting current user information"""
        response = authenticated_client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert "id" in data
    
    def test_update_current_user(self, authenticated_client, test_user):
        """Test updating current user information"""
        response = authenticated_client.put(
            "/api/v1/users/me",
            json={
                "full_name": "Updated Name",
                "bio": "Updated bio",
                "age": 25,
                "gender": "male",
                "location": "Beijing"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["bio"] == "Updated bio"
        assert data["age"] == 25
    
    def test_get_user_profile(self, authenticated_client, test_user, db_session):
        """Test getting user profile"""
        # Create user profile
        from app.models.profile import UserProfile
        profile = UserProfile(
            user_id=test_user.id,
            preferred_language="zh",
            preferred_article_length="medium"
        )
        db_session.add(profile)
        db_session.commit()
        
        response = authenticated_client.get("/api/v1/users/me/profile")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["preferred_language"] == "zh"
    
    def test_update_user_profile(self, authenticated_client, test_user, db_session):
        """Test updating user profile"""
        # Create user profile first
        from app.models.profile import UserProfile
        profile = UserProfile(
            user_id=test_user.id,
            preferred_language="zh"
        )
        db_session.add(profile)
        db_session.commit()
        
        response = authenticated_client.put(
            "/api/v1/users/me/profile",
            json={
                "preferred_language": "en",
                "preferred_article_length": "long",
                "reading_frequency": "high",
                "quality_threshold": 0.8,
                "diversity_preference": 0.7
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["preferred_language"] == "en"
        assert data["preferred_article_length"] == "long"
    
    def test_get_user_history(self, authenticated_client, test_user):
        """Test getting user reading history"""
        response = authenticated_client.get("/api/v1/users/me/history")
        # Should return empty list if no history
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_user_collections(self, authenticated_client, test_user):
        """Test getting user collections"""
        response = authenticated_client.get("/api/v1/users/me/collections")
        # Should return empty list if no collections
        assert response.status_code == status.HTTP_200_OK
    
    def test_delete_account(self, authenticated_client, test_user):
        """Test deleting user account"""
        response = authenticated_client.delete("/api/v1/users/me")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        
        # Verify user is deleted - login should fail
        from app.main import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "Test123456"
            }
        )
        assert login_response.status_code == status.HTTP_401_UNAUTHORIZED

