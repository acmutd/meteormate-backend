# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database import commit_or_raise, get_db, to_db
from exceptions import BadRequest, NotFound
from models.survey import Survey
from models.user import User
from schemas.survey import SurveyCreate, SurveyResponse, SurveyUpdate
from utils.firebase_auth import get_current_user

logger = logging.getLogger("meteormate." + __name__)
router = APIRouter()


@router.post("/", response_model=SurveyResponse)
async def create_survey(
    survey_data: SurveyCreate,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user_token.get("uid")

    user = db.query(User).filter(User.id == uid).first()
    if not user:
        logger.warning(f"Survey creation failed: User {uid} not found in DB")
        raise NotFound("User")

    existing_survey = db.query(Survey).filter(Survey.user_id == uid).first()
    if existing_survey:
        logger.warning(f"User {uid} attempted to create a duplicate survey")
        raise BadRequest("Survey already exists")

    new_survey = Survey(user_id=uid, **survey_data.model_dump())
    db.add(new_survey)

    commit_or_raise(db, logger, resource="survey", uid=uid, action="create")

    db.refresh(new_survey)

    return new_survey


@router.get("/me", response_model=SurveyResponse)
async def get_my_survey(
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user_token.get("uid")

    survey = db.query(Survey).filter(Survey.user_id == uid).first()
    if not survey:
        logger.warning(f"User {uid} requested survey but hasn't created one")
        raise NotFound("Survey")

    logger.info(f"User {uid} fetched their survey")
    return survey


@router.put("/", response_model=SurveyResponse)
async def update_survey(
    survey_data: SurveyUpdate,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = current_user_token.get("uid")

    survey = db.query(Survey).filter(Survey.user_id == uid).first()
    if not survey:
        logger.warning(f"User {uid} attempted to update non-existent survey")
        raise NotFound("Survey")

    update_data = survey_data.model_dump(exclude_unset=True)
    if "answers" in update_data and update_data["answers"] is not None:
        current_answers = survey.answers or {}
        survey.answers = {**current_answers, **update_data["answers"]}
        update_data.pop("answers")

    for field, value in update_data.items():
        setattr(survey, field, value)

    commit_or_raise(db, logger, resource="survey", uid=uid, action="update")

    db.refresh(survey)

    return survey
