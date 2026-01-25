# Created by Ryan Polasky | 9/20/25
# ACM MeteorMate | All Rights Reserved

from sqlalchemy import ARRAY, Column, DateTime, Text, ForeignKey, func, Numeric
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableList
from ..database import ORMBase

GENDER_ENUM = PGEnum(
    'female',
    'male',
    'non_binary',
    'prefer_not_to_say',
    'other',
    name='gender_enum',
    create_type=True
)

CLASSIFICATION_ENUM = PGEnum(
    'freshman',
    'sophomore',
    'junior',
    'senior',
    'graduate',
    name='classification_enum',
    create_type=True
)


class UserProfile(ORMBase):
    __tablename__ = "user_profiles"

    user_id = Column(Text, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)

    gender = Column(GENDER_ENUM)
    major = Column(Text)
    classification = Column(CLASSIFICATION_ENUM)
    bio = Column(Text)
    profile_picture_url = Column(MutableList.as_mutable(ARRAY(Text)))

    # moved from user table
    first_name = Column(Text)
    last_name = Column(Text)
    age = Column(Numeric)

    # behind-the-scenes stuff
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="profile", uselist=False)
