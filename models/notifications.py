# Created by Atharva Mishra | 9/16/2026
# ACM MeteorMate | All Rights Reserved

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.sql import func

from database import ORMBase


class Notifications(ORMBase):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Text, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    seen = Column(Boolean, default=False)
