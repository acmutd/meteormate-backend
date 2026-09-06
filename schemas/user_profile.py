# Created by Ryan Polasky | 9/20/25
# Updated by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator

from config import settings
from utils.exceptions import BadRequest

Gender = Literal["female", "male", "non_binary", "prefer_not_to_say", "other"]
Classification = Literal["freshman", "sophomore", "junior", "senior", "graduate"]
School = Literal["AHT", "BBS", "EPPS", "ECS", "IDS", "JSOM", "NSM"]


def validate_name(name: str, min_len: int, max_len: int, position: str) -> str:
    if not (min_len <= len(name) <= max_len):
        raise BadRequest(f"{position} name must be between {min_len} and {max_len} characters")

    if not name.isalpha():
        raise BadRequest(f"{position} name cannot contain any numbers or special characters")

    return name


class UserProfileBase(BaseModel):
    gender: Optional[Gender] = None
    major: Optional[str] = None
    school: Optional[School] = None
    classification: Optional[Classification] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[List[str]] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[datetime] = None
    age: Optional[int] = None
    match_notification: Optional[bool] = True
    promotional_notification: Optional[bool] = False

    class Config:
        from_attributes = True

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v):
        if v is None:
            return v

        return validate_name(v, settings.FIRST_NAME_MIN_LEN, settings.FIRST_NAME_MAX_LEN, "first")

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v):
        if v is None:
            return v

        return validate_name(v, settings.LAST_NAME_MIN_LEN, settings.LAST_NAME_MAX_LEN, "last")

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, v):
        if v is None:
            return v

        if v > datetime.now():
            raise BadRequest("Date of birth cannot be in the future")

        return v

    @model_validator(mode="after")
    @classmethod
    def calculate_and_validate_age(cls, values):
        if values.age is not None:
            raise BadRequest("Age cannot be provided directly")

        dob = values.dob
        if dob is None:
            return values

        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if not (settings.MIN_AGE <= age <= settings.MAX_AGE):
            raise BadRequest(f"Age must be between {settings.MIN_AGE} and {settings.MAX_AGE} years")

        values.age = age

        return values


class UserProfileCreate(UserProfileBase):
    gender: Gender
    school: School
    major: str
    classification: Classification
    profile_picture_url: list[str]
    bio: str
    first_name: str
    last_name: str
    dob: datetime


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileResponse(BaseModel):
    user_id: str
    gender: Gender
    school: School
    major: str
    classification: Classification
    created_at: datetime
    updated_at: datetime
    first_name: str
    last_name: str
    age: int
    dob: datetime
    profile_picture_url: List[str]
    bio: str
    match_notification: bool
    promotional_notification: bool

    class Config:
        from_attributes = True


class UserProfileDeletePictures(BaseModel):
    profile_picture_url: List[str]

    @field_validator("profile_picture_url")
    @classmethod
    def validate_picture_count(cls, v):
        if len(v) == 0:
            raise BadRequest("At least one profile picture must be provided for deletion")

        return v


class UserUpdateNotifications(BaseModel):
    match_notification: Optional[bool] = None
    promotional_notification: Optional[bool] = None

    @model_validator(mode="before")
    @classmethod
    def validate_atleast_one(cls, values):
        if (values.get("match_notification") is None and values.get("promotional_notification") is None):
            raise BadRequest("At least one notification preference must be provided")

        return values
