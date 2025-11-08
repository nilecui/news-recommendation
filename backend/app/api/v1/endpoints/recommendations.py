"""
Recommendation endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Any, Optional

from app.config.database import get_db
from app.models.user import User
from app.schemas.recommendation import RecommendationResponse, RecommendationRequest
from app.services.recommendation.recommendation_service import RecommendationService
from app.services.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=RecommendationResponse)
async def get_personalized_recommendations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    limit: Optional[int] = Query(None, ge=1, le=50, description="Deprecated: use page_size instead"),
    refresh: bool = Query(False, description="Force refresh recommendations"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get personalized news recommendations for the current user
    """
    recommendation_service = RecommendationService(db)
    
    # Use page_size if provided, otherwise use limit (for backward compatibility)
    actual_page_size = page_size if limit is None else limit
    
    # Create RecommendationRequest
    request = RecommendationRequest(
        page=page,
        page_size=actual_page_size,
        category_id=category_id
    )
    
    recommendations, recommendation_id = await recommendation_service.get_recommendations(
        user_id=current_user.id,
        request=request
    )
    
    # Convert to RecommendationResponse format
    from datetime import datetime
    return {
        "items": recommendations,
        "total": len(recommendations),
        "page": page,
        "page_size": actual_page_size,
        "recommendation_id": recommendation_id,
        "algorithm_version": recommendation_service.algorithm_version,
        "timestamp": datetime.utcnow(),
        "has_next": len(recommendations) == actual_page_size,
        "metadata": None
    }


@router.get("/cold-start")
async def get_cold_start_recommendations(
    categories: Optional[List[int]] = Query(None, description="Preferred category IDs"),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get recommendations for new users (cold start)
    """
    recommendation_service = RecommendationService(db)
    
    # Create request with category filter
    request = RecommendationRequest(
        page=1,
        page_size=limit,
        category_id=categories[0] if categories else None
    )
    
    recommendations, recommendation_id = await recommendation_service.get_recommendations(
        user_id=current_user.id,
        request=request
    )
    
    from datetime import datetime
    return {
        "items": recommendations,
        "total": len(recommendations),
        "page": 1,
        "page_size": limit,
        "recommendation_id": recommendation_id,
        "algorithm_version": recommendation_service.algorithm_version,
        "timestamp": datetime.utcnow(),
        "has_next": False,
        "metadata": {"strategy": "cold_start"}
    }


@router.get("/similar/{news_id}")
async def get_similar_news(
    news_id: int,
    limit: int = Query(10, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get news similar to the given news ID
    """
    recommendation_service = RecommendationService(db)
    similar_news = await recommendation_service.get_similar_news(
        news_id=news_id,
        limit=limit
    )
    
    # Convert to recommendation format
    results = []
    for news in similar_news:
        results.append({
            "news_id": news.id,
            "title": news.title,
            "title_zh": news.title_zh,
            "summary": news.summary,
            "image_url": news.image_url,
            "source": news.source,
            "category_id": news.category_id,
            "published_at": news.published_at.isoformat() if news.published_at else None,
            "recall_strategy": "similar"
        })
    
    return {
        "items": results,
        "total": len(results),
        "reference_news_id": news_id
    }


@router.get("/popular")
async def get_popular_news(
    timeframe: str = Query("24h", pattern="^(1h|6h|24h|7d|30d|hour|day|week)$"),
    category: Optional[str] = None,
    category_id: Optional[int] = Query(None, description="Category ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    limit: Optional[int] = Query(None, ge=1, le=50, description="Deprecated: use page_size instead"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get popular news recommendations
    """
    from app.services.news.news_service import NewsService
    news_service = NewsService(db)
    
    # Use page_size if provided, otherwise use limit (for backward compatibility)
    actual_limit = page_size if limit is None else limit
    
    # Convert timeframe to time_range format
    # Support both old format (hour/day/week) and new format (1h/6h/24h/7d/30d)
    time_range_map = {
        "hour": "1h",
        "day": "24h",
        "week": "7d",
        "1h": "1h",
        "6h": "6h",
        "24h": "24h",
        "7d": "7d",
        "30d": "30d"
    }
    time_range = time_range_map.get(timeframe, "24h")
    
    # Get category_id if category name provided
    if not category_id and category:
        from app.models.news import NewsCategory
        cat = db.query(NewsCategory).filter(NewsCategory.name == category).first()
        if cat:
            category_id = cat.id
    
    # Get enough news for pagination
    popular_news = await news_service.get_trending_news(
        category_id=category_id,
        time_range=time_range,
        limit=actual_limit * page  # Get enough for pagination
    )
    
    # Apply pagination
    start = (page - 1) * actual_limit
    end = start + actual_limit
    paginated_news = popular_news[start:end]
    
    results = []
    for news in paginated_news:
        results.append({
            "news_id": news.id,
            "title": news.title,
            "title_zh": news.title_zh,
            "summary": news.summary,
            "image_url": news.image_url,
            "source": news.source,
            "category_id": news.category_id,
            "trending_score": news.trending_score,
            "published_at": news.published_at.isoformat() if news.published_at else None
        })
    
    return {
        "items": results,
        "total": len(popular_news),
        "page": page,
        "page_size": actual_limit,
        "timeframe": timeframe,
        "has_next": end < len(popular_news)
    }


@router.get("/discovery")
async def get_discovery_recommendations(
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get discovery recommendations (exploration beyond user's interests)
    """
    recommendation_service = RecommendationService(db)
    
    # Use fresh news recall for discovery
    request = RecommendationRequest(
        page=1,
        page_size=limit,
        explore_ratio=0.5,  # Higher exploration ratio
        fresh_ratio=0.5
    )
    
    recommendations, recommendation_id = await recommendation_service.get_recommendations(
        user_id=current_user.id,
        request=request
    )
    
    from datetime import datetime
    return {
        "items": recommendations,
        "total": len(recommendations),
        "page": 1,
        "page_size": limit,
        "recommendation_id": recommendation_id,
        "algorithm_version": recommendation_service.algorithm_version,
        "timestamp": datetime.utcnow(),
        "has_next": False,
        "metadata": {"strategy": "discovery"}
    }


@router.post("/feedback")
async def submit_recommendation_feedback(
    news_id: int,
    feedback_type: str = Query(..., pattern="^(like|dislike|not_interested)$"),
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Submit feedback on recommendations to improve future suggestions
    """
    from app.services.tracking.tracking_service import TrackingService
    tracking_service = TrackingService(db)
    
    # Map feedback type to behavior type
    behavior_type_map = {
        "like": "like",
        "dislike": "click",  # Use click as proxy for negative feedback
        "not_interested": "click"
    }
    
    behavior_type = behavior_type_map.get(feedback_type, "click")
    
    # Record feedback as behavior
    behavior = await tracking_service.track_interaction(
        user_id=current_user.id,
        news_id=news_id,
        interaction_type=behavior_type,
        feedback_text=reason
    )
    
    return {
        "success": True,
        "message": "Feedback recorded successfully",
        "behavior_id": behavior.id
    }