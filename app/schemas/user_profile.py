# Created by Ryan Polasky | 9/20/25
# ACM MeteorMate | All Rights Reserved

from typing import Optional, Literal, Self
from datetime import datetime, date
from pydantic import BaseModel, field_validator
from app.schemas.validation_config import (
    FIRST_NAME_MIN_LEN,
    FIRST_NAME_MAX_LEN,
    LAST_NAME_MIN_LEN,
    LAST_NAME_MAX_LEN,
    MIN_AGE,
    MAX_AGE
)

Gender = Literal["female", "male", "non_binary", "prefer_not_to_say", "other"]
Classification = Literal["freshman", "sophomore", "junior", "senior", "graduate"]

def validate_name(name, min_len, max_len, position):
    if len(name) > FIRST_NAME_MAX_LEN or len(name) < FIRST_NAME_MIN_LEN:
            raise ValueError(f"User's {position} name must be between {min_len} and {max_len} characters (inclusive)")
    if any(not char.isalpha() for char in name):
        raise ValueError(f"User's {position} name cannot contain any numbers or special characters")
    return name


class UserProfileCreate(BaseModel):
    gender: Gender
    major: str
    classification: Classification
    bio: str
    profile_picture_url: Optional[str] = None
    first_name: str
    last_name: str
    age: int

    class Config:
        from_attributes = True
    
    @field_validator("first_name")
    def validate_first_name(cls, v) -> str:
        return validate_name(v, FIRST_NAME_MIN_LEN, FIRST_NAME_MAX_LEN, "first")

    @field_validator("last_name")
    def validate_last_name(cls, v) -> str:
        return validate_name(v, LAST_NAME_MIN_LEN, LAST_NAME_MAX_LEN, "last")
    
    @field_validator("age")
    def validate_age(cls, v):
        if v < MIN_AGE or v > MAX_AGE:
            raise ValueError(f"User's age must be between {MIN_AGE} and {MAX_AGE} years")
    



class UserProfileUpdate(BaseModel):
    gender: Optional[Gender] = None
    major: Optional[str] = None
    classification: Optional[Classification] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None

    class Config:
        from_attributes = True
    
    @field_validator("first_name")
    def validate_first_name(cls, v) -> str:
        return validate_name(v, FIRST_NAME_MIN_LEN, FIRST_NAME_MAX_LEN, "first")

    @field_validator("last_name")
    def validate_last_name(cls, v) -> str:
        return validate_name(v, LAST_NAME_MIN_LEN, LAST_NAME_MAX_LEN, "last")
    
    @field_validator("age")
    def validate_age(cls, v):
        if v < MIN_AGE or v > MAX_AGE:
            raise ValueError(f"User's age must be between {MIN_AGE} and {MAX_AGE} years (inclusive)")


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
    profile_picture_url: Optional[str] = None
    bio: str

    class Config:
        from_attributes = True
