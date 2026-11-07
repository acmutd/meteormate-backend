# Created by Ryan Polasky | 1/5/26
# Updated by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from database import ORMBase, enum_values


class CodeType(str, Enum):
    PWD_RESET_CODE = "pwd_reset_code"
    ACC_VERIFICATION_CODE = "acc_verification_code"


class VerificationCodes(ORMBase):
    __tablename__ = "verification_codes"

    user_id: Mapped[str] = mapped_column(
        Text, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(Text)
    type: Mapped[CodeType] = mapped_column(
        SQLEnum(
            CodeType,
            name="code_type_enum",
            validate_strings=True,
            values_callable=enum_values,
        ),
        nullable=False,
    )

    # behind-the-scenes stuff
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
