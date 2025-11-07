"""
User profile and preference models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, ARRAY, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class UserProfile(Base):
    """
    Extended user profile with preferences and behavior analysis
    """
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    # Content preferences
    preferred_categories = Column(JSON, nullable=True)  # Category preferences with weights
    preferred_tags = Column(JSON, nullable=True)  # Tag preferences with weights
    preferred_sources = Column(JSON, nullable=True)  # Source preferences
    blocked_sources = Column(ARRAY(String), nullable=True)  # Blocked news sources
    blocked_keywords = Column(ARRAY(String), nullable=True)  # Blocked keywords

    # Reading preferences
    preferred_language = Column(String(10), default="zh")
    preferred_article_length = Column(String(20), default="medium")  # 'short', 'medium', 'long'
    reading_frequency = Column(String(20), default="medium")  # 'low', 'medium', 'high'

    # Interest profile (ML generated)
    interest_vector = Column(JSON, nullable=True)  # User interest embedding vector
    interest_keywords = Column(JSON, nullable=True)  # Keywords with weights
    interest_categories = Column(JSON, nullable=True)  # Category interests with weights

    # Behavior patterns
    typical_reading_times = Column(JSON, nullable=True)  # Hours when user typically reads
    typical_session_duration = Column(Float, default=5.0)  # Average session duration in minutes
    bounce_rate = Column(Float, default=0.0)  # User's typical bounce rate

    # Content quality preferences
    quality_threshold = Column(Float, default=0.5)  # Minimum quality score preference
    diversity_preference = Column(Float, default=0.5)  # Preference for content diversity (0-1)
    novelty_preference = Column(Float, default=0.5)  # Preference for novel content (0-1)

    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    notification_frequency = Column(String(20), default="daily")  # 'immediate', 'daily', 'weekly'
    notification_categories = Column(ARRAY(String), nullable=True)

    # Privacy settings
    data_collection_allowed = Column(Boolean, default=True)
    personalization_allowed = Column(Boolean, default=True)
    analytics_sharing_allowed = Column(Boolean, default=False)

    # Demographics (enhanced)
    education_level = Column(String(50), nullable=True)
    occupation = Column(String(100), nullable=True)
    interests = Column(ARRAY(String), nullable=True)  # General interests

    # ML model data
    model_version = Column(String(20), nullable=True)  # Last ML model version used
    last_profile_update = Column(DateTime(timezone=True), server_default=func.now())
    profile_confidence = Column(Float, default=0.0)  # Confidence in profile accuracy (0-1)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="profile")
    preferences = relationship("UserPreference", back_populates="profile", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id})>"

    @property
    def is_cold_start_user(self):
        """Check if this is a new user with limited data"""
        return self.profile_confidence < 0.3

    @property
    def profile_completeness(self):
        """Calculate how complete the user profile is"""
        fields = [
            self.preferred_categories,
            self.interest_vector,
            self.typical_reading_times,
            self.education_level,
            self.occupation,
            self.interests
        ]
        filled_fields = sum(1 for field in fields if field is not None)
        return filled_fields / len(fields)


class UserPreference(Base):
    """
    Specific user preferences for different aspects
    """
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)

    # Preference type and value
    preference_type = Column(String(50), nullable=False, index=True)  # 'category', 'source', 'topic', 'author'
    preference_key = Column(String(255), nullable=False, index=True)  # The actual value (e.g., 'technology', 'BBC')
    preference_value = Column(Float, nullable=False, default=0.0)  # Preference score (-1 to 1)

    # Metadata
    source = Column(String(50), nullable=True)  # How this preference was derived ('explicit', 'implicit', 'ml')
    confidence = Column(Float, default=0.0)  # Confidence in this preference (0-1)
    weight = Column(Float, default=1.0)  # Weight for this preference in algorithms

    # Temporal data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_seen = Column(DateTime(timezone=True), nullable=True)  # When this preference was last reinforced

    # Relationships
    profile = relationship("UserProfile", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreference(id={self.id}, type={self.preference_type}, key={self.preference_key}, value={self.preference_value})>"

    @property
    def is_positive_preference(self):
        """Check if this is a positive preference"""
        return self.preference_value > 0

    @property
    def is_strong_preference(self):
        """Check if this is a strong preference"""
        return abs(self.preference_value) > 0.7