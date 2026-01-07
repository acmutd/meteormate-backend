import logging

from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.database import get_db
from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileCreate, UserProfileResponse
from app.utils.firebase_auth import get_current_user

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


@router.post('/create', response_model=UserProfileResponse)
async def create_user_profile(
    profile_data: UserProfileCreate,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    uid = current_user_token.get("uid")

    try:
        existing = db.get(UserProfile, uid)
        if existing:
            logger.warning(
                f'/api/profiles/create: tried making a user profile that already exists for User {uid}'
            )
            raise HTTPException(status_code=409, detail="User profile already exists.")

        profile = UserProfile(user_id=uid, **profile_data.model_dump())

        db.add(profile)
        db.commit()
        db.refresh(profile)

        logger.info(f'/api/profiles/create: successfully created a new user profile for User {uid}')

        return profile

    except IntegrityError as e:
        db.rollback()

        if "foreign key" in str(e.orig).lower():
            logger.exception(
                f"/api/profiles/create: encountered a foreign key for a user that doesn't exists, recheck firebase and db table for User {uid}"
            )
            raise HTTPException(
                status_code=404,  # not found
                detail="User does not exist."
            )

        logger.exception(f'/api/profiles/create: profile already exists for User {uid}')
        raise HTTPException(
            status_code=409,  # duplicate (error code is called conflict)
            detail="User profile already exists."
        )

    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            f"/api/profiles/create: Unexpected DB error creating profile for User {uid}"
        )
        raise HTTPException(
            status_code=500,  # internal server error
            detail="Database error creating user profile"
        )
