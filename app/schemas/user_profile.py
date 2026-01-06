# Created by Ryan Polasky | 9/20/25
# ACM MeteorMate | All Rights Reserved

from typing import Optional, Literal
from datetime import datetime, date
from pydantic import BaseModel

Gender = Literal["female", "male", "non_binary", "prefer_not_to_say", "other"]
Classification = Literal["freshman", "sophomore", "junior", "senior", "graduate"]


class UserProfileCreate(BaseModel):
    user_id: str
    gender: Optional[Gender] = None
    major: Optional[str] = None
    classification: Optional[Classification] = None
    llc: Optional[bool] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    gender: Optional[Gender] = None
    major: Optional[str] = None
    classification: Optional[Classification] = None
    llc: Optional[bool] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    user_id: str
    gender: Optional[Gender] = None
    major: Optional[str] = None
    classification: Optional[Classification] = None
    llc: Optional[bool] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
