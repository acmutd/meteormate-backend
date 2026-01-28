# Created by Ryan Polasky | 9/20/25
# ACM MeteorMate | All Rights Reserved

from typing import List, Optional, Literal, Self
from datetime import datetime, date
from pydantic import BaseModel, field_validator

from config import settings

Gender = Literal["female", "male", "non_binary", "prefer_not_to_say", "other"]
Classification = Literal["freshman", "sophomore", "junior", "senior", "graduate"]


def validate_name(name, min_len, max_len, position):
    if len(name) > settings.FIRST_NAME_MAX_LEN or len(name) < settings.FIRST_NAME_MIN_LEN:
        raise ValueError(f"User's {position} name must be between {min_len} and {max_len} characters (inclusive)")
    if any(not char.isalpha() for char in name):
        raise ValueError(f"User's {position} name cannot contain any numbers or special characters")
    return name


class UserProfileCreate(BaseModel):
    gender: Gender
    major: str
    classification: Classification
    bio: str
    profile_picture_url: Optional[List[str]] = None
    first_name: str
    last_name: str
    age: int

    class Config:
        from_attributes = True

    @field_validator("first_name")
    def validate_first_name(cls, v) -> str:
        return validate_name(v, settings.FIRST_NAME_MIN_LEN, settings.FIRST_NAME_MAX_LEN, "first")

    @field_validator("last_name")
    def validate_last_name(cls, v) -> str:
        return validate_name(v, settings.LAST_NAME_MIN_LEN, settings.LAST_NAME_MAX_LEN, "last")

    @field_validator("age")
    def validate_age(cls, v):
        if v < settings.MIN_AGE or v > settings.MAX_AGE:
            raise ValueError(f"User's age must be between {settings.MIN_AGE} and {settings.MAX_AGE} years")
        
        return v


class UserProfileUpdate(BaseModel):
    gender: Optional[Gender] = None
    major: Optional[str] = None
    classification: Optional[Classification] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[List[str]] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None

    class Config:
        from_attributes = True

    @field_validator("first_name")
    def validate_first_name(cls, v) -> str:
        return validate_name(v, settings.FIRST_NAME_MIN_LEN, settings.FIRST_NAME_MAX_LEN, "first")

    @field_validator("last_name")
    def validate_last_name(cls, v) -> str:
        return validate_name(v, settings.LAST_NAME_MIN_LEN, settings.LAST_NAME_MAX_LEN, "last")

    @field_validator("age")
    def validate_age(cls, v):
        if v < settings.MIN_AGE or v > settings.MAX_AGE:
            raise ValueError(f"User's age must be between {settings.MIN_AGE} and {settings.MAX_AGE} years (inclusive)")

        return v


class UserProfileResponse(BaseModel):
    user_id: str
    gender: Gender
    major: str
    classification: Classification
    created_at: datetime
    updated_at: datetime
    first_name: str
    last_name: str
    age: int
    profile_picture_url: Optional[List[str]] = None
    bio: str

    class Config:
        from_attributes = True

class UserProfilePicture(BaseModel):
    base64: str
