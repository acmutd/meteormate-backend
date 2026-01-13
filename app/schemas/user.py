# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from typing import Optional, Literal
from datetime import date, datetime
from pydantic import BaseModel, Field, computed_field, field_validator

from app.schemas.survey import SurveyResponse


class UserCreate(BaseModel):
    email: str
    password: str
    utd_id: str

    @field_validator('email')
    def validate_utd_email(cls, v):
        if not v.endswith('@utdallas.edu'):
            raise ValueError('Email must be a valid @utdallas.edu address')
        return v

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: str
    utd_id: str
    email: str
    created_at: datetime

    @field_validator('email')
    def validate_utd_email(cls, v):
        if not v.endswith('@utdallas.edu'):
            raise ValueError('Email must be a valid @utdallas.edu address')
        return v

    class Config:
        from_attributes = True


class UserSurveyResponse(BaseModel):
    user: UserResponse
    survey: Optional[SurveyResponse] = None

    @computed_field
    @property
    def survey_done(self) -> bool:
        return self.survey is not None
