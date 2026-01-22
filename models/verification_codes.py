# Created by Ryan Polasky | 1/5/26
# ACM MeteorMate | All Rights Reserved

from enum import Enum

from sqlalchemy import Column, DateTime, Text, ForeignKey, func, Integer
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from ..database import ORMBase

CODE_TYPE_ENUM = PGEnum(
    'pwd_reset_code', 'acc_verification_code', name='code_type_enum', create_type=True
)


class CodeType(Enum):
    PWD_RESET_CODE = "pwd_reset_code"
    ACC_VERIFICATION_CODE = "acc_verification_code"


class VerificationCodes(ORMBase):
    __tablename__ = "verification_codes"

    user_id = Column(Text, ForeignKey("users.id", ondelete="CASCADE"), index=True)

    id = Column(Integer, primary_key=True, index=True)
    code = Column(Text)
    type = Column(CODE_TYPE_ENUM)

    # behind-the-scenes stuff
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
