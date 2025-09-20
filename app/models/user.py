# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from datetime import date
from sqlalchemy import Column, String, Boolean, DateTime, Text, Date, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from app.database import Base

HOUSING_INTENT = postgresql.ENUM(
    'on', 'off', 'both',
    name='housing_intent_enum',
    create_type=True
)


class User(Base):
    __tablename__ = "users"

    firebase_uid = Column(String, primary_key=True, index=True)

    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    birthdate = Column(Date)

    housing_intent = Column(HOUSING_INTENT, nullable=False, server_default='both')

    bio = Column(Text)
    profile_picture_url = Column(String)

    is_active = Column(Boolean, nullable=False, server_default='true', default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # compute age
    @hybrid_property
    def age(self):
        if not self.birthdate:
            return None
        today = date.today()
        return today.year - self.birthdate.year - (
                (today.month, today.day) < (self.birthdate.month, self.birthdate.day)
        )

    @age.expression
    def age(cls):
        return func.extract('year', func.age(func.current_date(), cls.birthdate)).cast(postgresql.INTEGER)
