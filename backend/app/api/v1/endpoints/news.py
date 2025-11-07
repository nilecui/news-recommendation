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
from app.services.auth.dependencies import get_current_user, get_optional_current_user

router = APIRouter()


# 注意：路由顺序很重要！具体路由（如 /latest, /trending）必须在参数路由（/{news_id}）之前定义

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
    # Convert category name to category_id if needed
    category_id = None
    if category:
        from app.models.news import NewsCategory
        cat = db.query(NewsCategory).filter(NewsCategory.name == category).first()
        if cat:
            category_id = cat.id
    
    latest_news = await news_service.get_latest_news(
        category_id=category_id,
        limit=limit
    )
    
    # Apply pagination manually since service doesn't support it
    start = (page - 1) * limit
    end = start + limit
    paginated_news = latest_news[start:end]
    
    return {
        "items": paginated_news,
        "total": len(latest_news),
        "page": page,
        "page_size": limit
    }


@router.get("/trending")
async def get_trending_news(
    timeframe: str = Query("day", pattern="^(hour|day|week)$"),
    category: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get trending news
    """
    news_service = NewsService(db)
    # Convert timeframe to time_range format
    time_range_map = {
        "hour": "1h",
        "day": "24h",
        "week": "7d"
    }
    time_range = time_range_map.get(timeframe, "24h")
    
    # Convert category name to category_id if needed
    category_id = None
    if category:
        from app.models.news import NewsCategory
        cat = db.query(NewsCategory).filter(NewsCategory.name == category).first()
        if cat:
            category_id = cat.id
    
    trending_news = await news_service.get_trending_news(
        category_id=category_id,
        time_range=time_range,
        limit=limit
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
    search_results = await news_service.search_news(search_request)
    return search_results


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
    # Get category by name
    from app.models.news import NewsCategory
    cat = db.query(NewsCategory).filter(NewsCategory.name == category).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category}' not found"
        )
    
    # Use get_latest_news with category filter
    news_list = await news_service.get_latest_news(
        category_id=cat.id,
        limit=limit * page  # Get enough for pagination
    )
    
    # Apply pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_news = news_list[start:end]
    
    return {
        "items": paginated_news,
        "total": len(news_list),
        "page": page,
        "page_size": limit,
        "category": category
    }


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
    news = await news_service.get_news_by_id(news_id, increment_view=current_user is not None)

    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )

    return news


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
    platform: str = Query(..., pattern="^(wechat|weibo|twitter|facebook)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Record news sharing
    """
    news_service = NewsService(db)
    result = await news_service.record_share(news_id, current_user.id, platform)
    return result