# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
from app.database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    target_user_id = Column(String, ForeignKey("users.id"))
    is_like = Column(Boolean)  # true for like, false for pass
    is_mutual = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())