# Created by Ryan Polasky | 7/12/25
# Updated by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database import get_db
from models.matches import Match
from models.user import User
from services.matching_service import top_k_matches
from utils.firebase_auth import ensure_email_verified
from utils.exceptions import Forbidden, InternalServerError, BadRequest
from database import commit_or_raise

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


@router.get("/potential_matches")
async def get_potential_matches(
    current_user: Annotated[User, Depends(ensure_email_verified)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 10,
):
    if not current_user.survey or not current_user.survey.answers:
        logger.warning(f"User {current_user.id} requested matches without a completed survey")
        raise Forbidden("Complete your survey to see potential matches")

    try:
        matches = top_k_matches(db, current_user.id, k=limit)
        logger.info(f"User {current_user.id} fetched potential matches")

        return {
            "matches": [{
                "uid": match.id,
                "profile": match.profile,
                "survey": match.survey
            } for match in matches]
        }
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching matches for user {current_user.id}: {str(e)}")
        raise InternalServerError("Database error fetching matches")
    except Exception as e:
        logger.error(f"Unexpected error fetching matches for user {current_user.id}: {str(e)}")
        raise InternalServerError("Unexpected error fetching matches")


@router.post("/like/{target_user_id}")
async def like_user(
    target_user_id: str,
    current_user: Annotated[User, Depends(ensure_email_verified)],
    db: Annotated[Session, Depends(get_db)],
):
    uid = current_user.id

    if uid == target_user_id:
        raise BadRequest("You cannot like yourself")

    new_match = Match(user_id=uid, target_user_id=target_user_id, is_like=True)
    db.add(new_match)

    commit_or_raise(db, logger, resource="match", uid=uid, action="create")

    db.refresh(new_match)

    logger.info(f"User {uid} liked User {target_user_id}")
    return {"message": "User liked successfully"}


@router.post("/pass/{target_user_id}")
async def pass_user(
    target_user_id: str,
    current_user: Annotated[User, Depends(ensure_email_verified)],
    db: Annotated[Session, Depends(get_db)],
):
    uid = current_user.id

    if uid == target_user_id:
        raise BadRequest("You cannot pass on yourself")

    new_match = Match(user_id=uid, target_user_id=target_user_id, is_like=False)
    db.add(new_match)

    commit_or_raise(db, logger, resource="match", uid=uid, action="create")

    db.refresh(new_match)

    logger.info(f"User {uid} passed on User {target_user_id}")
    return {"message": "User passed on successfully"}
