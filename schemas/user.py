# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, computed_field, field_validator

from ..schemas.survey import SurveyResponse
from ..schemas.user_profile import UserProfileResponse


class UserCreate(BaseModel):
    email: str
    password: str
    utd_id: str

    @field_validator("email")
    def validate_utd_email(cls, v):
        if not v.endswith("@utdallas.edu"):
            raise ValueError("Email must be a valid @utdallas.edu address")
        return v

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: str
    utd_id: str
    email: str
    created_at: datetime

    survey: Optional[SurveyResponse] = None
    profile: Optional[UserProfileResponse] = None

    @computed_field
    @property
    def survey_done(self) -> bool:
        return self.survey is not None

    @computed_field
    @property
    def profile_created(self) -> bool:
        return self.profile is not None

    class Config:
        from_attributes = True
