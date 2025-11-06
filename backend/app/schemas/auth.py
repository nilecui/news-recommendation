"""
Authentication schemas for request/response validation
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class TokenData(BaseModel):
    """Token data schema"""
    email: Optional[str] = None


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefresh(BaseModel):
    """Token refresh request schema"""
    refresh_token: str


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        if v and len(v) > 100:
            raise ValueError('Full name must be less than 100 characters')
        return v


class UserCreate(UserBase):
    """User creation schema"""
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = None

    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 13 or v > 120):
            raise ValueError('Age must be between 13 and 120')
        return v

    @validator('gender')
    def validate_gender(cls, v):
        if v is not None and v not in ['male', 'female', 'other']:
            raise ValueError('Gender must be male, female, or other')
        return v


class UserResponse(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    language: str
    created_at: str
    last_login_at: Optional[str] = None
    reading_count: int
    like_count: int
    share_count: int

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


class PasswordReset(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


class EmailVerification(BaseModel):
    """Email verification schema"""
    token: str


class UserProfile(BaseModel):
    """Extended user profile schema"""
    preferred_categories: Optional[dict] = None
    preferred_tags: Optional[dict] = None
    preferred_sources: Optional[dict] = None
    blocked_sources: Optional[list] = None
    blocked_keywords: Optional[list] = None
    preferred_language: str = "zh"
    preferred_article_length: str = "medium"
    reading_frequency: str = "medium"
    quality_threshold: float = 0.5
    diversity_preference: float = 0.5
    novelty_preference: float = 0.5
    email_notifications: bool = True
    push_notifications: bool = True
    notification_frequency: str = "daily"
    notification_categories: Optional[list] = None
    data_collection_allowed: bool = True
    personalization_allowed: bool = True
    analytics_sharing_allowed: bool = False
    education_level: Optional[str] = None
    occupation: Optional[str] = None
    interests: Optional[list] = None

    @validator('preferred_article_length')
    def validate_article_length(cls, v):
        if v not in ['short', 'medium', 'long']:
            raise ValueError('Article length must be short, medium, or long')
        return v

    @validator('reading_frequency')
    def validate_reading_frequency(cls, v):
        if v not in ['low', 'medium', 'high']:
            raise ValueError('Reading frequency must be low, medium, or high')
        return v

    @validator('notification_frequency')
    def validate_notification_frequency(cls, v):
        if v not in ['immediate', 'daily', 'weekly']:
            raise ValueError('Notification frequency must be immediate, daily, or weekly')
        return v

    @validator('quality_threshold', 'diversity_preference', 'novelty_preference')
    def validate_preference_scores(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Preference scores must be between 0 and 1')
        return v