"""
User behavior tracking endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Any, Optional

from app.config.database import get_db
from app.models.user import User
from app.schemas.tracking import BehaviorBatchRequest, BehaviorBatchResponse
from app.services.tracking.tracking_service import TrackingService
from app.services.auth.dependencies import get_current_user

router = APIRouter()


@router.post("/behaviors", response_model=BehaviorBatchResponse)
async def track_behaviors(
    behavior_data: BehaviorBatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Track user behaviors in batch
    
    Request body should be:
    {
        "behaviors": [
            {
                "news_id": 1,
                "behavior_type": "impression",
                "page": 1,
                "position": 0
            }
        ],
        "session_id": "optional-session-id",
        "device_type": "desktop",
        "platform": "web"
    }
    """
    tracking_service = TrackingService(db)
    result = await tracking_service.track_behaviors_batch(
        user_id=current_user.id,
        batch_request=behavior_data
    )
    return {
        "success": result["success"],
        "message": f"Processed {result['total_processed']} behaviors",
        "total_processed": result["total_processed"],
        "total_failed": result["total_failed"],
        "failed_indices": result["failed_indices"]
    }


@router.post("/impression")
async def track_impression(
    news_id: int = Query(..., description="News ID"),
    position: int = Query(0, description="Position in list"),
    page: int = Query(1, ge=1, description="Page number"),
    recommendation_id: Optional[str] = Query(None, description="Recommendation batch ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Track single news impression
    """
    tracking_service = TrackingService(db)
    result = await tracking_service.track_impression(
        user_id=current_user.id,
        news_ids=[news_id],
        page=page,
        recommendation_id=recommendation_id
    )
    return {"success": True, "impressions_recorded": result}


@router.post("/click")
async def track_click(
    news_id: int = Query(..., description="News ID"),
    position: Optional[int] = Query(None, ge=0, description="Position in list"),
    page: int = Query(1, ge=1, description="Page number"),
    recommendation_id: Optional[str] = Query(None, description="Recommendation batch ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Track news click
    """
    tracking_service = TrackingService(db)
    result = await tracking_service.track_click(
        user_id=current_user.id,
        news_id=news_id,
        position=position,
        page=page,
        recommendation_id=recommendation_id
    )
    return {
        "success": True,
        "behavior_id": result.id,
        "news_id": result.news_id,
        "behavior_type": result.behavior_type
    }


@router.post("/read")
async def track_read(
    news_id: int = Query(..., description="News ID"),
    duration: float = Query(..., ge=0.0, description="Reading duration in seconds"),
    scroll_percentage: Optional[float] = Query(None, ge=0.0, le=100.0, description="Scroll percentage"),
    read_percentage: Optional[float] = Query(None, ge=0.0, le=100.0, description="Read percentage"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Track news reading completion
    """
    tracking_service = TrackingService(db)
    result = await tracking_service.track_read(
        user_id=current_user.id,
        news_id=news_id,
        duration=duration,
        scroll_percentage=scroll_percentage,
        read_percentage=read_percentage
    )
    return {
        "success": True,
        "behavior_id": result.id,
        "news_id": result.news_id,
        "duration": result.duration,
        "read_percentage": result.read_percentage
    }


@router.get("/stats")
async def get_user_behavior_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get user behavior statistics
    """
    tracking_service = TrackingService(db)
    stats = await tracking_service.get_user_behavior_stats(current_user.id)
    return stats