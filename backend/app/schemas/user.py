"""
User schemas for request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator


class UserBase(BaseModel):
    """Base schema for user"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)


class UserResponse(BaseModel):
    """Schema for user response (public info)"""
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    is_verified: bool
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    language: str
    created_at: datetime
    last_login_at: Optional[datetime] = None
    reading_count: int
    like_count: int
    share_count: int

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user info"""
    full_name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=500)
    bio: Optional[str] = None
    age: Optional[int] = Field(None, ge=13, le=120)
    gender: Optional[str] = Field(None, pattern=r'^(male|female|other)$')
    location: Optional[str] = Field(None, max_length=255)
    language: Optional[str] = Field(None, max_length=10)


class UserProfileResponse(BaseModel):
    """Schema for user profile response"""
    id: int
    user_id: int
    preferred_categories: Optional[Dict[str, float]] = None
    preferred_tags: Optional[Dict[str, float]] = None
    preferred_sources: Optional[Dict[str, float]] = None
    blocked_sources: Optional[List[str]] = None
    blocked_keywords: Optional[List[str]] = None
    preferred_language: str
    preferred_article_length: str
    reading_frequency: str
    interest_keywords: Optional[Dict[str, float]] = None
    interest_categories: Optional[Dict[str, float]] = None
    typical_reading_times: Optional[Dict[str, float]] = None
    typical_session_duration: float
    bounce_rate: float
    quality_threshold: float
    diversity_preference: float
    novelty_preference: float
    email_notifications: bool
    push_notifications: bool
    notification_frequency: str
    notification_categories: Optional[List[str]] = None
    data_collection_allowed: bool
    personalization_allowed: bool
    analytics_sharing_allowed: bool
    education_level: Optional[str] = None
    occupation: Optional[str] = None
    interests: Optional[List[str]] = None
    model_version: Optional[str] = None
    last_profile_update: datetime
    profile_confidence: float
    created_at: datetime
    updated_at: datetime

    # Computed properties
    is_cold_start_user: Optional[bool] = None
    profile_completeness: Optional[float] = None

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    preferred_categories: Optional[Dict[str, float]] = None
    preferred_tags: Optional[Dict[str, float]] = None
    preferred_sources: Optional[Dict[str, float]] = None
    blocked_sources: Optional[List[str]] = None
    blocked_keywords: Optional[List[str]] = None
    preferred_language: Optional[str] = Field(None, max_length=10)
    preferred_article_length: Optional[str] = Field(None, pattern=r'^(short|medium|long)$')
    reading_frequency: Optional[str] = Field(None, pattern=r'^(low|medium|high)$')
    quality_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    diversity_preference: Optional[float] = Field(None, ge=0.0, le=1.0)
    novelty_preference: Optional[float] = Field(None, ge=0.0, le=1.0)
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    notification_frequency: Optional[str] = Field(None, pattern=r'^(immediate|daily|weekly)$')
    notification_categories: Optional[List[str]] = None
    data_collection_allowed: Optional[bool] = None
    personalization_allowed: Optional[bool] = None
    analytics_sharing_allowed: Optional[bool] = None
    education_level: Optional[str] = Field(None, max_length=50)
    occupation: Optional[str] = Field(None, max_length=100)
    interests: Optional[List[str]] = None


class UserPreferenceItem(BaseModel):
    """Schema for a single user preference"""
    id: int
    preference_type: str
    preference_key: str
    preference_value: float
    source: Optional[str] = None
    confidence: float
    weight: float
    created_at: datetime
    updated_at: datetime
    last_seen: Optional[datetime] = None
    is_positive_preference: Optional[bool] = None
    is_strong_preference: Optional[bool] = None

    class Config:
        from_attributes = True


class UserPreferenceCreate(BaseModel):
    """Schema for creating user preference"""
    preference_type: str = Field(..., pattern=r'^(category|source|topic|author)$')
    preference_key: str = Field(..., max_length=255)
    preference_value: float = Field(..., ge=-1.0, le=1.0)
    source: str = Field("explicit", pattern=r'^(explicit|implicit|ml)$')
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    weight: float = Field(1.0, ge=0.0)


class UserPreferenceUpdate(BaseModel):
    """Schema for updating user preference"""
    preference_value: Optional[float] = Field(None, ge=-1.0, le=1.0)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    weight: Optional[float] = Field(None, ge=0.0)


class UserStatsResponse(BaseModel):
    """Schema for user statistics"""
    total_reading_count: int
    total_like_count: int
    total_share_count: int
    total_bookmark_count: int
    total_reading_time: float  # in hours
    average_session_duration: float  # in minutes
    most_read_categories: List[Dict[str, Any]]
    most_read_tags: List[Dict[str, Any]]
    reading_streak_days: int
    last_active_at: Optional[datetime] = None
    member_since: datetime


class UserHistoryRequest(BaseModel):
    """Schema for user history request"""
    behavior_type: Optional[str] = Field(None, pattern=r'^(read|like|share|bookmark)$')
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category_id: Optional[int] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class UserHistoryItem(BaseModel):
    """Schema for user history item"""
    id: int
    news_id: int
    news_title: str
    news_summary: Optional[str] = None
    news_image_url: Optional[str] = None
    news_category: Optional[str] = None
    behavior_type: str
    duration: Optional[float] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class UserHistoryResponse(BaseModel):
    """Schema for user history response"""
    items: List[UserHistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class UserRecommendationPreferences(BaseModel):
    """Schema for user recommendation preferences (onboarding)"""
    categories: List[int] = Field(..., min_items=1, max_items=10)
    tags: Optional[List[str]] = Field(None, max_items=20)
    preferred_sources: Optional[List[str]] = None
    article_length: str = Field("medium", pattern=r'^(short|medium|long)$')
    diversity_preference: float = Field(0.5, ge=0.0, le=1.0)
    novelty_preference: float = Field(0.5, ge=0.0, le=1.0)
