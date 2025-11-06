"""
User model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.config.database import Base


class User(Base):
    """
    User model for authentication and user management
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    # User status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # User information
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    # Demographics (optional)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)  # 'male', 'female', 'other'
    location = Column(String(255), nullable=True)
    language = Column(String(10), default="zh")  # Language preference

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Statistics
    login_count = Column(Integer, default=0)
    reading_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    behaviors = relationship("UserBehavior", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"

    @property
    def is_premium(self):
        """Check if user has premium access (placeholder for future implementation)"""
        return False

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "age": self.age,
            "gender": self.gender,
            "location": self.location,
            "language": self.language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "reading_count": self.reading_count,
            "like_count": self.like_count,
            "share_count": self.share_count,
        }