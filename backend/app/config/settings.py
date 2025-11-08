"""
Application Settings and Configuration
"""

from typing import List, Optional
# from pydantic import BaseSettings, validator
from pydantic_settings import BaseSettings
from pydantic import validator

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings"""

    # Application
    PROJECT_NAME: str = "News Recommendation System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # 5 minutes

    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX: str = "news"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # CORS
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.12.225:3000",  # Frontend Docker container
    ]

    # Logging
    LOG_LEVEL: str = "INFO"

    # External APIs - News Data Sources
    SERPAPI_API_KEY: Optional[str] = None  # SerpAPI for Google News search
    NEWS_API_KEY: Optional[str] = None  # NewsAPI.org
    GNEWS_API_KEY: Optional[str] = None  # GNews.io
    NEWSDATA_API_KEY: Optional[str] = None  # NewsData.io
    
    # Crawler Settings
    CRAWLER_ENABLED: bool = True
    CRAWLER_INTERVAL_MINUTES: int = 30  # Default crawl interval
    CRAWLER_MAX_ARTICLES_PER_RUN: int = 100  # Max articles per crawl
    CRAWLER_DEFAULT_LANGUAGE: str = "zh"  # Default language for news
    CRAWLER_DEFAULT_COUNTRY: str = "cn"  # Default country for news
    CRAWLER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # News Processing Settings
    NEWS_DEDUPLICATION_ENABLED: bool = True
    NEWS_MIN_CONTENT_LENGTH: int = 100  # Minimum content length in characters
    NEWS_AUTO_CATEGORIZE: bool = True  # Auto categorize news based on keywords

    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Recommendation
    RECOMMENDATION_CACHE_TTL: int = 300  # 5 minutes
    DEFAULT_RECOMMENDATION_COUNT: int = 20

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        # .env file is in backend/ directory (BASE_DIR already points to backend/)
        env_file = os.path.join(BASE_DIR, ".env")
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = "allow"  # Allow extra fields in .env


# Create settings instance
settings = Settings()