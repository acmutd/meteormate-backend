# Created by Ryan Polasky | 1/5/26
# ACM MeteorMate | All Rights Reserved

from enum import Enum

from sqlalchemy import Column, DateTime, Text, ForeignKey, func, Integer, Enum as SQLEnum
from database import ORMBase


class CodeType(str, Enum):
    PWD_RESET_CODE = "pwd_reset_code"
    ACC_VERIFICATION_CODE = "acc_verification_code"


class VerificationCodes(ORMBase):
    __tablename__ = "verification_codes"

    user_id = Column(Text, ForeignKey("users.id", ondelete="CASCADE"), index=True)

    id = Column(Integer, primary_key=True, index=True)
    code = Column(Text)
    type = Column(
        SQLEnum(
            CodeType,
            name="code_type_enum",
            validate_strings=True,
            values_callable=lambda enum: [e.value for e in enum]
        ),
        nullable=False
    )

    # behind-the-scenes stuff
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
