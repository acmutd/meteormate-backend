# Created by Atharva Mishra | 1/8/2026
# ACM MeteorMate | All Rights Reserved

import logging
from typing import Annotated
from urllib.parse import unquote, urlparse

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import commit_or_raise, get_db
from models.admin import Banlist
from models.user import User
from models.user_profile import UserProfile
from schemas.user_profile import UserProfileCreate, UserProfileDeletePictures, UserProfileResponse, UserProfileUpdate, UserUpdateNotifications
from utils.exceptions import BadRequest, Conflict, Forbidden, NotFound
from utils.firebase_auth import ensure_email_verified
from utils.firebase_storage import delete_profile_picture
from utils.rate_limiters import get_rate_limiter, regular_updates_limiter, sensitive_updates_limiter

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


@router.post(
    "/create",
    response_model=UserProfileResponse,
    dependencies=[sensitive_updates_limiter],
)
async def create_user_profile(
    profile_data: UserProfileCreate,
    current_user: Annotated[User, Depends(ensure_email_verified)],
    db: Annotated[Session, Depends(get_db)],
):
    if current_user.profile:
        logger.warning(f"profile already exists for User {current_user.id}")
        raise Conflict("User profile already exists")

    if len(profile_data.profile_picture_url) != 5:
        logger.warning(f"User {current_user.id} attempted to upload an incorrect number of profile pictures")
        raise BadRequest("Exactly 5 profile pictures must be uploaded")

    profile = UserProfile(user_id=current_user.id, **profile_data.model_dump())
    db.add(profile)

    commit_or_raise(db, logger, resource="user profile", uid=current_user.id, action="create")

    db.refresh(profile)
    return profile


@router.put(
    "/update",
    response_model=UserProfileResponse,
    dependencies=[regular_updates_limiter],
)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: Annotated[User, Depends(ensure_email_verified)],
    db: Annotated[Session, Depends(get_db)],
):
    profile = current_user.profile

    if not profile:
        logger.warning(f"profile not found for User {current_user.id}")
        raise NotFound("User profile")

    if profile_data.profile_picture_url is not None and len(profile_data.profile_picture_url) != 5:
        logger.warning(f"User {current_user.id} attempted to upload an incorrect number of profile pictures")
        raise BadRequest("Exactly 5 profile pictures must be uploaded")

    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    commit_or_raise(db, logger, resource="user profile", uid=current_user.id, action="update")

    db.refresh(profile)
    return profile


@router.get("/get/{uid}", response_model=UserProfileResponse, dependencies=[get_rate_limiter])
async def get_user_profile(uid: str, db: Annotated[Session, Depends(get_db)]):
    profile = db.query(UserProfile).filter(UserProfile.user_id == uid).first()
    if not profile:
        logger.warning(f"profile not found for User {uid}")
        raise NotFound("User profile")

    if db.query(Banlist).filter(Banlist.net_id == uid).first():
        logger.warning(f"User with Net ID {uid} attempted to access profile but is banned")
        raise Forbidden("This user is banned from using this service. If you believe this is a mistake, please contact support.")

    return profile


@router.delete(
    "/delete_pictures",
    response_model=UserProfileResponse,
    dependencies=[regular_updates_limiter],
)
async def delete_profile_pics(
    pictures_to_delete: UserProfileDeletePictures,
    current_user: Annotated[User, Depends(ensure_email_verified)],
    db: Annotated[Session, Depends(get_db)],
):
    uid = current_user.id
    profile = current_user.profile

    if not profile:
        logger.warning(f"profile not found for User {uid}")
        raise NotFound("User profile")
    
    for url in pictures_to_delete.profile_picture_url:
        # this basically parses the url to recognize any params with '?' and any url encodings
        parsed_url = urlparse(url)
        url_path = unquote(parsed_url.path)  # get only the path
        file_name = url_path.split("/")[-1]

        # Remove the picture URL from the list
        if url in profile.profile_picture_url:
            # firebase storage helper don't confuse with endpoint function (also don't catch exceptions from this)
            delete_profile_picture(f"profile_pictures/{uid}/{file_name}")
            
            for i in range(len(profile.profile_picture_url)):
                if profile.profile_picture_url[i] == url:
                    profile.profile_picture_url[i] = "" # set to empty string instead of removing to maintain list length of 5

    commit_or_raise(db, logger, resource="user profile", uid=uid, action="delete pictures")

    db.refresh(profile)

    return profile


@router.post(
    "/update_notifications",
    response_model=UserProfileResponse,
    dependencies=[regular_updates_limiter],
)
async def update_notifications(
    notification_updates: UserUpdateNotifications,
    current_user: Annotated[User, Depends(ensure_email_verified)],
    db: Annotated[Session, Depends(get_db)],
):
    profile = current_user.profile
    uid = current_user.id

    if not profile:
        logger.warning(f"profile not found for User {uid}")
        raise NotFound("User profile")

    if notification_updates.match_notification is not None:
        profile.match_notification = notification_updates.match_notification

    if notification_updates.promotional_notification is not None:
        profile.promotional_notification = notification_updates.promotional_notification

    commit_or_raise(db, logger, resource="user profile", uid=uid, action="update notifications")

    db.refresh(profile)

    return profile
