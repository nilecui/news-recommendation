"""
Tests for news endpoints
"""
import pytest
from fastapi import status
from datetime import datetime, timezone


class TestNews:
    """Test news endpoints"""
    
    def test_get_news_detail(self, client, test_news):
        """Test getting news detail"""
        response = client.get(f"/api/v1/news/{test_news.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_news.id
        assert data["title"] == test_news.title
        assert "content" in data
    
    def test_get_news_detail_not_found(self, client):
        """Test getting non-existent news"""
        response = client.get("/api/v1/news/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_latest_news(self, client, test_news):
        """Test getting latest news"""
        response = client.get("/api/v1/news/latest")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data or isinstance(data, list)
    
    def test_get_news_by_category(self, client, test_news, test_category):
        """Test getting news by category"""
        response = client.get(f"/api/v1/news/category/{test_category.name}")
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_trending_news(self, client, test_news):
        """Test getting trending news"""
        response = client.get("/api/v1/news/trending")
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_news(self, client, test_news):
        """Test searching news"""
        response = client.post(
            "/api/v1/news/search",
            json={
                "query": "test",
                "page": 1,
                "page_size": 20
            }
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_like_news(self, authenticated_client, test_news):
        """Test liking news"""
        response = authenticated_client.post(f"/api/v1/news/{test_news.id}/like")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "liked" in data or "message" in data
    
    def test_collect_news(self, authenticated_client, test_news):
        """Test collecting news"""
        response = authenticated_client.post(f"/api/v1/news/{test_news.id}/collect")
        assert response.status_code == status.HTTP_200_OK
    
    def test_share_news(self, authenticated_client, test_news):
        """Test sharing news"""
        response = authenticated_client.post(
            f"/api/v1/news/{test_news.id}/share?platform=wechat"
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_like_news_unauthorized(self, client, test_news):
        """Test liking news without authentication"""
        response = client.post(f"/api/v1/news/{test_news.id}/like")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

