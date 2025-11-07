"""
Recommendation schemas for request/response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Schema for recommendation request"""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    category_id: Optional[int] = None
    include_breaking: bool = True
    include_featured: bool = True
    diversify: bool = True
    fresh_ratio: float = Field(0.2, ge=0.0, le=1.0)  # Ratio of fresh content
    explore_ratio: float = Field(0.1, ge=0.0, le=1.0)  # Ratio of exploratory content
    algorithm_version: Optional[str] = None


class RecommendationItem(BaseModel):
    """Schema for a single recommendation item"""
    news_id: int
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
    reading_time: int
    popularity_score: float
    trending_score: float
    is_featured: bool
    is_breaking: bool
    published_at: datetime
    slug: Optional[str] = None

    # Recommendation metadata
    position: int
    recommendation_score: float
    recommendation_reason: Optional[str] = None
    recall_strategy: Optional[str] = None  # 'collaborative', 'content', 'trending', 'fresh'

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """Schema for recommendation response"""
    items: List[RecommendationItem]
    total: int
    page: int
    page_size: int
    recommendation_id: str  # Unique ID for this recommendation batch
    algorithm_version: str
    timestamp: datetime
    has_next: bool
    metadata: Optional[Dict[str, Any]] = None


class PersonalizedRecommendationRequest(BaseModel):
    """Schema for personalized recommendation request"""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    category_id: Optional[int] = None
    exclude_read: bool = True  # Exclude already read news
    min_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    diversify: bool = True
    fresh_ratio: float = Field(0.2, ge=0.0, le=1.0)
    explore_ratio: float = Field(0.1, ge=0.0, le=1.0)


class HotRecommendationRequest(BaseModel):
    """Schema for hot/trending recommendation request"""
    time_range: str = Field("24h", pattern=r'^(1h|6h|24h|7d|30d)$')
    category_id: Optional[int] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class CategoryRecommendationRequest(BaseModel):
    """Schema for category-based recommendation request"""
    category_id: int
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("popularity", pattern=r'^(popularity|trending|published_at|quality)$')


class SimilarNewsRequest(BaseModel):
    """Schema for similar news recommendation request"""
    news_id: int
    limit: int = Field(10, ge=1, le=50)
    min_similarity: float = Field(0.5, ge=0.0, le=1.0)


class SimilarNewsResponse(BaseModel):
    """Schema for similar news response"""
    items: List[RecommendationItem]
    total: int
    reference_news_id: int


class ColdStartRecommendationRequest(BaseModel):
    """Schema for cold start recommendation (new users)"""
    selected_categories: List[int] = Field(..., min_items=1, max_items=10)
    selected_tags: Optional[List[str]] = Field(None, max_items=20)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class RecommendationFeedbackRequest(BaseModel):
    """Schema for recommendation feedback"""
    recommendation_id: str = Field(..., max_length=100)
    news_id: int
    feedback_type: str = Field(..., pattern=r'^(positive|negative|neutral)$')
    reason: Optional[str] = Field(None, max_length=500)


class RecommendationFeedbackResponse(BaseModel):
    """Schema for recommendation feedback response"""
    success: bool
    message: str


class RecommendationStatsResponse(BaseModel):
    """Schema for recommendation statistics"""
    total_recommendations: int
    total_clicks: int
    total_reads: int
    click_through_rate: float
    avg_reading_time: float
    top_categories: List[Dict[str, Any]]
    top_recall_strategies: List[Dict[str, Any]]
    algorithm_performance: Dict[str, Any]


class RecallStrategyWeight(BaseModel):
    """Schema for recall strategy weight configuration"""
    collaborative: float = Field(0.3, ge=0.0, le=1.0)
    content: float = Field(0.3, ge=0.0, le=1.0)
    trending: float = Field(0.2, ge=0.0, le=1.0)
    fresh: float = Field(0.1, ge=0.0, le=1.0)
    explore: float = Field(0.1, ge=0.0, le=1.0)


class RecommendationConfigRequest(BaseModel):
    """Schema for recommendation configuration request"""
    recall_weights: Optional[RecallStrategyWeight] = None
    ranking_model: Optional[str] = Field(None, pattern=r'^(lightgbm|random_forest|neural_network)$')
    diversity_lambda: Optional[float] = Field(None, ge=0.0, le=1.0)
    freshness_decay: Optional[float] = Field(None, ge=0.0, le=1.0)
    min_quality_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)


class RecommendationConfigResponse(BaseModel):
    """Schema for recommendation configuration response"""
    recall_weights: RecallStrategyWeight
    ranking_model: str
    diversity_lambda: float
    freshness_decay: float
    min_quality_threshold: float
    updated_at: datetime


class ABTestConfig(BaseModel):
    """Schema for A/B test configuration"""
    test_name: str = Field(..., max_length=100)
    test_group: str = Field(..., pattern=r'^(control|variant_a|variant_b|variant_c)$')
    config: Dict[str, Any]
    traffic_percentage: float = Field(..., ge=0.0, le=100.0)
    is_active: bool = True


class ABTestAssignment(BaseModel):
    """Schema for A/B test assignment"""
    user_id: int
    test_name: str
    assigned_group: str
    assigned_at: datetime
