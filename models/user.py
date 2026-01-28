# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

import enum
from typing import Optional, Literal

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Boolean, DateTime, Text, func, Enum
from sqlalchemy.orm import relationship

from database import ORMBase


class InactivityStage(str, enum.Enum):
    ONE_MONTH = "one_month"
    ONE_WEEK = "one_week"
    INACTIVE = "inactive"


class User(ORMBase):
    __tablename__ = "users"

    id = Column(Text, primary_key=True, index=True)
    utd_id = Column(Text, unique=True, index=True)
    email = Column(Text, unique=True, index=True)

    # behind-the-scenes stuff
    is_active = Column(Boolean, nullable=False, server_default='true', default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    inactivity_notification_stage = Column(Enum(InactivityStage), nullable=True)
    last_inactivity_notification_sent_at = Column(DateTime, nullable=True)

    survey = relationship(
        "Survey", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    profile = relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class UserRequestVerify(BaseModel):
    email: EmailStr
    uid: Optional[str] = None
    purpose: Literal["verify", "reset"] = "verify"


class UserCompleteVerify(BaseModel):
    email: EmailStr
    code: str


class UserResetPassword(BaseModel):
    email: EmailStr
    code: str
    new_password: str
