# Created by Ryan Polasky | 9/20/25
# Updated by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    ARRAY,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    func,
    text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import ORMBase, enum_values

if TYPE_CHECKING:
    from models.user import User


class Gender(str, enum.Enum):
    FEMALE = "female"
    MALE = "male"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"
    OTHER = "other"


class Classification(str, enum.Enum):
    FRESHMAN = "freshman"
    SOPHOMORE = "sophomore"
    JUNIOR = "junior"
    SENIOR = "senior"
    GRADUATE = "graduate"


class School(str, enum.Enum):
    AHT = "AHT"
    BBS = "BBS"
    EPPS = "EPPS"
    ECS = "ECS"
    IDS = "IDS"
    JSOM = "JSOM"
    NSM = "NSM"


class UserProfile(ORMBase):
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(
        Text, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    gender: Mapped[Gender] = mapped_column(
        SQLEnum(Gender, name="gender_enum", values_callable=enum_values)
    )
    school: Mapped[School] = mapped_column(
        SQLEnum(School, name="school_enum", values_callable=enum_values)
    )
    classification: Mapped[Classification] = mapped_column(
        SQLEnum(
            Classification, name="classification_enum", values_callable=enum_values
        )
    )
    major: Mapped[str] = mapped_column(Text)
    bio: Mapped[str] = mapped_column(Text)
    profile_picture_url: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(ARRAY(Text)),
        default=list,
        server_default="{}",
    )

    # moved from user table
    first_name: Mapped[str] = mapped_column(Text)
    last_name: Mapped[str] = mapped_column(Text)
    age: Mapped[int] = mapped_column(Numeric)

    dob: Mapped[date] = mapped_column(Date, nullable=False)

    # notification preferences
    match_notification: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    promotional_notification: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship(back_populates="profile")
