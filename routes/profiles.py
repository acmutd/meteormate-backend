# Created by Atharva Mishra | 1/8/2026
# ACM MeteorMate | All Rights Reserved

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from exceptions import Conflict, NotFound
from utils.firebase_storage import upload_profile_picture

from database import commit_or_raise, get_db
from models.user_profile import UserProfile
from schemas.user_profile import (
    UserProfileCreate,
    UserProfilePicture,
    UserProfileResponse,
    UserProfileUpdate,
)
from utils.firebase_auth import get_current_user

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


@router.post("/create", response_model=UserProfileResponse)
async def create_user_profile(
    profile_data: UserProfileCreate,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user_token.get("uid")

    if db.get(UserProfile, uid):
        logger.warning(f"profile already exists for User {uid}")
        raise Conflict("User profile already exists")

    profile = UserProfile(user_id=uid, **profile_data.model_dump())
    db.add(profile)

    commit_or_raise(db, logger, resource="user profile", uid=uid, action="create")

    db.refresh(profile)
    return profile


@router.put("/update", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user_token.get("uid")

    profile = db.query(UserProfile).filter(UserProfile.user_id == uid).first()

    if not profile:
        logger.warning(f"profile not found for User {uid}")
        raise NotFound("User profile")

    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    commit_or_raise(db, logger, resource="user profile", uid=uid, action="update")

    db.refresh(profile)
    return profile


@router.get("/get/{uid}", response_model=UserProfileResponse)
async def get_user_profile(uid: str, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == uid).first()

    if not profile:
        logger.warning(f"profile not found for User {uid}")
        raise NotFound("User profile")

    return profile


@router.post("/upload", response_model=UserProfileResponse)
async def upload_profile_pic(
    image_data: UserProfilePicture,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user_token.get("uid")

    profile = db.query(UserProfile).filter(UserProfile.user_id == uid).first()
    if not profile:
        logger.warning(f"profile not found for User {uid}")
        raise NotFound("User profile")

    index = len(profile.profile_picture_url)
    blob_path = f"profile-pictures/{uid}-{index}.webp"

    # raises http exceptions do not catch
    profile_pic_url = upload_profile_picture(image_data.image_bytes, blob_path)
    profile.profile_picture_url.append(profile_pic_url)

    commit_or_raise(db, logger, resource="user profile", uid=uid, action="upload")

    db.refresh(profile)

    return profile
