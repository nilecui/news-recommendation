"""
News service implementation
"""

from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc
from fastapi import HTTPException, status
import redis.asyncio as aioredis
import json

from app.config.settings import settings
from app.models.news import News, NewsCategory
from app.models.behavior import UserBehavior
from app.schemas.news import (
    NewsCreate,
    NewsUpdate,
    NewsSearchRequest,
    NewsListItem,
    NewsResponse,
    NewsCategoryCreate,
    NewsCategoryUpdate
)


class NewsService:
    """
    News service for managing news articles
    """

    def __init__(self, db: Session):
        self.db = db
        self.redis_url = settings.REDIS_URL
        self._redis_pool: Optional[aioredis.Redis] = None

    async def get_redis(self) -> aioredis.Redis:
        """Get Redis connection from pool"""
        if self._redis_pool is None:
            self._redis_pool = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False  # For JSON serialization
            )
        return self._redis_pool

    async def close_redis(self) -> None:
        """Close Redis connection pool"""
        if self._redis_pool is not None:
            await self._redis_pool.close()
            self._redis_pool = None

    # ========== News CRUD Operations ==========

    async def get_news_by_id(self, news_id: int, increment_view: bool = True) -> Optional[News]:
        """Get news by ID"""
        news = self.db.query(News).filter(News.id == news_id).first()

        if news and increment_view:
            # Increment view count
            news.view_count += 1
            self.db.commit()

            # Update view count in Redis for real-time stats
            redis = await self.get_redis()
            await redis.hincrby(f"news_stats:{news_id}", "view_count", 1)

        return news

    async def get_news_by_slug(self, slug: str) -> Optional[News]:
        """Get news by slug"""
        return self.db.query(News).filter(News.slug == slug).first()

    async def create_news(self, news_data: NewsCreate) -> News:
        """Create a new news article"""
        # Generate slug if not provided
        if not news_data.slug:
            slug = self._generate_slug(news_data.title)
        else:
            slug = news_data.slug

        # Check if slug already exists
        existing = await self.get_news_by_slug(slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slug already exists"
            )

        # Create news object
        db_news = News(
            **news_data.model_dump(exclude={'slug'}),
            slug=slug
        )

        self.db.add(db_news)
        self.db.commit()
        self.db.refresh(db_news)

        # Invalidate related caches
        await self._invalidate_news_caches(db_news.category_id)

        return db_news

    async def update_news(self, news_id: int, news_data: NewsUpdate) -> Optional[News]:
        """Update news article"""
        news = await self.get_news_by_id(news_id, increment_view=False)
        if not news:
            return None

        # Update fields
        update_data = news_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(news, field, value)

        news.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(news)

        # Invalidate caches
        await self._invalidate_news_caches(news.category_id)
        redis = await self.get_redis()
        await redis.delete(f"news_detail:{news_id}")

        return news

    async def delete_news(self, news_id: int) -> bool:
        """Delete news article"""
        news = await self.get_news_by_id(news_id, increment_view=False)
        if not news:
            return False

        category_id = news.category_id
        self.db.delete(news)
        self.db.commit()

        # Invalidate caches
        await self._invalidate_news_caches(category_id)
        redis = await self.get_redis()
        await redis.delete(f"news_detail:{news_id}")
        await redis.delete(f"news_stats:{news_id}")

        return True

    # ========== News Query Operations ==========

    async def search_news(self, search_request: NewsSearchRequest) -> Tuple[List[News], int]:
        """Search news with filters and pagination"""
        query = self.db.query(News).filter(News.is_published == True)

        # Apply filters
        if search_request.query:
            search_term = f"%{search_request.query}%"
            query = query.filter(
                or_(
                    News.title.ilike(search_term),
                    News.title_zh.ilike(search_term),
                    News.content.ilike(search_term),
                    News.summary.ilike(search_term)
                )
            )

        if search_request.category_id:
            query = query.filter(News.category_id == search_request.category_id)

        if search_request.categories:
            query = query.filter(News.category_id.in_(search_request.categories))

        if search_request.tags:
            # PostgreSQL array overlap
            query = query.filter(News.tags.overlap(search_request.tags))

        if search_request.source:
            query = query.filter(News.source == search_request.source)

        if search_request.sources:
            query = query.filter(News.source.in_(search_request.sources))

        if search_request.language:
            query = query.filter(News.language == search_request.language)

        if search_request.is_featured is not None:
            query = query.filter(News.is_featured == search_request.is_featured)

        if search_request.is_breaking is not None:
            query = query.filter(News.is_breaking == search_request.is_breaking)

        if search_request.published_after:
            query = query.filter(News.published_at >= search_request.published_after)

        if search_request.published_before:
            query = query.filter(News.published_at <= search_request.published_before)

        if search_request.min_quality_score:
            query = query.filter(News.quality_score >= search_request.min_quality_score)

        if search_request.min_popularity_score:
            query = query.filter(News.popularity_score >= search_request.min_popularity_score)

        # Get total count
        total = query.count()

        # Apply sorting
        if search_request.sort_by == "published_at":
            order_col = News.published_at
        elif search_request.sort_by == "popularity_score":
            order_col = News.popularity_score
        elif search_request.sort_by == "trending_score":
            order_col = News.trending_score
        elif search_request.sort_by == "view_count":
            order_col = News.view_count
        else:
            order_col = News.created_at

        if search_request.sort_order == "desc":
            query = query.order_by(desc(order_col))
        else:
            query = query.order_by(order_col)

        # Apply pagination
        offset = (search_request.page - 1) * search_request.page_size
        news_list = query.offset(offset).limit(search_request.page_size).all()

        return news_list, total

    async def get_trending_news(self, category_id: Optional[int] = None,
                                time_range: str = "24h", limit: int = 20) -> List[News]:
        """Get trending news"""
        # Try cache first
        cache_key = f"trending_news:{category_id}:{time_range}:{limit}"
        redis = await self.get_redis()
        cached = await redis.get(cache_key)

        if cached:
            news_ids = json.loads(cached)
            return self.db.query(News).filter(News.id.in_(news_ids)).all()

        # Calculate time threshold
        from datetime import timezone
        time_thresholds = {
            "1h": timedelta(hours=1),
            "6h": timedelta(hours=6),
            "24h": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        threshold = datetime.now(timezone.utc) - time_thresholds.get(time_range, timedelta(days=1))

        query = self.db.query(News).filter(
            and_(
                News.is_published == True,
                News.published_at >= threshold
            )
        )

        if category_id:
            query = query.filter(News.category_id == category_id)

        news_list = query.order_by(desc(News.trending_score)).limit(limit).all()

        # Cache results for 5 minutes
        news_ids = [news.id for news in news_list]
        await redis.setex(cache_key, 300, json.dumps(news_ids))

        return news_list

    async def get_latest_news(self, category_id: Optional[int] = None, limit: int = 20) -> List[News]:
        """Get latest news"""
        query = self.db.query(News).filter(News.is_published == True)

        if category_id:
            query = query.filter(News.category_id == category_id)

        return query.order_by(desc(News.published_at)).limit(limit).all()

    async def get_featured_news(self, limit: int = 10) -> List[News]:
        """Get featured news"""
        return self.db.query(News).filter(
            and_(News.is_published == True, News.is_featured == True)
        ).order_by(desc(News.published_at)).limit(limit).all()

    async def get_breaking_news(self, limit: int = 5) -> List[News]:
        """Get breaking news"""
        return self.db.query(News).filter(
            and_(News.is_published == True, News.is_breaking == True)
        ).order_by(desc(News.published_at)).limit(limit).all()

    # ========== Category Operations ==========

    async def get_category_by_id(self, category_id: int) -> Optional[NewsCategory]:
        """Get category by ID"""
        return self.db.query(NewsCategory).filter(NewsCategory.id == category_id).first()

    async def get_all_categories(self, include_inactive: bool = False) -> List[NewsCategory]:
        """Get all categories"""
        query = self.db.query(NewsCategory)
        if not include_inactive:
            query = query.filter(NewsCategory.is_active == True)

        return query.order_by(NewsCategory.sort_order).all()

    async def create_category(self, category_data: NewsCategoryCreate) -> NewsCategory:
        """Create a new category"""
        db_category = NewsCategory(**category_data.model_dump())
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    async def update_category(self, category_id: int, category_data: NewsCategoryUpdate) -> Optional[NewsCategory]:
        """Update category"""
        category = await self.get_category_by_id(category_id)
        if not category:
            return None

        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        category.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(category)

        return category

    # ========== Interaction Operations ==========

    async def increment_like(self, news_id: int) -> bool:
        """Increment news like count"""
        news = await self.get_news_by_id(news_id, increment_view=False)
        if not news:
            return False

        news.like_count += 1
        self.db.commit()

        # Update in Redis
        redis = await self.get_redis()
        await redis.hincrby(f"news_stats:{news_id}", "like_count", 1)

        return True

    async def increment_share(self, news_id: int) -> bool:
        """Increment news share count"""
        news = await self.get_news_by_id(news_id, increment_view=False)
        if not news:
            return False

        news.share_count += 1
        self.db.commit()

        # Update in Redis
        redis = await self.get_redis()
        await redis.hincrby(f"news_stats:{news_id}", "share_count", 1)

        return True

    async def toggle_like(self, news_id: int, user_id: int) -> dict:
        """Toggle like status for news (like/unlike)"""
        news = await self.get_news_by_id(news_id, increment_view=False)
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="News not found"
            )

        # Check if user already liked this news
        existing_behavior = self.db.query(UserBehavior).filter(
            UserBehavior.user_id == user_id,
            UserBehavior.news_id == news_id,
            UserBehavior.behavior_type == 'like'
        ).first()

        if existing_behavior:
            # Unlike: delete behavior and decrement count
            self.db.delete(existing_behavior)
            news.like_count = max(0, news.like_count - 1)
            self.db.commit()
            liked = False
        else:
            # Like: create behavior and increment count
            behavior = UserBehavior(
                user_id=user_id,
                news_id=news_id,
                behavior_type='like',
                timestamp=datetime.utcnow()
            )
            self.db.add(behavior)
            news.like_count += 1
            self.db.commit()
            liked = True

        # Update in Redis
        redis = await self.get_redis()
        await redis.hset(f"news_stats:{news_id}", "like_count", news.like_count)

        return {
            "news_id": news_id,
            "liked": liked,
            "like_count": news.like_count
        }

    async def toggle_collect(self, news_id: int, user_id: int) -> dict:
        """Toggle collect/bookmark status for news"""
        news = await self.get_news_by_id(news_id, increment_view=False)
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="News not found"
            )

        # Check if user already collected this news
        existing_behavior = self.db.query(UserBehavior).filter(
            UserBehavior.user_id == user_id,
            UserBehavior.news_id == news_id,
            UserBehavior.behavior_type == 'bookmark'
        ).first()

        if existing_behavior:
            # Uncollect: delete behavior
            self.db.delete(existing_behavior)
            self.db.commit()
            collected = False
        else:
            # Collect: create behavior
            behavior = UserBehavior(
                user_id=user_id,
                news_id=news_id,
                behavior_type='bookmark',
                timestamp=datetime.utcnow()
            )
            self.db.add(behavior)
            self.db.commit()
            collected = True

        return {
            "news_id": news_id,
            "collected": collected,
            "message": "News collected" if collected else "News uncollected"
        }

    async def record_share(self, news_id: int, user_id: int, platform: str) -> dict:
        """Record news sharing"""
        news = await self.get_news_by_id(news_id, increment_view=False)
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="News not found"
            )

        # Create share behavior
        behavior = UserBehavior(
            user_id=user_id,
            news_id=news_id,
            behavior_type='share',
            context={"platform": platform},
            timestamp=datetime.utcnow()
        )
        self.db.add(behavior)

        # Increment share count
        news.share_count += 1
        self.db.commit()

        # Update in Redis
        redis = await self.get_redis()
        await redis.hincrby(f"news_stats:{news_id}", "share_count", 1)

        return {
            "news_id": news_id,
            "platform": platform,
            "share_count": news.share_count,
            "message": "Share recorded successfully"
        }

    # ========== Helper Methods ==========

    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        import re
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug[:100]  # Limit length

        # Add timestamp to ensure uniqueness
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"{slug}-{timestamp}"

    async def _invalidate_news_caches(self, category_id: Optional[int] = None) -> None:
        """Invalidate news-related caches"""
        redis = await self.get_redis()

        # Invalidate trending caches
        pattern = "trending_news:*"
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)

        # Invalidate category-specific caches if provided
        if category_id:
            pattern = f"category_news:{category_id}:*"
            keys = await redis.keys(pattern)
            if keys:
                await redis.delete(*keys)
