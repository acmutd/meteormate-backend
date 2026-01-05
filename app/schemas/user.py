# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from typing import Optional, Literal
from datetime import date, datetime
from pydantic import BaseModel, field_validator

HousingIntent = Literal["on", "off", "both"]


class UserCreate(BaseModel):
    email: str
    password: str
    utd_id: str
    first_name: str
    last_name: str
    birthdate: Optional[date] = None

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
    first_name: str
    last_name: str
    age: Optional[int] = None
    birthdate: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True
