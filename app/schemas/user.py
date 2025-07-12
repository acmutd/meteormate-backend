# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    age: int
    bio: Optional[str] = None


class UserResponse(BaseModel):
    firebase_uid: str
    username: str
    first_name: str
    last_name: str
    age: int
    bio: Optional[str]
    profile_picture_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
