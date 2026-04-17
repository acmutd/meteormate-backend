# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database import get_db
from models.survey import Survey
from services.matching_service import top_k_matches
from utils.firebase_auth import ensure_email_verified
from utils.exceptions import Forbidden, InternalServerError

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
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user_token.get("uid")

    if uid == target_user_id:
        raise HTTPException(status_code=400, detail="You cannot like yourself")

    try:
        matching_service = MatchingService(db)

        result = await matching_service.like_user(uid, target_user_id)

        logger.info(f"User {uid} liked User {target_user_id}")
        return result

    except ValueError as e:
        logger.warning(f"Logic error processing like for User {uid}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error processing like from {uid} -> {target_user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error processing like")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in /like for User {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/pass/{target_user_id}")
async def pass_user(
    target_user_id: str,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user_token.get("uid")

    if uid == target_user_id:
        raise HTTPException(status_code=400, detail="You cannot pass on yourself")

    try:
        matching_service = MatchingService(db)
        result = await matching_service.pass_user(uid, target_user_id)

        logger.info(f"User {uid} passed on User {target_user_id}")
        return result

    except ValueError as e:
        logger.warning(f"Logic error processing pass for User {uid}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error processing pass from {uid} -> {target_user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error processing pass")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in /pass for User {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
