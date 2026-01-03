# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.survey import Survey
from app.models.user import User
from app.schemas.survey import SurveyCreate, SurveyResponse, SurveyUpdate
from app.utils.firebase_auth import get_current_user

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/", response_model=SurveyResponse)
async def create_survey(
    survey_data: SurveyCreate,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # check if user exists
    user = db.query(User).filter(User.id == current_user_token["id"]).first()
    if not user:
        logger.error(f"STATUS 404 - User ID {current_user_token["id"]} not found in database")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User ID {current_user_token["id"]} successfully found in \"User\" database")

    # check if survey already exists
    existing_survey = db.query(Survey).filter(Survey.user_id == user.id).first()
    if existing_survey:
        logger.error(f"STATUS 400 - Survey with User ID {user.id} already exists in \"Survey\" database")
        raise HTTPException(status_code=400, detail="Survey already exists")


    new_survey = Survey(user_id=user.id, **survey_data.dict())

    logger.info(f"Successfully created new survey for User ID {current_user_token["id"]}")

    db.add(new_survey)
    db.commit()
    db.refresh(new_survey)

    logger.info(f"Successfully committed new survey for User ID {current_user_token["id"]} to \"Survey\" database")

    return new_survey


@router.get("/me", response_model=SurveyResponse)
async def get_my_survey(
    current_user_token=Depends(get_current_user), db: Session = Depends(get_db)
):
    survey = db.query(Survey).filter(Survey.user_id == current_user_token["uid"]).first()
    if not survey:
        # Not necessary to explicitly mention name of api call, already mentioned in log_requests 
        logger.error(f"STATUS 404 - Survey with User ID {current_user_token["uid"]} not found in \"Survey\" database")
        raise HTTPException(status_code=404, detail="survey not found")
    logger.info(f"User ID {current_user_token["id"]} successfully found in \"Survey\" database")

    return survey


@router.put("/", response_model=SurveyResponse)
async def update_survey(
    survey_data: SurveyUpdate,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    survey = db.query(Survey).filter(Survey.user_id == current_user_token["uid"]).first()
    if not survey:
        logger.error(f"STATUS 404 - Survey with User ID {current_user_token["uid"]} not found in \"Survey\" database")
        raise HTTPException(status_code=404, detail="survey not found")
    logger.info(f"Successfully found survey for User UID {current_user_token["uid"]} in \"Survey\" database")

    update_data = survey_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(survey, field, value)

    logger.info(f"Successfully updated survey for User UID {current_user_token["uid"]}")

    db.commit()
    db.refresh(survey)

    logger.info(f"Successfully committed survey changes for User UID {current_user_token["uid"]} in \"Survey\" database")

    return survey
