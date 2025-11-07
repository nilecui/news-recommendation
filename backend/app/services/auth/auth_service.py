"""
Authentication service implementation
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import redis.asyncio as aioredis
import json
import hashlib
import bcrypt

from app.config.settings import settings
from app.models.user import User
from app.schemas.auth import TokenData, UserCreate, UserResponse


class AuthService:
    """
    Authentication service for handling user authentication and authorization
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

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash
        
        Uses bcrypt directly to avoid passlib initialization issues.
        For passwords > 72 bytes, pre-hashes with SHA256.
        """
        password_bytes = plain_password.encode('utf-8')
        
        # bcrypt has a 72-byte limit, so pre-hash longer passwords with SHA256
        if len(password_bytes) > 72:
            # Pre-hash with SHA256 before verification (consistent with get_password_hash)
            pre_hashed = hashlib.sha256(password_bytes).hexdigest()
            password_to_check = pre_hashed.encode('utf-8')
        else:
            password_to_check = password_bytes
        
        try:
            return bcrypt.checkpw(password_to_check, hashed_password.encode('utf-8'))
        except Exception:
            return False

    def get_password_hash(self, password: str) -> str:
        """Generate password hash using bcrypt directly
        
        Note: bcrypt has a 72-byte limit. For longer passwords, we use SHA256
        to pre-hash the password before bcrypt, which is a common practice.
        """
        password_bytes = password.encode('utf-8')
        
        # bcrypt has a 72-byte limit, so pre-hash longer passwords with SHA256
        if len(password_bytes) > 72:
            # Pre-hash with SHA256 to handle longer passwords
            password_bytes = hashlib.sha256(password_bytes).hexdigest().encode('utf-8')
        
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if username already exists
        existing_user = await self.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Hash the password
        hashed_password = self.get_password_hash(user_data.password)

        # Create user object
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
        )

        # Save to database
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    def _create_token_internal(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None, token_type: str = "access") -> str:
        """Internal method to create JWT token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            if token_type == "access":
                expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            else:
                expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({"exp": expire, "type": token_type})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def create_access_token(self, email: str) -> str:
        """Create access token for user"""
        return self._create_token_internal(
            data={"sub": email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            token_type="access"
        )

    async def create_refresh_token(self, email: str) -> str:
        """Create refresh token for user"""
        refresh_token = self._create_token_internal(
            data={"sub": email},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            token_type="refresh"
        )

        # Store refresh token in Redis for validation
        redis = await self.get_redis()
        await redis.setex(
            f"refresh_token:{email}",
            settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            refresh_token
        )

        return refresh_token

    async def verify_token(self, token: str, token_type: str = "access") -> Optional[TokenData]:
        """Verify JWT token and return token data"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            token_type_in_token: str = payload.get("type")

            if email is None or token_type_in_token != token_type:
                return None

            token_data = TokenData(email=email)
            return token_data

        except JWTError:
            return None

    async def verify_refresh_token(self, refresh_token: str) -> Optional[TokenData]:
        """Verify refresh token"""
        # First verify JWT signature
        token_data = await self.verify_token(refresh_token, "refresh")
        if not token_data:
            return None

        # Then check if token exists in Redis
        redis = await self.get_redis()
        stored_token = await redis.get(f"refresh_token:{token_data.email}")

        if stored_token != refresh_token:
            return None

        return token_data

    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token"""
        token_data = await self.verify_token(token)
        if token_data is None:
            return None

        user = await self.get_user_by_email(token_data.email)
        if user is None:
            return None

        return user

    async def update_last_login(self, user: User) -> None:
        """Update user's last login timestamp"""
        user.last_login_at = datetime.utcnow()
        user.login_count += 1
        self.db.commit()

    async def logout_user(self, email: str) -> None:
        """Logout user by removing refresh token from Redis"""
        redis = await self.get_redis()
        await redis.delete(f"refresh_token:{email}")

    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        redis = await self.get_redis()
        blacklisted = await redis.exists(f"blacklist:{token}")
        return blacklisted

    async def blacklist_token(self, token: str, expires_delta: Optional[timedelta] = None) -> None:
        """Add token to blacklist"""
        if not expires_delta:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        redis = await self.get_redis()
        await redis.setex(
            f"blacklist:{token}",
            int(expires_delta.total_seconds()),
            "1"
        )

    async def change_password(self, user: User, current_password: str, new_password: str) -> bool:
        """Change user password"""
        if not self.verify_password(current_password, user.hashed_password):
            return False

        user.hashed_password = self.get_password_hash(new_password)
        self.db.commit()

        # Invalidate all refresh tokens for this user
        await self.logout_user(user.email)

        return True

    async def reset_password_request(self, email: str) -> bool:
        """Send password reset request (placeholder)"""
        user = await self.get_user_by_email(email)
        if not user:
            return False

        # TODO: Implement password reset email sending
        # This would generate a reset token and send it via email

        return True

    async def validate_user_session(self, token: str) -> Optional[User]:
        """Validate user session and return user"""
        # Check if token is blacklisted
        if await self.is_token_blacklisted(token):
            return None

        # Get user from token
        user = await self.get_current_user(token)
        if not user or not user.is_active:
            return None

        return user