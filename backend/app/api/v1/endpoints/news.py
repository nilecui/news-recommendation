"""
News management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Any, Optional

from app.config.database import get_db
from app.models.user import User
from app.schemas.news import NewsResponse, NewsSearchRequest
from app.services.news.news_service import NewsService
from app.services.auth.auth_service import get_current_user, get_optional_current_user

router = APIRouter()


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news_detail(
    news_id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get news detail by ID
    """
    news_service = NewsService(db)
    news = await news_service.get_news_by_id(news_id, current_user.id if current_user else None)

    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )

    return news


@router.get("/category/{category}")
async def get_news_by_category(
    category: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get news by category
    """
    news_service = NewsService(db)
    news_list = await news_service.get_news_by_category(
        category, page, limit, current_user.id if current_user else None
    )
    return news_list


@router.get("/trending")
async def get_trending_news(
    timeframe: str = Query("day", regex="^(hour|day|week)$"),
    category: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get trending news
    """
    news_service = NewsService(db)
    trending_news = await news_service.get_trending_news(
        timeframe, category, limit, current_user.id if current_user else None
    )
    return trending_news


@router.post("/search")
async def search_news(
    search_request: NewsSearchRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Search news
    """
    news_service = NewsService(db)
    search_results = await news_service.search_news(
        search_request, current_user.id if current_user else None
    )
    return search_results


@router.get("/latest")
async def get_latest_news(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get latest news
    """
    news_service = NewsService(db)
    latest_news = await news_service.get_latest_news(
        page, limit, category, current_user.id if current_user else None
    )
    return latest_news


@router.post("/{news_id}/like")
async def like_news(
    news_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Like/unlike news
    """
    news_service = NewsService(db)
    result = await news_service.toggle_like(news_id, current_user.id)
    return result


@router.post("/{news_id}/collect")
async def collect_news(
    news_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Collect/uncollect news
    """
    news_service = NewsService(db)
    result = await news_service.toggle_collect(news_id, current_user.id)
    return result


@router.post("/{news_id}/share")
async def share_news(
    news_id: int,
    platform: str = Query(..., regex="^(wechat|weibo|twitter|facebook)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Record news sharing
    """
    news_service = NewsService(db)
    result = await news_service.record_share(news_id, current_user.id, platform)
    return result