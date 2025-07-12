# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    firebase_uid = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(Integer)
    bio = Column(Text)
    profile_picture_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
