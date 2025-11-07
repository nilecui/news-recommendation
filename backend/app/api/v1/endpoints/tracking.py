"""
User behavior tracking endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.config.database import get_db
from app.models.user import User
from app.schemas.tracking import BehaviorBatchRequest, BehaviorResponse
from app.services.tracking.tracking_service import TrackingService
from app.services.auth.dependencies import get_current_user

router = APIRouter()


@router.post("/behaviors", response_model=BehaviorResponse)
async def track_behaviors(
    behavior_data: BehaviorBatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Track user behaviors in batch
    """
    tracking_service = TrackingService(db)

    # Validate that all behaviors belong to the current user
    for behavior in behavior_data.behaviors:
        if behavior.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot track behaviors for other users"
            )

    result = await tracking_service.track_behaviors(behavior_data.behaviors)
    return result


@router.post("/impression")
async def track_impression(
    news_id: int,
    position: int,
    context: dict = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Track single news impression
    """
    tracking_service = TrackingService(db)
    result = await tracking_service.track_impression(
        user_id=current_user.id,
        news_id=news_id,
        position=position,
        context=context or {}
    )
    return result


@router.post("/click")
async def track_click(
    news_id: int,
    position: int,
    context: dict = None,
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
        context=context or {}
    )
    return result


@router.post("/read")
async def track_read(
    news_id: int,
    duration: int,
    scroll_percentage: float = None,
    context: dict = None,
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
        context=context or {}
    )
    return result


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