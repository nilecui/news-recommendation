"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app.config.database import get_db
from app.services.auth.auth_service import AuthService
from app.schemas.auth import Token, UserCreate, UserResponse
from app.models.user import User
from app.services.auth.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user
    """
    auth_service = AuthService(db)

    # Check if user already exists
    existing_user = await auth_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user = await auth_service.create_user(user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    auth_service = AuthService(db)

    # Authenticate user
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = await auth_service.create_access_token(user.email)
    refresh_token = await auth_service.create_refresh_token(user.email)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token
    """
    auth_service = AuthService(db)

    # Validate refresh token and create new access token
    token_data = await auth_service.verify_refresh_token(refresh_token)
    user = await auth_service.get_user_by_email(token_data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(user.email)
    new_refresh_token = await auth_service.create_refresh_token(user.email)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Logout user (invalidate token)
    """
    auth_service = AuthService(db)
    await auth_service.logout_user(current_user.email)

    return {"message": "Successfully logged out"}