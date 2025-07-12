# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.survey import Survey
from app.services.matching_service import MatchingService
from app.utils.firebase_auth import get_current_user
from typing import List

router = APIRouter()


@router.get("/potential")
async def get_potential_matches(
    limit: int = 10, current_user_token=Depends(get_current_user), db: Session = Depends(get_db)
):
    # check if user has completed survey
    user_survey = db.query(Survey).filter(Survey.user_id == current_user_token["uid"]).first()
    if not user_survey:
        raise HTTPException(status_code=400, detail="complete your survey first")

    matching_service = MatchingService(db)
    matches = await matching_service.find_potential_matches(current_user_token["uid"], limit)

    return {"matches": matches}


@router.post("/like/{target_user_id}")
async def like_user(
    target_user_id: str,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    matching_service = MatchingService(db)
    result = await matching_service.like_user(current_user_token["uid"], target_user_id)

    return result


@router.post("/pass/{target_user_id}")
async def pass_user(
    target_user_id: str,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    matching_service = MatchingService(db)
    result = await matching_service.pass_user(current_user_token["uid"], target_user_id)

    return result


@router.get("/mutual")
async def get_mutual_matches(
    current_user_token=Depends(get_current_user), db: Session = Depends(get_db)
):
    matching_service = MatchingService(db)
    matches = await matching_service.get_mutual_matches(current_user_token["uid"])

    return {"matches": matches}
