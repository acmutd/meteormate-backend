# Created by Ryan Polasky | 9/20/25
# ACM MeteorMate | All Rights Reserved

from typing import Optional, Literal, Self
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator
from validation_config import *

Gender = Literal["female", "male", "non_binary", "prefer_not_to_say", "other"]
Classification = Literal["freshman", "sophomore", "junior", "senior", "graduate"]


class UserProfileCreate(BaseModel):
    user_id: str
    gender: Optional[Gender] = None
    major: Optional[str] = None
    classification: Optional[Classification] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    first_name: str
    last_name: str
    age: int

    class Config:
        from_attributes = True
    
    @field_validator("first_name")
    def validate_first_name(cls, first_name) -> Self:
        if first_name > FIRST_NAME_MAX_LEN or first_name < FIRST_NAME_MIN_LEN:
            raise ValueError(f"User's first name must be between {FIRST_NAME_MIN_LEN} and {FIRST_NAME_MAX_LEN} characters (inclusive)")
        if any(not char.isalpha() for char in first_name):
            raise ValueError(f"User's first name cannot contain any numbers or special characters")
        return first_name

    @field_validator("last_name")
    def validate_last_name(cls, last_name) -> str:
        if last_name > LAST_NAME_MAX_LEN or last_name < LAST_NAME_MIN_LEN:
            raise ValueError(f"User's last name must be between {LAST_NAME_MIN_LEN} and {LAST_NAME_MAX_LEN} characters (inclusive)")
        if any(not char.isalpha() for char in last_name):
            raise ValueError(f"User's first name cannot contain any numbers or special characters")
        return last_name

    @field_validator("gender")
    


class UserProfileUpdate(BaseModel):
    gender: Optional[Gender] = None
    major: Optional[str] = None
    classification: Optional[Classification] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    first_name: str
    last_name: str
    age: int

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    user_id: str
    gender: Optional[Gender] = None
    major: Optional[str] = None
    classification: Optional[Classification] = None
    created_at: datetime
    updated_at: datetime
    first_name: str
    last_name: str
    age: int

    class Config:
        from_attributes = True
