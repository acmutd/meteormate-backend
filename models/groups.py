
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import ORMBase

if TYPE_CHECKING:
    from models.user import User

class Groups(ORMBase):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    max_members: Mapped[int] = mapped_column(Integer, nullable=False)

    members: Mapped[list["User"]] = relationship(back_populates="group")
