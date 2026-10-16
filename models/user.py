# Created by Ryan Polasky | 7/12/25
# Updated by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Text, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import ORMBase

if TYPE_CHECKING:
    from models.survey import Survey
    from models.user_profile import UserProfile


class InactivityStage(str, enum.Enum):
    ONE_MONTH = "one_month"
    ONE_WEEK = "one_week"
    INACTIVE = "inactive"


class User(ORMBase):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(Text, primary_key=True, index=True)
    utd_id: Mapped[str] = mapped_column(Text, unique=True, index=True)
    email: Mapped[str] = mapped_column(Text, unique=True, index=True)

    # behind-the-scenes stuff
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true", default=True
    )
    pending_deletion: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false", default=False
    )
    is_banned: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false", default=False
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
    inactivity_notification_stage: Mapped[InactivityStage | None] = mapped_column(
        SQLEnum(
            InactivityStage,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
            name="inactivitystage",
        ),
        nullable=True,
    )
    last_inactivity_notification_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    survey: Mapped[Optional["Survey"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    profile: Mapped[Optional["UserProfile"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
