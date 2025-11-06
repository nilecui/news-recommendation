"""
User behavior model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class UserBehavior(Base):
    """
    User behavior tracking model for recommendation training
    """
    __tablename__ = "user_behaviors"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False, index=True)

    # Behavior type
    behavior_type = Column(String(50), nullable=False, index=True)  # 'impression', 'click', 'read', 'like', 'share', 'comment', 'bookmark'

    # Behavior context
    position = Column(Integer, nullable=True)  # Position in recommendation list
    page = Column(Integer, default=1)  # Page number
    context = Column(JSON, nullable=True)  # Additional context (device, location, time, etc.)

    # Duration and completion (for reading behaviors)
    duration = Column(Float, nullable=True)  # Duration in seconds
    scroll_percentage = Column(Float, nullable=True)  # Scroll completion (0-100)
    read_percentage = Column(Float, nullable=True)  # Estimated read percentage

    # Sentiment and feedback
    sentiment = Column(String(20), nullable=True)  # 'positive', 'negative', 'neutral'
    feedback_score = Column(Float, nullable=True)  # User feedback score (1-5)
    feedback_text = Column(String(1000), nullable=True)  # User feedback text

    # Recommendation context
    recommendation_id = Column(String(100), nullable=True)  # ID of recommendation batch
    algorithm_version = Column(String(20), nullable=True)  # Which algorithm generated this recommendation
    ab_test_group = Column(String(20), nullable=True)  # A/B test group

    # Device and session information
    device_type = Column(String(50), nullable=True)  # 'mobile', 'desktop', 'tablet'
    platform = Column(String(50), nullable=True)  # 'web', 'ios', 'android'
    session_id = Column(String(100), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)

    # Geographic information
    country = Column(String(2), nullable=True)  # ISO 3166-1 alpha-2
    city = Column(String(100), nullable=True)
    timezone = Column(String(50), nullable=True)

    # Timing
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    time_of_day = Column(Integer, nullable=True)  # Hour of day (0-23)
    day_of_week = Column(Integer, nullable=True)  # Day of week (0-6)

    # Quality indicators
    is_valid = Column(Boolean, default=True)  # Whether this behavior is valid for training
    is_bot = Column(Boolean, default=False)  # Whether this appears to be bot traffic
    confidence = Column(Float, default=1.0)  # Confidence in this behavior data (0-1)

    # Processing flags
    is_processed = Column(Boolean, default=False)  # Whether processed by ML pipeline
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="behaviors")
    news = relationship("News", back_populates="behaviors")

    def __repr__(self):
        return f"<UserBehavior(id={self.id}, user_id={self.user_id}, news_id={self.news_id}, type={self.behavior_type})>"

    @property
    def is_positive_feedback(self):
        """Check if this behavior indicates positive user feedback"""
        positive_behaviors = {'click', 'read', 'like', 'share', 'bookmark'}
        return self.behavior_type in positive_behaviors

    @property
    def is_engagement(self):
        """Check if this behavior represents meaningful engagement"""
        engagement_behaviors = {'read', 'like', 'share', 'comment', 'bookmark'}
        return self.behavior_type in engagement_behaviors

    @property
    def engagement_weight(self):
        """Calculate weight for this behavior in recommendation algorithms"""
        weights = {
            'impression': 0.1,
            'click': 1.0,
            'read': 2.0,
            'like': 3.0,
            'share': 4.0,
            'comment': 3.5,
            'bookmark': 3.0
        }
        base_weight = weights.get(self.behavior_type, 0.1)

        # Apply duration multiplier for reading behaviors
        if self.behavior_type == 'read' and self.duration:
            if self.duration > 300:  # 5+ minutes
                return base_weight * 2.0
            elif self.duration > 120:  # 2+ minutes
                return base_weight * 1.5
            elif self.duration < 10:  # < 10 seconds (bounce)
                return base_weight * 0.3

        # Apply scroll percentage multiplier
        if self.read_percentage:
            if self.read_percentage > 80:
                return base_weight * 1.5
            elif self.read_percentage < 20:
                return base_weight * 0.5

        return base_weight

    def to_dict(self):
        """Convert behavior object to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "news_id": self.news_id,
            "behavior_type": self.behavior_type,
            "position": self.position,
            "page": self.page,
            "context": self.context,
            "duration": self.duration,
            "scroll_percentage": self.scroll_percentage,
            "read_percentage": self.read_percentage,
            "sentiment": self.sentiment,
            "feedback_score": self.feedback_score,
            "recommendation_id": self.recommendation_id,
            "device_type": self.device_type,
            "platform": self.platform,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "time_of_day": self.time_of_day,
            "day_of_week": self.day_of_week,
            "is_valid": self.is_valid,
            "engagement_weight": self.engagement_weight
        }