# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models.survey import Survey
from app.models.user import User
from app.schemas.survey import SurveyCreate, SurveyResponse, SurveyUpdate
from app.utils.firebase_auth import get_current_user

logger = logging.getLogger("meteormate." + __name__)

router = APIRouter()


@router.post("/", response_model=SurveyResponse)
async def create_survey(
    survey_data: SurveyCreate,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    uid = current_user_token.get("uid")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    try:
        user = db.query(User).filter(User.id == uid).first()
        if not user:
            logger.warning(f"Survey creation failed: User {uid} not found in DB")
            raise HTTPException(status_code=404, detail="User not found")

        existing_survey = db.query(Survey).filter(Survey.user_id == uid).first()
        if existing_survey:
            logger.warning(f"User {uid} attempted to create a duplicate survey")
            raise HTTPException(status_code=400, detail="Survey already exists")

    except SQLAlchemyError as e:
        logger.error(f"DB error checking user/survey for {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")

    try:
        new_survey = Survey(user_id=uid, **survey_data.model_dump())
        db.add(new_survey)
        db.commit()
        db.refresh(new_survey)

        logger.info(f"User {uid} successfully created their survey")
        return new_survey

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error creating survey for User {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create survey")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in create_survey for User {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me", response_model=SurveyResponse)
async def get_my_survey(
    current_user_token=Depends(get_current_user), db: Session = Depends(get_db)
):
    uid = current_user_token.get("uid")

    try:
        survey = db.query(Survey).filter(Survey.user_id == uid).first()
        if not survey:
            logger.warning(f"User {uid} requested survey but hasn't created one")
            raise HTTPException(status_code=404, detail="Survey not found")

        logger.info(f"User {uid} fetched their survey")
        return survey

    except SQLAlchemyError as e:
        logger.error(f"DB error fetching survey for User {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error in get_my_survey for User {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/", response_model=SurveyResponse)
async def update_survey(
    survey_data: SurveyUpdate,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    uid = current_user_token.get("uid")

    try:
        survey = db.query(Survey).filter(Survey.user_id == uid).first()
        if not survey:
            logger.warning(f"User {uid} attempted to update non-existent survey")
            raise HTTPException(status_code=404, detail="Survey not found")

        update_data = survey_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(survey, field, value)

        db.commit()
        db.refresh(survey)

        logger.info(f"User {uid} updated their survey")
        return survey

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error updating survey for User {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update survey")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in update_survey for User {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
