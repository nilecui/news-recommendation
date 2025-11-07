"""
Tests for recommendation endpoints
"""
import pytest
from fastapi import status


class TestRecommendations:
    """Test recommendation endpoints"""
    
    def test_get_personalized_recommendations(self, authenticated_client, test_user, test_news):
        """Test getting personalized recommendations"""
        response = authenticated_client.get("/api/v1/recommendations/?page=1&limit=20")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data or isinstance(data, list)
    
    def test_get_cold_start_recommendations(self, authenticated_client, test_user, test_category):
        """Test getting cold start recommendations"""
        response = authenticated_client.get(
            f"/api/v1/recommendations/cold-start?categories={test_category.name}&limit=20"
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_similar_news(self, authenticated_client, test_news):
        """Test getting similar news"""
        response = authenticated_client.get(f"/api/v1/recommendations/similar/{test_news.id}?limit=10")
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_popular_news(self, authenticated_client):
        """Test getting popular news"""
        response = authenticated_client.get("/api/v1/recommendations/popular?timeframe=day&limit=20")
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_discovery_recommendations(self, authenticated_client):
        """Test getting discovery recommendations"""
        response = authenticated_client.get("/api/v1/recommendations/discovery?limit=20")
        assert response.status_code == status.HTTP_200_OK
    
    def test_submit_recommendation_feedback(self, authenticated_client, test_news):
        """Test submitting recommendation feedback"""
        response = authenticated_client.post(
            f"/api/v1/recommendations/feedback?news_id={test_news.id}&feedback_type=like"
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_recommendations_unauthorized(self, client):
        """Test getting recommendations without authentication"""
        response = client.get("/api/v1/recommendations/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

