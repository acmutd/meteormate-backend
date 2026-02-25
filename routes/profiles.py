# Created by Atharva Mishra | 1/8/2026
# ACM MeteorMate | All Rights Reserved

import logging
from typing import Annotated
from urllib.parse import unquote, urlparse
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.user import User
from utils.exceptions import BadRequest, Conflict, NotFound
from utils.firebase_storage import upload_profile_picture, delete_profile_picture

from database import commit_or_raise, get_db
from models.user_profile import UserProfile
from schemas.user_profile import (
    UserProfileCreate,
    UserProfilePicture,
    UserProfileResponse,
    UserProfileUpdate,
    UserUpdateNotifications,
)
from utils.firebase_auth import get_current_user

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


@router.post("/create", response_model=UserProfileResponse)
async def create_user_profile(
    profile_data: UserProfileCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    if current_user.profile:
        logger.warning(f"profile already exists for User {current_user.id}")
        raise Conflict("User profile already exists")

    profile = UserProfile(user_id=current_user.id, **profile_data.model_dump())
    db.add(profile)

    commit_or_raise(db, logger, resource="user profile", uid=current_user.id, action="create")

    db.refresh(profile)
    return profile


@router.put("/update", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    profile = current_user.profile

    if not profile:
        logger.warning(f"profile not found for User {current_user.id}")
        raise NotFound("User profile")

    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    commit_or_raise(db, logger, resource="user profile", uid=current_user.id, action="update")

    db.refresh(profile)
    return profile


@router.get("/get/{uid}", response_model=UserProfileResponse)
async def get_user_profile(uid: str, db: Annotated[Session, Depends(get_db)]):
    profile = db.query(UserProfile).filter(UserProfile.user_id == uid).first()

    if not profile:
        logger.warning(f"profile not found for User {uid}")
        raise NotFound("User profile")

    return profile


@router.post("/upload_picture", response_model=UserProfileResponse)
async def upload_profile_pic(
    image_data: UserProfilePicture,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    profile = current_user.profile
    uid = current_user.id

    if not profile:
        logger.warning(f"profile not found for User {uid}")
        raise NotFound("User profile")

    if profile.profile_picture_url is None:
        profile.profile_picture_url = []

    img_id = str(uuid.uuid4())
    blob_path = f"profile_pictures/{uid}/{img_id}.webp"

    # raises http exceptions do not catch
    profile_pic_url = upload_profile_picture(image_data.image_bytes, blob_path)
    profile.profile_picture_url.append(profile_pic_url)

    commit_or_raise(db, logger, resource="user profile", uid=uid, action="upload")

    db.refresh(profile)

    return profile


@router.delete("/delete_picture/{index}", response_model=UserProfileResponse)
async def delete_profile_pic(
    index: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    uid = current_user.id
    profile = current_user.profile

    if not profile:
        logger.warning(f"profile not found for User {uid}")
        raise NotFound("User profile")

    if index < 0 or index >= len(profile.profile_picture_url):
        logger.warning(f"invalid picture index {index} for User {uid}")
        raise BadRequest("Index out-of-bounds for profile pictures")  # kinda funny ngl

    # this basically parses the url to recognize any params with '?' and any url encodings
    parsed_url = urlparse(profile.profile_picture_url[index])
    url_path = unquote(parsed_url.path)  # get only the path
    file_name = url_path.split("/")[-1]

    # firebase storage helper don't confuse with endpoint function (also don't catch exceptions from this)
    delete_profile_picture(f"profile_pictures/{uid}/{file_name}")

    # Remove the picture URL from the list
    profile.profile_picture_url.pop(index)

    commit_or_raise(db, logger, resource="user profile", uid=uid, action="delete")

    db.refresh(profile)

    return profile


@router.post("/update_notifications", response_model=UserProfileResponse)
async def update_notifications(
    notification_updates: UserUpdateNotifications,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    profile = current_user.profile
    uid = current_user.id

    if not profile:
        logger.warning(f"profile not found for User {uid}")
        raise NotFound("User profile")

    if notification_updates.match_notifications is not None:
        profile.match_notifications = notification_updates.match_notifications

    if notification_updates.promotional_notifications is not None:
        profile.promotional_notifications = (notification_updates.promotional_notifications)

    commit_or_raise(db, logger, resource="user profile", uid=uid, action="update notifications")

    db.refresh(profile)

    return profile
