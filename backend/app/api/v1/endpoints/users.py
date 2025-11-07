"""
User management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.config.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserProfileResponse, UserProfileUpdate
from app.services.user.user_service import UserService
from app.services.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user information
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current user information
    """
    user_service = UserService(db)
    updated_user = await user_service.update_user(current_user.id, user_data)
    return updated_user


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get current user profile with preferences
    """
    user_service = UserService(db)
    profile = await user_service.get_user_profile(current_user.id)
    if not profile:
        # Create profile if it doesn't exist
        profile = await user_service.create_user_profile(current_user.id)
    return profile


@router.put("/me/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update user profile and preferences
    """
    user_service = UserService(db)
    updated_profile = await user_service.update_user_profile(current_user.id, profile_data)
    return updated_profile


@router.get("/me/history")
async def get_reading_history(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get user's reading history
    """
    user_service = UserService(db)
    history = await user_service.get_reading_history(current_user.id, page, limit)
    return history


@router.get("/me/collections")
async def get_user_collections(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get user's collected/bookmarked news
    """
    user_service = UserService(db)
    collections = await user_service.get_user_collections(current_user.id, page, limit)
    return collections


@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete user account
    """
    user_service = UserService(db)
    await user_service.delete_user(current_user.id)
    return {"message": "Account deleted successfully"}