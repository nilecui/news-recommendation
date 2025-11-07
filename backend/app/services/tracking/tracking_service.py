"""
Tracking service implementation for user behavior tracking
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import redis.asyncio as aioredis
import json
import uuid

from app.config.settings import settings
from app.models.behavior import UserBehavior
from app.schemas.tracking import (
    BehaviorCreate,
    BehaviorBatchItem,
    BehaviorBatchRequest
)


class TrackingService:
    """
    Tracking service for recording user behaviors
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
                decode_responses=True
            )
        return self._redis_pool

    async def close_redis(self) -> None:
        """Close Redis connection pool"""
        if self._redis_pool is not None:
            await self._redis_pool.close()
            self._redis_pool = None

    # ========== Behavior Tracking ==========

    async def track_behavior(self, user_id: int, behavior_data: BehaviorCreate) -> UserBehavior:
        """Track a single user behavior"""
        timestamp = datetime.utcnow()

        behavior = UserBehavior(
            user_id=user_id,
            **behavior_data.model_dump(),
            timestamp=timestamp,
            time_of_day=timestamp.hour,
            day_of_week=timestamp.weekday()
        )

        self.db.add(behavior)
        self.db.commit()
        self.db.refresh(behavior)

        # Update real-time stats in Redis
        await self._update_realtime_stats(user_id, behavior)

        return behavior

    async def track_behaviors_batch(self, user_id: int, batch_request: BehaviorBatchRequest) -> dict:
        """Track multiple behaviors in batch"""
        processed = 0
        failed = 0
        failed_indices = []

        for idx, behavior_item in enumerate(batch_request.behaviors):
            try:
                timestamp = behavior_item.timestamp or datetime.utcnow()

                behavior = UserBehavior(
                    user_id=user_id,
                    news_id=behavior_item.news_id,
                    behavior_type=behavior_item.behavior_type,
                    position=behavior_item.position,
                    page=behavior_item.page,
                    context=behavior_item.context,
                    duration=behavior_item.duration,
                    scroll_percentage=behavior_item.scroll_percentage,
                    read_percentage=behavior_item.read_percentage,
                    session_id=batch_request.session_id,
                    device_type=batch_request.device_type,
                    platform=batch_request.platform,
                    recommendation_id=batch_request.recommendation_id,
                    algorithm_version=batch_request.algorithm_version,
                    timestamp=timestamp,
                    time_of_day=timestamp.hour,
                    day_of_week=timestamp.weekday()
                )

                self.db.add(behavior)
                processed += 1

                # Update real-time stats
                await self._update_realtime_stats(user_id, behavior)

            except Exception as e:
                failed += 1
                failed_indices.append(idx)
                print(f"Failed to track behavior {idx}: {str(e)}")

        if processed > 0:
            self.db.commit()

        return {
            "success": failed == 0,
            "total_processed": processed,
            "total_failed": failed,
            "failed_indices": failed_indices
        }

    async def track_impression(self, user_id: int, news_ids: List[int],
                               page: int = 1, recommendation_id: Optional[str] = None) -> int:
        """Track news impressions (batch)"""
        timestamp = datetime.utcnow()
        behaviors = []

        for position, news_id in enumerate(news_ids):
            behavior = UserBehavior(
                user_id=user_id,
                news_id=news_id,
                behavior_type="impression",
                position=position,
                page=page,
                recommendation_id=recommendation_id,
                timestamp=timestamp,
                time_of_day=timestamp.hour,
                day_of_week=timestamp.weekday()
            )
            behaviors.append(behavior)

        self.db.bulk_save_objects(behaviors)
        self.db.commit()

        return len(behaviors)

    async def track_click(self, user_id: int, news_id: int, position: Optional[int] = None,
                         page: int = 1, recommendation_id: Optional[str] = None) -> UserBehavior:
        """Track news click"""
        timestamp = datetime.utcnow()

        behavior = UserBehavior(
            user_id=user_id,
            news_id=news_id,
            behavior_type="click",
            position=position,
            page=page,
            recommendation_id=recommendation_id,
            timestamp=timestamp,
            time_of_day=timestamp.hour,
            day_of_week=timestamp.weekday()
        )

        self.db.add(behavior)
        self.db.commit()
        self.db.refresh(behavior)

        # Update Redis hot news
        await self._update_hot_news(news_id)

        return behavior

    async def track_read(self, user_id: int, news_id: int, duration: float,
                        scroll_percentage: Optional[float] = None,
                        read_percentage: Optional[float] = None) -> UserBehavior:
        """Track news reading"""
        timestamp = datetime.utcnow()

        behavior = UserBehavior(
            user_id=user_id,
            news_id=news_id,
            behavior_type="read",
            duration=duration,
            scroll_percentage=scroll_percentage,
            read_percentage=read_percentage,
            timestamp=timestamp,
            time_of_day=timestamp.hour,
            day_of_week=timestamp.weekday()
        )

        self.db.add(behavior)
        self.db.commit()
        self.db.refresh(behavior)

        return behavior

    async def track_interaction(self, user_id: int, news_id: int, interaction_type: str,
                                feedback_text: Optional[str] = None) -> UserBehavior:
        """Track user interaction (like, share, bookmark, comment)"""
        timestamp = datetime.utcnow()

        behavior = UserBehavior(
            user_id=user_id,
            news_id=news_id,
            behavior_type=interaction_type,
            feedback_text=feedback_text,
            timestamp=timestamp,
            time_of_day=timestamp.hour,
            day_of_week=timestamp.weekday()
        )

        self.db.add(behavior)
        self.db.commit()
        self.db.refresh(behavior)

        # Update Redis hot news
        await self._update_hot_news(news_id, weight=2)  # Interactions have higher weight

        return behavior

    # ========== Session Management ==========

    async def create_session(self, user_id: int, device_type: Optional[str] = None,
                            platform: Optional[str] = None) -> str:
        """Create a new user session"""
        session_id = str(uuid.uuid4())

        # Store session in Redis with 1 hour TTL
        redis = await self.get_redis()
        session_data = {
            "user_id": user_id,
            "device_type": device_type or "unknown",
            "platform": platform or "unknown",
            "started_at": datetime.utcnow().isoformat()
        }
        await redis.setex(
            f"session:{session_id}",
            3600,  # 1 hour
            json.dumps(session_data)
        )

        return session_id

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        redis = await self.get_redis()
        session_data = await redis.get(f"session:{session_id}")

        if session_data:
            return json.loads(session_data)
        return None

    # ========== Statistics ==========

    async def get_user_behavior_stats(self, user_id: int, days: int = 30) -> dict:
        """Get user behavior statistics"""
        from datetime import timedelta

        start_date = datetime.utcnow() - timedelta(days=days)

        behaviors = self.db.query(UserBehavior).filter(
            and_(
                UserBehavior.user_id == user_id,
                UserBehavior.timestamp >= start_date
            )
        ).all()

        stats = {
            "total_behaviors": len(behaviors),
            "impressions": len([b for b in behaviors if b.behavior_type == "impression"]),
            "clicks": len([b for b in behaviors if b.behavior_type == "click"]),
            "reads": len([b for b in behaviors if b.behavior_type == "read"]),
            "likes": len([b for b in behaviors if b.behavior_type == "like"]),
            "shares": len([b for b in behaviors if b.behavior_type == "share"]),
            "bookmarks": len([b for b in behaviors if b.behavior_type == "bookmark"])
        }

        # Calculate CTR
        if stats["impressions"] > 0:
            stats["ctr"] = stats["clicks"] / stats["impressions"]
        else:
            stats["ctr"] = 0.0

        # Calculate average reading time
        read_behaviors = [b for b in behaviors if b.behavior_type == "read" and b.duration]
        if read_behaviors:
            stats["avg_reading_time"] = sum(b.duration for b in read_behaviors) / len(read_behaviors)
        else:
            stats["avg_reading_time"] = 0.0

        return stats

    async def get_news_behavior_stats(self, news_id: int) -> dict:
        """Get news behavior statistics"""
        behaviors = self.db.query(UserBehavior).filter(
            UserBehavior.news_id == news_id
        ).all()

        stats = {
            "total_behaviors": len(behaviors),
            "unique_users": len(set(b.user_id for b in behaviors)),
            "impressions": len([b for b in behaviors if b.behavior_type == "impression"]),
            "clicks": len([b for b in behaviors if b.behavior_type == "click"]),
            "reads": len([b for b in behaviors if b.behavior_type == "read"]),
            "likes": len([b for b in behaviors if b.behavior_type == "like"]),
            "shares": len([b for b in behaviors if b.behavior_type == "share"])
        }

        # Calculate CTR
        if stats["impressions"] > 0:
            stats["ctr"] = stats["clicks"] / stats["impressions"]
        else:
            stats["ctr"] = 0.0

        return stats

    # ========== Helper Methods ==========

    async def _update_realtime_stats(self, user_id: int, behavior: UserBehavior) -> None:
        """Update real-time statistics in Redis"""
        redis = await self.get_redis()

        # Update user recent behaviors (keep last 100)
        await redis.lpush(f"user_recent_behaviors:{user_id}", json.dumps({
            "news_id": behavior.news_id,
            "behavior_type": behavior.behavior_type,
            "timestamp": behavior.timestamp.isoformat()
        }))
        await redis.ltrim(f"user_recent_behaviors:{user_id}", 0, 99)

        # Update behavior type counters
        await redis.hincrby(f"user_behavior_counts:{user_id}", behavior.behavior_type, 1)

    async def _update_hot_news(self, news_id: int, weight: int = 1) -> None:
        """Update hot news ranking in Redis"""
        redis = await self.get_redis()

        # Add to hot news sorted set (24h window)
        await redis.zincrby("hot_news_24h", weight, str(news_id))

        # Set expiry on the sorted set (25 hours to be safe)
        await redis.expire("hot_news_24h", 90000)
