"""
News schemas for request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, validator


class NewsCategoryBase(BaseModel):
    """Base schema for news category"""
    name: str = Field(..., max_length=100)
    name_zh: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    sort_order: int = 0
    is_active: bool = True


class NewsCategoryCreate(NewsCategoryBase):
    """Schema for creating a news category"""
    pass


class NewsCategoryUpdate(BaseModel):
    """Schema for updating a news category"""
    name: Optional[str] = Field(None, max_length=100)
    name_zh: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class NewsCategoryResponse(NewsCategoryBase):
    """Schema for news category response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NewsBase(BaseModel):
    """Base schema for news"""
    title: str = Field(..., max_length=500)
    title_zh: Optional[str] = Field(None, max_length=500)
    content: str
    summary: Optional[str] = None
    summary_zh: Optional[str] = None
    source: str = Field(..., max_length=255)
    source_url: str = Field(..., max_length=1000)
    author: Optional[str] = Field(None, max_length=255)
    image_url: Optional[str] = Field(None, max_length=1000)
    video_url: Optional[str] = Field(None, max_length=1000)
    category_id: int
    tags: Optional[List[str]] = None
    language: str = "zh"
    word_count: int = 0
    reading_time: int = 0
    quality_score: float = Field(0.0, ge=0.0, le=1.0)
    sentiment_score: float = Field(0.0, ge=-1.0, le=1.0)
    is_published: bool = True
    is_featured: bool = False
    is_breaking: bool = False
    published_at: datetime
    slug: Optional[str] = Field(None, max_length=500)
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NewsCreate(NewsBase):
    """Schema for creating news"""
    pass


class NewsUpdate(BaseModel):
    """Schema for updating news"""
    title: Optional[str] = Field(None, max_length=500)
    title_zh: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    summary: Optional[str] = None
    summary_zh: Optional[str] = None
    source: Optional[str] = Field(None, max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    image_url: Optional[str] = Field(None, max_length=1000)
    video_url: Optional[str] = Field(None, max_length=1000)
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    language: Optional[str] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_breaking: Optional[bool] = None
    published_at: Optional[datetime] = None
    slug: Optional[str] = Field(None, max_length=500)
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NewsListItem(BaseModel):
    """Schema for news in list view (minimal fields)"""
    id: int
    title: str
    title_zh: Optional[str] = None
    summary: Optional[str] = None
    summary_zh: Optional[str] = None
    source: str
    author: Optional[str] = None
    image_url: Optional[str] = None
    category_id: int
    category_name: Optional[str] = None
    tags: Optional[List[str]] = None
    language: str
    reading_time: int
    view_count: int
    like_count: int
    share_count: int
    comment_count: int
    popularity_score: float
    trending_score: float
    is_featured: bool
    is_breaking: bool
    published_at: datetime
    slug: Optional[str] = None

    class Config:
        from_attributes = True


class NewsResponse(NewsBase):
    """Schema for full news response"""
    id: int
    view_count: int = 0
    like_count: int = 0
    share_count: int = 0
    comment_count: int = 0
    click_through_rate: float = 0.0
    popularity_score: float = 0.0
    trending_score: float = 0.0
    created_at: datetime
    updated_at: datetime
    last_crawled_at: datetime

    # Additional computed fields
    is_trending: Optional[bool] = None
    engagement_rate: Optional[float] = None

    class Config:
        from_attributes = True


class NewsSearchRequest(BaseModel):
    """Schema for news search request"""
    query: Optional[str] = Field(None, min_length=1, max_length=200)
    category_id: Optional[int] = None
    categories: Optional[List[int]] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    sources: Optional[List[str]] = None
    language: Optional[str] = None
    is_featured: Optional[bool] = None
    is_breaking: Optional[bool] = None
    published_after: Optional[datetime] = None
    published_before: Optional[datetime] = None
    min_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    min_popularity_score: Optional[float] = Field(None, ge=0.0)
    sort_by: str = Field("published_at", regex=r'^(published_at|popularity_score|trending_score|created_at|view_count)$')
    sort_order: str = Field("desc", regex=r'^(asc|desc)$')
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class NewsSearchResponse(BaseModel):
    """Schema for news search response"""
    items: List[NewsListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class NewsInteractionRequest(BaseModel):
    """Schema for news interaction (like, bookmark, etc.)"""
    news_id: int


class NewsInteractionResponse(BaseModel):
    """Schema for news interaction response"""
    success: bool
    message: str
    new_count: Optional[int] = None


class NewsFeedRequest(BaseModel):
    """Schema for news feed request (for homepage)"""
    category_id: Optional[int] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    include_breaking: bool = True
    include_featured: bool = True


class NewsTrendingRequest(BaseModel):
    """Schema for trending news request"""
    category_id: Optional[int] = None
    time_range: str = Field("24h", regex=r'^(1h|6h|24h|7d|30d)$')
    limit: int = Field(20, ge=1, le=100)
