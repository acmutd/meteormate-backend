# Created by Ryan Polasky | 9/20/25
# Updated by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

import base64
import binascii
from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator

from config import settings
from utils.exceptions import BadRequest, UnprocessableEntity

Gender = Literal["female", "male", "non_binary", "prefer_not_to_say", "other"]
Classification = Literal["freshman", "sophomore", "junior", "senior", "graduate"]


def validate_name(name: str, min_len: int, max_len: int, position: str) -> str:
    if not (min_len <= len(name) <= max_len):
        raise BadRequest(f"{position} name must be between {min_len} and {max_len} characters")

    if not name.isalpha():
        raise BadRequest(f"{position} name cannot contain any numbers or special characters")

    return name


class UserProfileBase(BaseModel):
    gender: Optional[Gender] = None
    major: Optional[str] = None
    classification: Optional[Classification] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[List[str]] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    match_notifications: Optional[bool] = True
    promotional_notifications: Optional[bool] = False

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

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if v is None:
            return v

        if not (settings.MIN_AGE <= v <= settings.MAX_AGE):
            raise BadRequest(f"age must be between {settings.MIN_AGE} and {settings.MAX_AGE} years")

        return v


class UserProfileCreate(UserProfileBase):
    gender: Gender
    major: str
    classification: Classification
    profile_picture_url: list[str]
    bio: str
    first_name: str
    last_name: str
    age: int


class UserProfileUpdate(UserProfileBase):
    pass


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

    ext: str
    image_bytes: bytes

    @model_validator(mode="before")
    @classmethod
    def parse_and_validate(cls, values):
        raw = values.get("base64")
        if not raw or "," not in raw:
            raise UnprocessableEntity("Image data not in base64 format")

        header, data = raw.split(",", 1)

        if not header.startswith("data:image/") or ";base64" not in header:
            raise UnprocessableEntity("Invalid image base64 header")

        ext = header[len("data:image/"):header.index(";base64")]
        if ext not in {"jpeg", "jpg", "png", "webp"}:
            raise UnprocessableEntity("Not an acceptable image type")

        try:
            image_bytes = base64.b64decode(data, validate=True)
        except (ValueError, binascii.Error):
            raise UnprocessableEntity("Image data has incorrect padding or invalid characters")

        values["ext"] = ext
        values["image_bytes"] = image_bytes

        return values


class UserUpdateNotifications(BaseModel):
    match_notifications: Optional[bool] = None
    promotional_notifications: Optional[bool] = None

    @model_validator(mode="before")
    @classmethod
    def validate_atleast_one(cls, values):
        if (
            values.get("match_notifications") is None
            and values.get("promotional_notifications") is None
        ):
            raise BadRequest("At least one notification preference must be provided")

        return values
