"""
Database models package
"""

from app.models.user import User
from app.models.news import News, NewsCategory
from app.models.behavior import UserBehavior
from app.models.profile import UserProfile, UserPreference

__all__ = [
    "User",
    "News",
    "NewsCategory",
    "UserBehavior",
    "UserProfile",
    "UserPreference"
]