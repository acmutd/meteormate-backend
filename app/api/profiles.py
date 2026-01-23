# Created by Atharva Mishra | 1/8/2026
# ACM MeteorMate | All Rights Reserved

import logging

from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.database import get_db
from app.models.user_profile import UserProfile
from app.schemas.user_profile import (
    UserProfileCreate,
    UserProfilePicture,
    UserProfileResponse,
    UserProfileUpdate,
)
from app.utils.firebase_auth import get_current_user
from app.utils.firebase_storage import upload_profile_picture

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


@router.post("/create", response_model=UserProfileResponse)
async def create_user_profile(
    profile_data: UserProfileCreate,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user_token.get("uid")

    try:
        existing = db.get(UserProfile, uid)
        if existing:
            logger.warning(
                f"/api/profiles/create: tried making a user profile that already exists for User {uid}"
            )
            raise HTTPException(status_code=409, detail="User profile already exists.")

        profile = UserProfile(user_id=uid, **profile_data.model_dump())

        db.add(profile)
        db.commit()
        db.refresh(profile)

        logger.info(f"/api/profiles/create: successfully created a new user profile for User {uid}")

        return profile

    except IntegrityError as e:
        db.rollback()

        if "foreign key" in str(e.orig).lower():
            logger.exception(
                f"/api/profiles/create: encountered a foreign key for a user that doesn't exists, recheck firebase and db table for User {uid}"
            )
            raise HTTPException(
                status_code=404,  # not found but with a twist where the db is messed up
                detail="User does not exist.",
            )

        logger.exception(f"/api/profiles/create: conflicting profile exists for User {uid}")
        raise HTTPException(
            status_code=409,  # conflict error different from duplicate
            detail="User profile conflicts with pre-existing profile",
        )

    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            f"/api/profiles/create: Unexpected DB error creating profile for User {uid}"
        )
        raise HTTPException(
            status_code=500,  # internal server error
            detail="Database error creating user profile",
        )


@router.put("/update", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user_token.get("uid")

    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == uid).first()
        if not profile:
            logger.warning(
                f"/api/profiles/update: tried updating profile that doesn't exist for User {uid}"
            )
            raise HTTPException(
                status_code=404, detail="User profile not found"
            )  # not found without a twist

        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)

        db.commit()
        db.refresh(profile)

        logger.info(f"/api/profiles/update: updated user profile for User {uid}")

        return profile

    except IntegrityError as e:
        db.rollback()

        if "foreign key" in str(e.orig).lower():
            logger.exception(
                f"/api/profiles/update: encountered a foreign key for a user that doesn't exists, recheck firebase and db table for User {uid}"
            )
            raise HTTPException(
                status_code=404,  # not found but with a twist where the db is messed up
                detail="User does not exist.",
            )

        logger.exception(f"/api/profiles/update: profile conflicts exist for User {uid}")
        raise HTTPException(
            status_code=409,  # conflict error different from duplicate
            detail="User profile conflicts on db",
        )

    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            f"/api/profiles/update: Unexpected DB error while updating profile for User {uid}"
        )
        raise HTTPException(
            status_code=500,  # internal server error
            detail="Database error updating user profile",
        )


@router.get("/get/{uid}", response_model=UserProfileResponse)
async def get_user_profile(uid: str, db: Session = Depends(get_db)):
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == uid).first()

        if not profile:
            logger.warning(
                f"/api/profiles/get: tried fetching profile that doesn't exist for User {uid}"
            )
            raise HTTPException(
                status_code=404, detail="User profile not found"
            )  # not found without a twist

        return profile

    except IntegrityError as e:
        db.rollback()

        if "foreign key" in str(e.orig).lower():
            logger.exception(
                f"/api/profiles/get: encountered a foreign key for a user that doesn't exists, recheck firebase and db table for User {uid}"
            )
            raise HTTPException(
                status_code=404,  # not found but with a twist where the db is messed up
                detail="User does not exist.",
            )

    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            f"/api/profiles/get: Unexpected DB error while updating profile for User {uid}"
        )

        raise HTTPException(
            status_code=500,  # internal server error
            detail="Database error updating user profile",
        )


@router.post("/upload", response_model=UserProfileResponse)
async def upload_profile_pic(
    image_data: UserProfilePicture,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user_token.get("uid")

    if "," in image_data.base64:
        header = image_data.base64.split(",")[0]
        data = image_data.base64.split(",")[1]
    else:
        raise HTTPException(
            status_code=422,  # unprocessable entity
            detail="image data not in base64 format",
        )

    file_ext = header["data:image/".length:header.indexOf(";base64")
                      ]  # holy syntax, python should js add substring method
    if file_ext not in ["jpeg", "jpg", "png", "webp"]:
        raise HTTPException(
            status_code=422,  # unprocessable entity
            detail="image data not in base64 format",
        )

    blob_path = f"/profile-pictures/{uid}.{file_ext}"

    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == uid).first()
        if not profile:
            logger.warning(
                f"/api/profiles/upload: tried getting profile that doesn't exist for User {uid}"
            )
            raise HTTPException(
                status_code=404, detail="User profile not found"
            )  # not found without a twist

        profile_pic_url = upload_profile_picture(
            data, blob_path, file_ext
        )  # raises http exceptions do not catch

        profile.profile_picture_url.append(profile_pic_url)

        db.commit()
        db.refresh(profile)

        logger.info(f"/api/profiles/upload: updated user profile for User {uid}")

        return profile

    except IntegrityError as e:
        db.rollback()

        if "foreign key" in str(e.orig).lower():
            logger.exception(
                f"/api/profiles/upload: encountered a foreign key for a user that doesn't exists, recheck firebase and db table for User {uid}"
            )
            raise HTTPException(
                status_code=404,  # not found but with a twist where the db is messed up
                detail="User does not exist.",
            )

        logger.exception(f"/api/profiles/upload: profile conflicts exist for User {uid}")
        raise HTTPException(
            status_code=409,  # conflict error different from duplicate
            detail="User profile conflicts on db",
        )

    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            f"/api/profiles/upload: Unexpected DB error while updating profile for User {uid}"
        )
        raise HTTPException(
            status_code=500,  # internal server error
            detail="Database error uploading user profile picture",
        )
