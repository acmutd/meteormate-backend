# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.survey import Survey
from app.models.user import User
from app.schemas.survey import SurveyCreate, SurveyResponse, SurveyUpdate
from app.utils.firebase_auth import get_current_user

router = APIRouter()


@router.post("/", response_model=SurveyResponse)
async def create_survey(
    survey_data: SurveyCreate,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # check if user exists
    user = db.query(User).filter(User.firebase_uid == current_user_token["uid"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    # check if survey already exists
    existing_survey = db.query(Survey).filter(Survey.user_id == user.firebase_uid).first()
    if existing_survey:
        raise HTTPException(status_code=400, detail="survey already exists")

    new_survey = Survey(user_id=user.firebase_uid, **survey_data.dict())

    db.add(new_survey)
    db.commit()
    db.refresh(new_survey)

    return new_survey


@router.get("/me", response_model=SurveyResponse)
async def get_my_survey(
    current_user_token=Depends(get_current_user), db: Session = Depends(get_db)
):
    survey = db.query(Survey).filter(Survey.user_id == current_user_token["uid"]).first()
    if not survey:
        raise HTTPException(status_code=404, detail="survey not found")

    return survey


@router.put("/", response_model=SurveyResponse)
async def update_survey(
    survey_data: SurveyUpdate,
    current_user_token=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    survey = db.query(Survey).filter(Survey.user_id == current_user_token["uid"]).first()
    if not survey:
        raise HTTPException(status_code=404, detail="survey not found")

    update_data = survey_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(survey, field, value)

    db.commit()
    db.refresh(survey)

    return survey
