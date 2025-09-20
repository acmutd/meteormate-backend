# Created by Ryan Polasky | 9/20/25
# ACM MeteorMate | All Rights Reserved

from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel

Gender = Literal["female", "male", "non_binary", "prefer_not_to_say", "other"]
ClassYear = Literal["freshman", "sophomore", "junior", "senior", "graduate", "other"]


class UserProfileCreate(BaseModel):
    user_id: str
    gender: Optional[Gender] = None
    major: Optional[str] = None
    class_year: Optional[ClassYear] = None
    llc: Optional[bool] = None

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    gender: Optional[Gender] = None
    major: Optional[str] = None
    class_year: Optional[ClassYear] = None
    llc: Optional[bool] = None

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    user_id: str
    gender: Optional[Gender] = None
    major: Optional[str] = None
    class_year: Optional[ClassYear] = None
    llc: Optional[bool] = None
    is_freshman: Optional[bool] = None  # computed in model
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
