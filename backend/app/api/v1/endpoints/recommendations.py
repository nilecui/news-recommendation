"""
Recommendation endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Any, Optional

from app.config.database import get_db
from app.models.user import User
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation.recommendation_service import RecommendationService
from app.services.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=RecommendationResponse)
async def get_personalized_recommendations(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    refresh: bool = Query(False, description="Force refresh recommendations"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get personalized news recommendations for the current user
    """
    recommendation_service = RecommendationService(db)
    recommendations = await recommendation_service.get_personalized_recommendations(
        user_id=current_user.id,
        page=page,
        limit=limit,
        force_refresh=refresh
    )
    return recommendations


@router.get("/cold-start")
async def get_cold_start_recommendations(
    categories: Optional[List[str]] = Query(None, description="Preferred categories"),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get recommendations for new users (cold start)
    """
    recommendation_service = RecommendationService(db)
    recommendations = await recommendation_service.get_cold_start_recommendations(
        user_id=current_user.id,
        preferred_categories=categories,
        limit=limit
    )
    return recommendations


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
        user_id=current_user.id,
        limit=limit
    )
    return similar_news


@router.get("/popular")
async def get_popular_news(
    timeframe: str = Query("day", pattern="^(hour|day|week)$"),
    category: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get popular news recommendations
    """
    recommendation_service = RecommendationService(db)
    popular_news = await recommendation_service.get_popular_news(
        timeframe=timeframe,
        category=category,
        limit=limit,
        user_id=current_user.id
    )
    return popular_news


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
    discovery_news = await recommendation_service.get_discovery_recommendations(
        user_id=current_user.id,
        limit=limit
    )
    return discovery_news


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
    recommendation_service = RecommendationService(db)
    result = await recommendation_service.submit_feedback(
        user_id=current_user.id,
        news_id=news_id,
        feedback_type=feedback_type,
        reason=reason
    )
    return result