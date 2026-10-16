# Created by Atharva Mishra | 4/16/2026
# ACM MeteorMate | All Rights Reserved

from datetime import datetime

from sqlalchemy import (
    ARRAY,
    DateTime,
    ForeignKey,
    Text,
    func,
)
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped

from database import ORMBase
from models.user import mapped_column


class UserReport(ORMBase):
    __tablename__ = "user_reports"

    id: Mapped[str] = mapped_column(Text, primary_key=True, index=True)
    reporter_uid: Mapped[str] = mapped_column(
        Text, ForeignKey("users.id"), nullable=False
    )
    reported_uid: Mapped[str] = mapped_column(
        Text, ForeignKey("users.id"), nullable=False
    )

    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    screenshots: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(ARRAY(Text)), default=list
    )
