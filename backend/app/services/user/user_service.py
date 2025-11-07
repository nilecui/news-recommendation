"""
User service implementation
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.profile import UserProfile, UserPreference
from app.models.behavior import UserBehavior
from app.models.news import News
from app.schemas.user import (
    UserUpdate,
    UserProfileUpdate,
    UserPreferenceCreate,
    UserPreferenceUpdate,
    UserRecommendationPreferences
)


class UserService:
    """
    User service for managing user accounts and profiles
    """

    def __init__(self, db: Session):
        self.db = db

    # ========== User Operations ==========

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)

        return user

    async def delete_user(self, user_id: int) -> bool:
        """Delete user account"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True

    async def activate_user(self, user_id: int) -> Optional[User]:
        """Activate user account"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.is_active = True
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)

        return user

    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate user account"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.is_active = False
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)

        return user

    async def verify_user(self, user_id: int) -> Optional[User]:
        """Verify user email"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.is_verified = True
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)

        return user

    # ========== User Profile Operations ==========

    async def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile"""
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    async def create_user_profile(self, user_id: int) -> UserProfile:
        """Create user profile (called after user registration)"""
        # Check if profile already exists
        existing = await self.get_user_profile(user_id)
        if existing:
            return existing

        profile = UserProfile(user_id=user_id)
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)

        return profile

    async def update_user_profile(self, user_id: int, profile_data: UserProfileUpdate) -> Optional[UserProfile]:
        """Update user profile"""
        profile = await self.get_user_profile(user_id)
        if not profile:
            # Create profile if it doesn't exist
            profile = await self.create_user_profile(user_id)

        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)

        profile.updated_at = datetime.utcnow()
        profile.last_profile_update = datetime.utcnow()
        self.db.commit()
        self.db.refresh(profile)

        return profile

    async def setup_user_preferences(self, user_id: int, preferences: UserRecommendationPreferences) -> UserProfile:
        """Setup initial user preferences (onboarding)"""
        profile = await self.get_user_profile(user_id)
        if not profile:
            profile = await self.create_user_profile(user_id)

        # Convert categories list to preference dict
        category_prefs = {str(cat_id): 1.0 for cat_id in preferences.categories}

        # Convert tags list to preference dict
        tag_prefs = None
        if preferences.tags:
            tag_prefs = {tag: 1.0 for tag in preferences.tags}

        # Convert sources list to preference dict
        source_prefs = None
        if preferences.preferred_sources:
            source_prefs = {source: 1.0 for source in preferences.preferred_sources}

        # Update profile
        profile.preferred_categories = category_prefs
        if tag_prefs:
            profile.preferred_tags = tag_prefs
        if source_prefs:
            profile.preferred_sources = source_prefs

        profile.preferred_article_length = preferences.article_length
        profile.diversity_preference = preferences.diversity_preference
        profile.novelty_preference = preferences.novelty_preference
        profile.updated_at = datetime.utcnow()
        profile.last_profile_update = datetime.utcnow()
        profile.profile_confidence = 0.5  # Initial confidence after explicit setup

        self.db.commit()
        self.db.refresh(profile)

        return profile

    # ========== User Preference Operations ==========

    async def get_user_preferences(self, user_id: int, preference_type: Optional[str] = None) -> List[UserPreference]:
        """Get user preferences"""
        profile = await self.get_user_profile(user_id)
        if not profile:
            return []

        query = self.db.query(UserPreference).filter(UserPreference.profile_id == profile.id)

        if preference_type:
            query = query.filter(UserPreference.preference_type == preference_type)

        return query.all()

    async def create_user_preference(self, user_id: int, pref_data: UserPreferenceCreate) -> UserPreference:
        """Create user preference"""
        profile = await self.get_user_profile(user_id)
        if not profile:
            profile = await self.create_user_profile(user_id)

        # Check if preference already exists
        existing = self.db.query(UserPreference).filter(
            UserPreference.profile_id == profile.id,
            UserPreference.preference_type == pref_data.preference_type,
            UserPreference.preference_key == pref_data.preference_key
        ).first()

        if existing:
            # Update existing preference
            existing.preference_value = pref_data.preference_value
            existing.confidence = pref_data.confidence
            existing.weight = pref_data.weight
            existing.updated_at = datetime.utcnow()
            existing.last_seen = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing

        # Create new preference
        preference = UserPreference(
            profile_id=profile.id,
            **pref_data.model_dump()
        )
        self.db.add(preference)
        self.db.commit()
        self.db.refresh(preference)

        return preference

    async def update_user_preference(self, user_id: int, preference_id: int,
                                     pref_data: UserPreferenceUpdate) -> Optional[UserPreference]:
        """Update user preference"""
        profile = await self.get_user_profile(user_id)
        if not profile:
            return None

        preference = self.db.query(UserPreference).filter(
            UserPreference.id == preference_id,
            UserPreference.profile_id == profile.id
        ).first()

        if not preference:
            return None

        update_data = pref_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preference, field, value)

        preference.updated_at = datetime.utcnow()
        preference.last_seen = datetime.utcnow()
        self.db.commit()
        self.db.refresh(preference)

        return preference

    async def delete_user_preference(self, user_id: int, preference_id: int) -> bool:
        """Delete user preference"""
        profile = await self.get_user_profile(user_id)
        if not profile:
            return False

        preference = self.db.query(UserPreference).filter(
            UserPreference.id == preference_id,
            UserPreference.profile_id == profile.id
        ).first()

        if not preference:
            return False

        self.db.delete(preference)
        self.db.commit()
        return True

    # ========== User Statistics ==========

    async def get_user_stats(self, user_id: int) -> dict:
        """Get user statistics"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return {}

        profile = await self.get_user_profile(user_id)

        return {
            "total_reading_count": user.reading_count,
            "total_like_count": user.like_count,
            "total_share_count": user.share_count,
            "last_login_at": user.last_login_at,
            "member_since": user.created_at,
            "profile_completeness": profile.profile_completeness if profile else 0.0,
            "is_cold_start_user": profile.is_cold_start_user if profile else True
        }

    # ========== User Reading History and Collections ==========

    async def get_reading_history(self, user_id: int, page: int = 1, limit: int = 20) -> dict:
        """Get user's reading history"""
        offset = (page - 1) * limit
        
        # Get reading behaviors (behavior_type = 'read')
        behaviors = self.db.query(UserBehavior).filter(
            UserBehavior.user_id == user_id,
            UserBehavior.behavior_type == 'read'
        ).order_by(UserBehavior.timestamp.desc()).offset(offset).limit(limit).all()
        
        total = self.db.query(UserBehavior).filter(
            UserBehavior.user_id == user_id,
            UserBehavior.behavior_type == 'read'
        ).count()
        
        # Get news details for each behavior
        history_items = []
        for behavior in behaviors:
            news = self.db.query(News).filter(News.id == behavior.news_id).first()
            if news:
                history_items.append({
                    "news_id": news.id,
                    "title": news.title,
                    "title_zh": news.title_zh,
                    "summary": news.summary,
                    "image_url": news.image_url,
                    "source": news.source,
                    "category_id": news.category_id,
                    "published_at": news.published_at.isoformat() if news.published_at else None,
                    "read_at": behavior.timestamp.isoformat() if behavior.timestamp else None,
                    "duration": behavior.duration,
                    "read_percentage": behavior.read_percentage,
                    "scroll_percentage": behavior.scroll_percentage
                })
        
        return {
            "items": history_items,
            "total": total,
            "page": page,
            "page_size": limit,
            "has_next": offset + limit < total
        }

    async def get_user_collections(self, user_id: int, page: int = 1, limit: int = 20) -> dict:
        """Get user's collected/bookmarked news"""
        offset = (page - 1) * limit
        
        # Get bookmark behaviors (behavior_type = 'bookmark')
        behaviors = self.db.query(UserBehavior).filter(
            UserBehavior.user_id == user_id,
            UserBehavior.behavior_type == 'bookmark'
        ).order_by(UserBehavior.timestamp.desc()).offset(offset).limit(limit).all()
        
        total = self.db.query(UserBehavior).filter(
            UserBehavior.user_id == user_id,
            UserBehavior.behavior_type == 'bookmark'
        ).count()
        
        # Get news details for each behavior
        collection_items = []
        for behavior in behaviors:
            news = self.db.query(News).filter(News.id == behavior.news_id).first()
            if news:
                collection_items.append({
                    "news_id": news.id,
                    "title": news.title,
                    "title_zh": news.title_zh,
                    "summary": news.summary,
                    "image_url": news.image_url,
                    "source": news.source,
                    "category_id": news.category_id,
                    "published_at": news.published_at.isoformat() if news.published_at else None,
                    "collected_at": behavior.timestamp.isoformat() if behavior.timestamp else None
                })
        
        return {
            "items": collection_items,
            "total": total,
            "page": page,
            "page_size": limit,
            "has_next": offset + limit < total
        }
