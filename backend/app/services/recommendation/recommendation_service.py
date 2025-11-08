"""
Recommendation service implementation
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import redis.asyncio as aioredis
import json
import uuid
import random

from app.config.settings import settings
from app.models.news import News
from app.models.user import User
from app.models.profile import UserProfile
from app.models.behavior import UserBehavior
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationItem
)


class RecommendationService:
    """
    Recommendation service for generating personalized news recommendations
    """

    def __init__(self, db: Session):
        self.db = db
        self.redis_url = settings.REDIS_URL
        self._redis_pool: Optional[aioredis.Redis] = None
        self.algorithm_version = "v1.0.0"

    async def get_redis(self) -> aioredis.Redis:
        """Get Redis connection from pool"""
        if self._redis_pool is None:
            self._redis_pool = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis_pool

    async def close_redis(self) -> None:
        """Close Redis connection pool"""
        if self._redis_pool is not None:
            await self._redis_pool.close()
            self._redis_pool = None

    # ========== Main Recommendation Methods ==========

    async def get_recommendations(self, user_id: int, request: RecommendationRequest) -> Tuple[List[dict], str]:
        """
        Get personalized recommendations for user
        Multi-strategy recall + ranking
        """
        # Generate unique recommendation ID
        recommendation_id = str(uuid.uuid4())

        # Get user profile
        user_profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

        # Determine if user is cold start
        is_cold_start = not user_profile or user_profile.is_cold_start_user

        if is_cold_start:
            # Cold start: use hot + category-based recommendations
            candidates = await self._cold_start_recall(request)
        else:
            # Warm start: use multi-strategy recall
            candidates = await self._multi_strategy_recall(user_id, user_profile, request)

        # Deduplicate candidates by news ID (keep first occurrence with highest priority strategy)
        candidates = self._deduplicate_candidates(candidates)

        # Rank candidates
        ranked_candidates = await self._rank_candidates(user_id, candidates, request)

        # Apply pagination
        start = (request.page - 1) * request.page_size
        end = start + request.page_size
        page_results = ranked_candidates[start:end]

        # Convert to RecommendationItem format
        results = []
        for position, (news, score, strategy) in enumerate(page_results, start=start):
            results.append({
                "news_id": news.id,
                "title": news.title,
                "title_zh": news.title_zh,
                "summary": news.summary,
                "summary_zh": news.summary_zh,
                "source": news.source,
                "author": news.author,
                "image_url": news.image_url,
                "category_id": news.category_id,
                "category_name": news.category.name if news.category else None,
                "tags": news.tags,
                "reading_time": news.reading_time,
                "popularity_score": news.popularity_score,
                "trending_score": news.trending_score,
                "is_featured": news.is_featured,
                "is_breaking": news.is_breaking,
                "published_at": news.published_at,
                "slug": news.slug,
                "position": position,
                "recommendation_score": score,
                "recall_strategy": strategy
            })

        return results, recommendation_id

    # ========== Recall Strategies ==========

    async def _cold_start_recall(self, request: RecommendationRequest) -> List[Tuple[News, str]]:
        """Recall for cold start users (no profile)"""
        candidates = []

        # 1. Hot news (60%)
        hot_news = await self._recall_hot_news(request.category_id, limit=60)
        candidates.extend([(news, "hot") for news in hot_news])

        # 2. Featured news (20%)
        featured_news = await self._recall_featured_news(request.category_id, limit=20)
        candidates.extend([(news, "featured") for news in featured_news])

        # 3. Fresh news (20%)
        fresh_news = await self._recall_fresh_news(request.category_id, limit=20)
        candidates.extend([(news, "fresh") for news in fresh_news])

        return candidates

    async def _multi_strategy_recall(self, user_id: int, user_profile: UserProfile,
                                     request: RecommendationRequest) -> List[Tuple[News, str]]:
        """Multi-strategy recall for users with profile"""
        candidates = []

        # 1. Content-based recall (40%)
        content_news = await self._recall_content_based(user_profile, request.category_id, limit=40)
        candidates.extend([(news, "content") for news in content_news])

        # 2. Collaborative filtering recall (30%) - simplified version
        collab_news = await self._recall_collaborative(user_id, limit=30)
        candidates.extend([(news, "collaborative") for news in collab_news])

        # 3. Hot news (20%)
        hot_news = await self._recall_hot_news(request.category_id, limit=20)
        candidates.extend([(news, "hot") for news in hot_news])

        # 4. Fresh news (exploration, 10%)
        fresh_news = await self._recall_fresh_news(request.category_id, limit=10)
        candidates.extend([(news, "fresh") for news in fresh_news])

        return candidates

    async def _recall_hot_news(self, category_id: Optional[int] = None, limit: int = 20) -> List[News]:
        """Recall hot/trending news"""
        # Try Redis cache first
        cache_key = f"hot_news:{category_id}:{limit}"
        redis = await self.get_redis()
        cached = await redis.get(cache_key)

        if cached:
            news_ids = json.loads(cached)
            return self.db.query(News).filter(News.id.in_(news_ids)).all()

        # Calculate from database
        time_threshold = datetime.now(timezone.utc) - timedelta(days=1)
        query = self.db.query(News).filter(
            and_(
                News.is_published == True,
                News.published_at >= time_threshold
            )
        )

        if category_id:
            query = query.filter(News.category_id == category_id)

        hot_news = query.order_by(desc(News.trending_score)).limit(limit).all()

        # Cache for 5 minutes
        news_ids = [news.id for news in hot_news]
        await redis.setex(cache_key, 300, json.dumps(news_ids))

        return hot_news

    async def _recall_featured_news(self, category_id: Optional[int] = None, limit: int = 10) -> List[News]:
        """Recall featured news"""
        query = self.db.query(News).filter(
            and_(News.is_published == True, News.is_featured == True)
        )

        if category_id:
            query = query.filter(News.category_id == category_id)

        return query.order_by(desc(News.published_at)).limit(limit).all()

    async def _recall_fresh_news(self, category_id: Optional[int] = None, limit: int = 10) -> List[News]:
        """Recall fresh/latest news"""
        query = self.db.query(News).filter(News.is_published == True)

        if category_id:
            query = query.filter(News.category_id == category_id)

        return query.order_by(desc(News.published_at)).limit(limit).all()

    async def _recall_content_based(self, user_profile: UserProfile,
                                    category_id: Optional[int] = None, limit: int = 30) -> List[News]:
        """Content-based recall using user preferences"""
        # Get preferred categories
        preferred_categories = user_profile.preferred_categories or {}

        if not preferred_categories:
            # Fallback to hot news if no preferences
            return await self._recall_hot_news(category_id, limit)

        # Get top preferred category IDs
        top_categories = sorted(preferred_categories.items(), key=lambda x: x[1], reverse=True)[:3]
        category_ids = [int(cat_id) for cat_id, _ in top_categories]

        query = self.db.query(News).filter(
            and_(
                News.is_published == True,
                News.category_id.in_(category_ids)
            )
        )

        if category_id:
            query = query.filter(News.category_id == category_id)

        # Filter by quality threshold
        if user_profile.quality_threshold:
            query = query.filter(News.quality_score >= user_profile.quality_threshold)

        # Order by recency and popularity
        return query.order_by(desc(News.published_at)).limit(limit).all()

    async def _recall_collaborative(self, user_id: int, limit: int = 20) -> List[News]:
        """
        Simplified collaborative filtering
        Find news liked by users with similar behavior
        """
        # Get user's recent positive behaviors (last 30 days)
        time_threshold = datetime.now(timezone.utc) - timedelta(days=30)

        user_behaviors = self.db.query(UserBehavior).filter(
            and_(
                UserBehavior.user_id == user_id,
                UserBehavior.timestamp >= time_threshold,
                UserBehavior.behavior_type.in_(['read', 'like', 'bookmark'])
            )
        ).all()

        if not user_behaviors:
            return []

        # Get news IDs user has interacted with
        user_news_ids = [b.news_id for b in user_behaviors]

        # Find similar users (users who liked the same news)
        similar_user_behaviors = self.db.query(UserBehavior).filter(
            and_(
                UserBehavior.news_id.in_(user_news_ids),
                UserBehavior.user_id != user_id,
                UserBehavior.timestamp >= time_threshold,
                UserBehavior.behavior_type.in_(['read', 'like', 'bookmark'])
            )
        ).limit(1000).all()

        # Count users per news
        user_counts = {}
        for behavior in similar_user_behaviors:
            user_counts[behavior.user_id] = user_counts.get(behavior.user_id, 0) + 1

        # Get top similar users
        top_similar_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        similar_user_ids = [user_id for user_id, _ in top_similar_users]

        # Get news liked by similar users that current user hasn't seen
        recommended_news_behaviors = self.db.query(UserBehavior).filter(
            and_(
                UserBehavior.user_id.in_(similar_user_ids),
                UserBehavior.timestamp >= time_threshold,
                UserBehavior.behavior_type.in_(['read', 'like', 'bookmark']),
                ~UserBehavior.news_id.in_(user_news_ids)  # Exclude already seen
            )
        ).limit(100).all()

        # Count recommendations per news
        news_counts = {}
        for behavior in recommended_news_behaviors:
            news_counts[behavior.news_id] = news_counts.get(behavior.news_id, 0) + 1

        # Get top recommended news IDs
        top_news_ids = [news_id for news_id, _ in
                       sorted(news_counts.items(), key=lambda x: x[1], reverse=True)[:limit]]

        # Fetch news objects
        return self.db.query(News).filter(News.id.in_(top_news_ids)).all()

    # ========== Ranking ==========

    async def _rank_candidates(self, user_id: int, candidates: List[Tuple[News, str]],
                               request: RecommendationRequest) -> List[Tuple[News, float, str]]:
        """
        Rank candidates using simple scoring
        In production, this would use LightGBM or other ML models
        """
        scored_candidates = []

        for news, strategy in candidates:
            # Calculate base score
            score = self._calculate_news_score(news, strategy)

            # Apply diversity penalty (simple version)
            if request.diversify:
                # Penalize news from same category if too many
                category_count = sum(1 for n, _, _ in scored_candidates if n.category_id == news.category_id)
                if category_count >= 3:
                    score *= 0.7

            scored_candidates.append((news, score, strategy))

        # Sort by score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # Apply diversity re-ranking (MMR algorithm simplified)
        if request.diversify:
            scored_candidates = self._apply_diversity_reranking(scored_candidates)

        return scored_candidates

    def _calculate_news_score(self, news: News, strategy: str) -> float:
        """Calculate news score for ranking"""
        # Base scores
        base_score = 0.0

        # Strategy weight
        strategy_weights = {
            "content": 1.0,
            "collaborative": 1.2,
            "hot": 0.8,
            "featured": 0.9,
            "fresh": 0.6
        }
        base_score += strategy_weights.get(strategy, 0.5)

        # Add popularity score
        base_score += news.popularity_score * 0.3

        # Add trending score
        base_score += news.trending_score * 0.3

        # Add quality score
        base_score += news.quality_score * 0.2

        # Time decay (fresher is better)
        # Ensure both datetimes are timezone-aware
        now = datetime.now(timezone.utc)
        published_at = news.published_at
        if published_at.tzinfo is None:
            # If published_at is naive, assume it's UTC
            published_at = published_at.replace(tzinfo=timezone.utc)
        hours_old = (now - published_at).total_seconds() / 3600
        freshness_score = max(0, 1 - (hours_old / 72))  # Decay over 3 days
        base_score += freshness_score * 0.2

        # Boost breaking news
        if news.is_breaking:
            base_score *= 1.5

        # Boost featured news
        if news.is_featured:
            base_score *= 1.2

        return base_score

    def _apply_diversity_reranking(self, scored_candidates: List[Tuple[News, float, str]],
                                   lambda_param: float = 0.5) -> List[Tuple[News, float, str]]:
        """Apply MMR-based diversity re-ranking"""
        if len(scored_candidates) <= 10:
            return scored_candidates

        reranked = []
        remaining = scored_candidates.copy()
        category_counts = {}

        while remaining and len(reranked) < len(scored_candidates):
            best_score = -1
            best_idx = 0

            for idx, (news, score, strategy) in enumerate(remaining):
                # Diversity penalty based on category
                category_penalty = category_counts.get(news.category_id, 0) * 0.1

                # MMR score: balance relevance and diversity
                mmr_score = lambda_param * score - (1 - lambda_param) * category_penalty

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx

            # Add best candidate to reranked list
            selected = remaining.pop(best_idx)
            reranked.append(selected)

            # Update category counts
            news = selected[0]
            category_counts[news.category_id] = category_counts.get(news.category_id, 0) + 1

        return reranked

    def _deduplicate_candidates(self, candidates: List[Tuple[News, str]]) -> List[Tuple[News, str]]:
        """
        Deduplicate candidates by news ID
        Keep the first occurrence (which typically has higher priority strategy)
        """
        seen_news_ids = set()
        deduplicated = []
        
        for news, strategy in candidates:
            if news.id not in seen_news_ids:
                seen_news_ids.add(news.id)
                deduplicated.append((news, strategy))
        
        return deduplicated

    # ========== Utility Methods ==========

    async def get_similar_news(self, news_id: int, limit: int = 10) -> List[News]:
        """Get similar news based on category and tags"""
        reference_news = self.db.query(News).filter(News.id == news_id).first()
        if not reference_news:
            return []

        query = self.db.query(News).filter(
            and_(
                News.id != news_id,
                News.is_published == True,
                News.category_id == reference_news.category_id
            )
        )

        # Prefer news with overlapping tags
        if reference_news.tags:
            query = query.filter(News.tags.overlap(reference_news.tags))

        return query.order_by(desc(News.published_at)).limit(limit).all()
