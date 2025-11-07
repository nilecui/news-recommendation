"""
Tracking and behavior schemas for request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class BehaviorBase(BaseModel):
    """Base schema for user behavior"""
    user_id: int
    news_id: int
    behavior_type: str = Field(..., pattern=r'^(impression|click|read|like|share|comment|bookmark)$')
    position: Optional[int] = Field(None, ge=0)
    page: int = Field(1, ge=1)
    context: Optional[Dict[str, Any]] = None
    duration: Optional[float] = Field(None, ge=0.0)
    scroll_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    read_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    sentiment: Optional[str] = Field(None, pattern=r'^(positive|negative|neutral)$')
    feedback_score: Optional[float] = Field(None, ge=1.0, le=5.0)
    feedback_text: Optional[str] = Field(None, max_length=1000)
    recommendation_id: Optional[str] = Field(None, max_length=100)
    algorithm_version: Optional[str] = Field(None, max_length=20)
    ab_test_group: Optional[str] = Field(None, max_length=20)
    device_type: Optional[str] = Field(None, pattern=r'^(mobile|desktop|tablet)$')
    platform: Optional[str] = Field(None, pattern=r'^(web|ios|android)$')
    session_id: Optional[str] = Field(None, max_length=100)


class BehaviorCreate(BehaviorBase):
    """Schema for creating a behavior record"""
    pass


class BehaviorBatchItem(BaseModel):
    """Schema for a single behavior in batch tracking"""
    news_id: int
    behavior_type: str = Field(..., pattern=r'^(impression|click|read|like|share|comment|bookmark)$')
    position: Optional[int] = Field(None, ge=0)
    page: int = Field(1, ge=1)
    context: Optional[Dict[str, Any]] = None
    duration: Optional[float] = Field(None, ge=0.0)
    scroll_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    read_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    timestamp: Optional[datetime] = None


class BehaviorBatchRequest(BaseModel):
    """Schema for batch behavior tracking request"""
    behaviors: List[BehaviorBatchItem] = Field(..., min_items=1, max_items=100)
    session_id: Optional[str] = Field(None, max_length=100)
    device_type: Optional[str] = Field(None, pattern=r'^(mobile|desktop|tablet)$')
    platform: Optional[str] = Field(None, pattern=r'^(web|ios|android)$')
    recommendation_id: Optional[str] = Field(None, max_length=100)
    algorithm_version: Optional[str] = Field(None, max_length=20)

    @validator('behaviors')
    def validate_behaviors(cls, v):
        if len(v) > 100:
            raise ValueError('Maximum 100 behaviors per batch')
        return v


class BehaviorResponse(BaseModel):
    """Schema for behavior response"""
    id: int
    user_id: int
    news_id: int
    behavior_type: str
    position: Optional[int] = None
    page: int
    context: Optional[Dict[str, Any]] = None
    duration: Optional[float] = None
    scroll_percentage: Optional[float] = None
    read_percentage: Optional[float] = None
    sentiment: Optional[str] = None
    feedback_score: Optional[float] = None
    recommendation_id: Optional[str] = None
    algorithm_version: Optional[str] = None
    ab_test_group: Optional[str] = None
    device_type: Optional[str] = None
    platform: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime
    time_of_day: Optional[int] = None
    day_of_week: Optional[int] = None
    is_valid: bool
    engagement_weight: Optional[float] = None

    class Config:
        from_attributes = True


class BehaviorBatchResponse(BaseModel):
    """Schema for batch behavior tracking response"""
    success: bool
    message: str
    total_processed: int
    total_failed: int
    failed_indices: List[int] = []


class ImpressionRequest(BaseModel):
    """Schema for impression tracking request (simplified)"""
    news_ids: List[int] = Field(..., min_items=1, max_items=50)
    page: int = Field(1, ge=1)
    recommendation_id: Optional[str] = Field(None, max_length=100)


class ClickRequest(BaseModel):
    """Schema for click tracking request"""
    news_id: int
    position: Optional[int] = Field(None, ge=0)
    page: int = Field(1, ge=1)
    recommendation_id: Optional[str] = Field(None, max_length=100)


class ReadRequest(BaseModel):
    """Schema for read tracking request"""
    news_id: int
    duration: float = Field(..., ge=0.0)
    scroll_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    read_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)


class InteractionRequest(BaseModel):
    """Schema for interaction tracking (like, share, bookmark)"""
    news_id: int
    interaction_type: str = Field(..., pattern=r'^(like|share|bookmark|comment)$')
    feedback_text: Optional[str] = Field(None, max_length=1000)


class SessionStartRequest(BaseModel):
    """Schema for session start tracking"""
    device_type: Optional[str] = Field(None, pattern=r'^(mobile|desktop|tablet)$')
    platform: Optional[str] = Field(None, pattern=r'^(web|ios|android)$')


class SessionStartResponse(BaseModel):
    """Schema for session start response"""
    session_id: str
    user_id: int
    started_at: datetime


class BehaviorStatsRequest(BaseModel):
    """Schema for behavior statistics request"""
    user_id: Optional[int] = None
    news_id: Optional[int] = None
    behavior_type: Optional[str] = Field(None, pattern=r'^(impression|click|read|like|share|comment|bookmark)$')
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    group_by: str = Field("day", pattern=r'^(hour|day|week|month)$')


class BehaviorStatsResponse(BaseModel):
    """Schema for behavior statistics response"""
    total_count: int
    unique_users: Optional[int] = None
    unique_news: Optional[int] = None
    avg_duration: Optional[float] = None
    avg_scroll_percentage: Optional[float] = None
    time_series: List[Dict[str, Any]] = []
    top_news: Optional[List[Dict[str, Any]]] = None
    top_categories: Optional[List[Dict[str, Any]]] = None


class EventTrackingRequest(BaseModel):
    """Schema for generic event tracking"""
    event_type: str = Field(..., max_length=50)
    event_data: Dict[str, Any]
    timestamp: Optional[datetime] = None
