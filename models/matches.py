# Created by Ryan Polasky | 7/12/25
# Updated by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database import ORMBase

if TYPE_CHECKING:
    from models.user import User


class Match(ORMBase):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        Text, ForeignKey("users.id", ondelete="CASCADE")
    )
    target_user_id: Mapped[str] = mapped_column(
        Text, ForeignKey("users.id", ondelete="CASCADE")
    )
    is_like: Mapped[bool] = mapped_column(Boolean)  # true for like, false for pass
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    target_user: Mapped["User"] = relationship("User", foreign_keys=[target_user_id])
