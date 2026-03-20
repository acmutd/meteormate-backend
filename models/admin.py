from datetime import datetime
from sqlalchemy import DateTime, Text, func
from sqlalchemy.orm import mapped_column, Mapped
from database import ORMBase


class Banlist(ORMBase):
    __tablename__ = "banlist"

    net_id: Mapped[str] = mapped_column(Text, nullable=False, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class Admins(ORMBase):
    __tablename__ = "admins"

    net_id: Mapped[str] = mapped_column(Text, nullable=False, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
