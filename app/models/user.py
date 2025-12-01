# Created by Ryan Polasky | 7/12/25
# ACM MeteorMate | All Rights Reserved

from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Boolean, DateTime, Text, Date, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from app.database import Base
from typing import Optional, Literal


class User(Base):
    __tablename__ = "users"

    id = Column(Text, primary_key=True, index=True)
    utd_id = Column(Text, unique=True, index=True)
    email = Column(Text, unique=True, index=True)
    first_name = Column(Text)
    last_name = Column(Text)
    birthdate = Column(Date)

    # behind-the-scenes stuff
    is_active = Column(Boolean, nullable=False, server_default='true', default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # compute age
    @hybrid_property
    def age(self):
        if not self.birthdate:
            return None
        today = date.today()
        return today.year - self.birthdate.year - ((today.month, today.day)
                                                   < (self.birthdate.month, self.birthdate.day))

    @age.expression
    def age(cls):
        return func.extract('year', func.age(func.current_date(),
                                             cls.birthdate)).cast(postgresql.INTEGER)


class UserRequestVerify(BaseModel):
    email: EmailStr
    uid: Optional[str] = None
    purpose: Literal["verify", "reset"] = "verify"


class UserCompleteVerify(BaseModel):
    email: EmailStr
    code: str

class UserResetPassword(BaseModel):
    email: EmailStr
    code: str
    new_password: str