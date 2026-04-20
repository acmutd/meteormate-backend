# Created by Atharva Mishra | 4/16/2026
# ACM MeteorMate | All Rights Reserved

from sqlalchemy import ARRAY, Column, Text, ForeignKey, func, Numeric, Enum as SQLEnum, Boolean, text, Date, DateTime
from sqlalchemy.ext.mutable import MutableList
from database import ORMBase

class UserReport(ORMBase):
    __tablename__ = "user_reports"

    id = Column(Text, primary_key=True, index=True)
    reporter_uid = Column(Text, ForeignKey("users.id"), nullable=False)
    reported_uid = Column(Text, ForeignKey("users.id"), nullable=False)
    
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    screenshots = Column(MutableList.as_mutable(ARRAY(Text)), default=list)
