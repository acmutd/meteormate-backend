# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from typing import Optional, Literal
from datetime import date, datetime
from pydantic import BaseModel

HousingIntent = Literal["on", "off", "both"]


class UserCreate(BaseModel):
    utd_id: str
    email: str
    first_name: str
    last_name: str
    birthdate: Optional[date] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    firebase_uid: str
    utd_id: str
    email: str
    first_name: str
    last_name: str
    age: Optional[int] = None
    birthdate: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True
