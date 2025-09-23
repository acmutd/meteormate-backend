# Created by Ryan Polasky | 9/20/25
# ACM MeteorMate | All Rights Reserved

from sqlalchemy import Column, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.ext.hybrid import hybrid_property
from app.database import Base

GENDER_ENUM = PGEnum(
    'female',
    'male',
    'non_binary',
    'prefer_not_to_say',
    'other',
    name='gender_enum',
    create_type=True
)

CLASS_YEAR_ENUM = PGEnum(
    'freshman',
    'sophomore',
    'junior',
    'senior',
    'graduate',
    'other',
    name='class_year_enum',
    create_type=True
)

HOUSING_INTENT = postgresql.ENUM('on', 'off', 'both', name='housing_intent_enum', create_type=True)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(Text, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)

    gender = Column(GENDER_ENUM)
    major = Column(Text)
    class_year = Column(CLASS_YEAR_ENUM)
    housing_intent = Column(HOUSING_INTENT, nullable=False, server_default='both')
    llc = Column(Boolean)
    bio = Column(Text)
    profile_picture_url = Column(Text)

    # behind-the-scenes stuff
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    @hybrid_property
    def is_freshman(self):
        return self.class_year == 'freshman'

    @is_freshman.expression
    def is_freshman(cls):
        return cls.class_year == 'freshman'
