# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.database import get_db
from backend.models.user import User
from backend.models.survey import Survey
from backend.services.matching_service import MatchingService
from backend.utils.firebase_auth import get_current_user

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


@router.get("/potential")
async def get_potential_matches(
    limit: int = 10, current_user_token=Depends(get_current_user), db: Session = Depends(get_db)
):
    
    uid = current_user_token.get("uid")
    if not uid:
        logger.error("Token missing 'uid' field in /potential request")
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    try:
        user_survey = db.query(Survey).filter(Survey.user_id == uid).first()
        if not user_survey:
            logger.warning(f"User {uid} attempted to fetch matches without completing survey")
            raise HTTPException(status_code=400, detail="Complete your survey first")

        matching_service = MatchingService(db)
        matches = await matching_service.find_potential_matches(uid, limit)

        logger.info(f"User {uid} fetched {len(matches) if matches else 0} potential matches")
        return {"matches": matches}

    except SQLAlchemyError as e:
        logger.error(f"DB error fetching matches for User {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error fetching matches")
    except Exception as e:
        logger.error(f"Unexpected error in /potential for User {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/like/{target_user_id}")
async def like_user(
    target_user_id: str,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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


@router.get("/mutual")
async def get_mutual_matches(
    current_user_token=Depends(get_current_user), db: Session = Depends(get_db)
):
    uid = current_user_token.get("uid")

    try:
        matching_service = MatchingService(db)
        matches = await matching_service.get_mutual_matches(uid)

        logger.info(f"User {uid} fetched mutual matches")
        return {"matches": matches}

    except SQLAlchemyError as e:
        logger.error(f"DB error fetching mutual matches for User {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error fetching matches")
    except Exception as e:
        logger.error(f"Unexpected error in /mutual for User {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
