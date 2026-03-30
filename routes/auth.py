# Created by Ryan Polasky | 7/12/25
# Updated by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

import logging
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError

from database import commit_or_raise, get_db
from config import settings
from models.admin import Banlist
from models.user import InactivityStage, User
from utils.exceptions import Conflict, Forbidden, InternalServerError
from utils.firebase_auth import ensure_email_verified
from utils.firebase_storage import delete_all_profile_pictures
from schemas.user import UserCreate, UserResponse

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Annotated[Session, Depends(get_db)]):
    if (
        db.query(User).filter((User.utd_id == user_data.net_id)
                              | (User.email == user_data.email)).first()
    ):

        logger.warning("user tried to create an account with an existing email/Net ID in DB")
        raise Conflict("Account already exists")

    if db.query(Banlist).filter(Banlist.net_id == user_data.net_id).first():
        logger.warning(f"User with Net ID {user_data.net_id} attempted to register but is banned")
        raise Forbidden(
            "You are banned from using this service. If you believe this is a mistake, please contact support."
        )

    firebase_user = None

    try:
        firebase_user = auth.create_user(
            email=user_data.email, password=user_data.password, email_verified=False
        )

        new_user = User(id=firebase_user.uid, email=user_data.email, utd_id=user_data.net_id)

        db.add(new_user)

        commit_or_raise(db, logger, resource="user", uid=new_user.id, action="create")

        db.refresh(new_user)
        return new_user

    except Exception:
        if firebase_user is not None:
            try:
                auth.delete_user(firebase_user.uid)
                logger.info(f"rolled back Firebase user {firebase_user.uid} after DB failure")
            except Exception:
                logger.error("failed to rollback Firebase user", exc_info=settings.DEBUG)

        raise  # re-raise the original exception


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: Annotated[User, Depends(ensure_email_verified)], ):
    logger.info(f"User {current_user.id} requested /me")

    return current_user


# more reason to hate YAPF
@router.delete("/delete")
async def delete_user_account(
    current_user: Annotated[User, Depends(ensure_email_verified)],
    db: Annotated[Session, Depends(get_db)],
):
    current_user.pending_deletion = True
    commit_or_raise(db, logger, resource="user", uid=current_user.id, action="mark for deletion")

    try:
        auth.delete_user(current_user.id)
    except (ValueError, FirebaseError) as e:
        logger.error(
            f"Error deleting User {current_user.id} account: {str(e)}",
            exc_info=settings.DEBUG,
        )

        current_user.pending_deletion = False
        commit_or_raise(
            db,
            logger,
            resource="user",
            uid=current_user.id,
            action="unmark for deletion",
        )

        raise InternalServerError("Error deleting account")

    # important part idk how i forgot it first time
    delete_all_profile_pictures(current_user.id)

    db.delete(current_user)

    try:
        commit_or_raise(db, logger, resource="user", uid=current_user.id, action="delete")
    except Exception as e:
        logger.critical(
            f"Failed to delete User {current_user.id} from DB after Firebase deletion (delete during cron): {str(e)}",
            exc_info=settings.DEBUG,
        )

    logger.info(f"User {current_user.id} successfully deleted their account")

    return {"message": "Account deleted successfully"}


@router.get("/activity-ping")
def activity_ping(
    current_user: Annotated[User, Depends(ensure_email_verified)],
    db: Annotated[Session, Depends(get_db)],
):
    current_user.updated_at = datetime.now(timezone.utc)
    current_user.inactivity_notification_stage = None

    commit_or_raise(db, logger, resource="user", uid=current_user.id, action="update")

    return {"status": "ok"}


@router.post("/mark-inactive")
def mark_inactive(
    current_user: Annotated[User, Depends(ensure_email_verified)],
    db: Annotated[Session, Depends(get_db)],
):
    current_user.inactivity_notification_stage = InactivityStage.INACTIVE

    commit_or_raise(db, logger, resource="user", uid=current_user.id, action="mark inactive")

    return {"status": "ok"}
