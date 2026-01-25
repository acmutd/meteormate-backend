# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from sqlalchemy import Column, Text, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
from ..database import ORMBase


class Match(ORMBase):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Text, ForeignKey("users.id"))
    target_user_id = Column(Text, ForeignKey("users.id"))
    is_like = Column(Boolean)  # true for like, false for pass
    created_at = Column(DateTime(timezone=True), server_default=func.now())
