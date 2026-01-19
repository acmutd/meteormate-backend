# Created by Atharva Mishra | 1/8/2026
# ACM MeteorMate | All Rights Reserved

import logging

from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.database import get_db
from backend.models.user_profile import UserProfile
from backend.schemas.user_profile import (
    UserProfileCreate,
    UserProfileResponse,
    UserProfileUpdate,
)
from backend.utils.firebase_auth import get_current_user

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
